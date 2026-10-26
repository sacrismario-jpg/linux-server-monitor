
"""Recopilación de métricas básicas de Linux."""

import os
import shutil
import time
from pathlib import Path


def read_cpu_times() -> list[int]:
    """Lee los contadores acumulados de CPU desde /proc/stat."""
    with open("/proc/stat", encoding="utf-8") as file:
        for line in file:
            if line.startswith("cpu "):
                return [int(value) for value in line.split()[1:]]
    raise RuntimeError("No se encontraron contadores de CPU")


def cpu_usage(interval: float = 0.5) -> float:
    """Calcula el porcentaje de uso global de CPU en un intervalo."""
    if interval <= 0:
        raise ValueError("El intervalo debe ser mayor que cero")

    first = read_cpu_times()
    time.sleep(interval)
    second = read_cpu_times()

    total_first = sum(first[:8])
    total_second = sum(second[:8])
    idle_first = first[3] + (first[4] if len(first) > 4 else 0)
    idle_second = second[3] + (second[4] if len(second) > 4 else 0)

    total_delta = total_second - total_first
    idle_delta = idle_second - idle_first

    if total_delta <= 0:
        raise RuntimeError("No se pudo calcular la utilización de CPU")

    usage = 100 * (total_delta - idle_delta) / total_delta
    return round(max(0.0, min(100.0, usage)), 2)


def read_meminfo() -> dict[str, int]:
    """Devuelve los valores de /proc/meminfo en KiB."""
    result: dict[str, int] = {}

    with open("/proc/meminfo", encoding="utf-8") as file:
        for line in file:
            key, value = line.split(":", 1)
            fields = value.split()
            if fields:
                result[key] = int(fields[0])

    return result


def memory_metrics() -> dict[str, float | int]:
    """Calcula uso y disponibilidad de RAM y swap."""
    info = read_meminfo()

    total = info.get("MemTotal", 0)
    available = info.get("MemAvailable", 0)
    swap_total = info.get("SwapTotal", 0)
    swap_free = info.get("SwapFree", 0)

    if total <= 0 or available < 0 or available > total:
        raise RuntimeError("Datos de memoria no válidos")

    if swap_total < 0 or swap_free < 0 or swap_free > swap_total:
        raise RuntimeError("Datos de swap no válidos")

    used = total - available
    swap_used = swap_total - swap_free

    return {
        "ram_total_kib": total,
        "ram_available_kib": available,
        "ram_used_percent": round(100 * used / total, 2),
        "swap_total_kib": swap_total,
        "swap_free_kib": swap_free,
        "swap_used_percent": (
            round(100 * swap_used / swap_total, 2)
            if swap_total else 0.0
        ),
    }


def disk_metrics(path: str = "/") -> dict[str, int | float | str]:
    """Obtiene y valida el uso de almacenamiento del sistema de archivos."""
    usage = shutil.disk_usage(path)

    if usage.total <= 0:
        raise RuntimeError(f"Tamaño de disco no válido para {path}")

    if usage.used < 0 or usage.free < 0:
        raise RuntimeError(f"Valores negativos de disco para {path}")

    if usage.used > usage.total or usage.free > usage.total:
        raise RuntimeError(f"Valores de disco incoherentes para {path}")


    return {
        "path": str(Path(path)),
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "free_bytes": usage.free,
        "used_percent": round(100 * usage.used / usage.total, 2),
    }


def system_metrics() -> dict[str, str | float]:
    """Obtiene información básica del sistema."""
    try:
        uptime_seconds = float(Path("/proc/uptime").read_text().split()[0])
    except (OSError, ValueError, IndexError) as exc:
        raise RuntimeError("No se pudo leer el tiempo de actividad") from exc

    return {
        "hostname": os.uname().nodename,
        "kernel": os.uname().release,
        "architecture": os.uname().machine,
        "uptime_seconds": uptime_seconds,
    }
