"""Diagnóstico de métricas del sistema Linux."""

from enum import Enum
from math import isfinite


class Status(str, Enum):
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


DEFAULT_THRESHOLDS = {
    "cpu": (80.0, 95.0),
    "ram": (80.0, 95.0),
    "swap": (50.0, 80.0),
    "disk": (80.0, 90.0),
}


def evaluate_metric(
    name: str,
    value: float | int | None,
    warning: float,
    critical: float,
) -> dict[str, str | float | None]:
    """Clasifica una métrica según sus umbrales."""

    if (
        not isinstance(warning, (int, float))
        or isinstance(warning, bool)
        or not isinstance(critical, (int, float))
        or isinstance(critical, bool)
        or not isfinite(warning)
        or not isfinite(critical)
        or warning < 0
        or critical > 100
        or warning >= critical
    ):
        raise ValueError("Los umbrales deben cumplir 0 <= warning < critical <= 100")

    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not isfinite(value)
        or value < 0
        or value > 100
    ):
        return {
            "metric": name,
            "value": None,
            "status": Status.UNKNOWN.value,
            "message": "Métrica ausente o inválida",
        }

    if value >= critical:
        status = Status.CRITICAL
        message = "Se ha alcanzado el umbral crítico"
    elif value >= warning:
        status = Status.WARNING
        message = "Se ha alcanzado el umbral de advertencia"
    else:
        status = Status.OK
        message = "Métrica dentro de los límites normales"

    return {
        "metric": name,
        "value": float(value),
        "status": status.value,
        "message": message,
    }
def diagnose_system(
    metrics: dict[str, float | int | None],
    thresholds: dict[str, tuple[float, float]] | None = None,
) -> dict:
    """Evalúa las métricas del sistema y calcula un estado general."""

    configured_thresholds = (
        DEFAULT_THRESHOLDS if thresholds is None else thresholds
    )

    results = []

    for name in DEFAULT_THRESHOLDS:
        value = metrics.get(name)

        if name not in metrics:
            value = None

        warning, critical = configured_thresholds.get(
            name, DEFAULT_THRESHOLDS[name]
        )

        result = evaluate_metric(name, value, warning, critical)
        results.append(result)

    statuses = [result["status"] for result in results]

    if Status.CRITICAL.value in statuses:
        overall_status = Status.CRITICAL.value
    elif Status.UNKNOWN.value in statuses:
        overall_status = Status.UNKNOWN.value
    elif Status.WARNING.value in statuses:
        overall_status = Status.WARNING.value
    else:
        overall_status = Status.OK.value

    return {
        "status": overall_status,
        "metrics": results,
        "summary": {
            "total": len(results),
            "ok": statuses.count(Status.OK.value),
            "warning": statuses.count(Status.WARNING.value),
            "critical": statuses.count(Status.CRITICAL.value),
            "unknown": statuses.count(Status.UNKNOWN.value),
        },
    }
def collect_and_diagnose() -> dict:
    """Recopila métricas reales y evalúa el estado del sistema."""
    from .collectors import (
        cpu_usage,
        memory_metrics,
        disk_metrics,
    )
    from .services import failed_services 

    metrics = {}

    try:
        metrics["cpu"] = cpu_usage()
    except (OSError, RuntimeError, ValueError):
        metrics["cpu"] = None

    try:
        memory = memory_metrics()
        metrics["ram"] = memory["ram_used_percent"]
        metrics["swap"] = memory["swap_used_percent"]
    except (OSError, RuntimeError, ValueError, KeyError):
        metrics["ram"] = None
        metrics["swap"] = None

    try:
        disk = disk_metrics("/")
        metrics["disk"] = disk["used_percent"]
    except (OSError, RuntimeError, ValueError, KeyError):
        metrics["disk"] = None

    report = diagnose_system(metrics)

    try:
        services = failed_services()
        report["services"] = {
            "status": "WARNING" if services else "OK",
            "failed": services,
            "message": (
                f"Se han detectado {len(services)} servicios fallidos"
                if services
                else "No hay servicios fallidos"
            ),
        }

        if services and report["status"] == Status.OK.value:
            report["status"] = Status.WARNING.value

    except (OSError, RuntimeError, ValueError) as exc:
        report["services"] = {
            "status": "UNKNOWN",
            "failed": None,
            "message": f"No se pudo consultar systemd: {exc}",
        }

        if report["status"] not in (
            Status.CRITICAL.value,
            Status.WARNING.value,
        ):
            report["status"] = Status.UNKNOWN.value

    return report
