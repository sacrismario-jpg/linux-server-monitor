"""Punto de entrada de Linux Server Monitor."""

import json
import sys

from linux_monitor.diagnostics import collect_and_diagnose
EXIT_CODES = {
    "OK": 0,
    "WARNING": 1,
    "CRITICAL": 2,
    "UNKNOWN": 3,
}

def main() -> int:
    """Ejecuta el diagnóstico y muestra el informe."""

    try:
        report = collect_and_diagnose()
    except Exception as exc:
        print(f"Error al ejecutar el diagnóstico: {exc}", file=sys.stderr)
        return 4

    if "--json" in sys.argv[1:]:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return EXIT_CODES[report["status"]]

    print("=" * 50)
    print("         LINUX SERVER MONITOR")
    print("=" * 50)
    print(f"\nEstado general: {report['status']}")

    system = report.get("system")

    if system:
        print("\nSISTEMA")
        print(f"  Hostname:     {system['hostname']}")
        print(f"  Kernel:       {system['kernel']}")
        print(f"  Arquitectura: {system['architecture']}")

        uptime = system["uptime_seconds"]
        days, remainder = divmod(int(uptime), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        print(
            f"  Tiempo activo: {days}d "
            f"{hours}h {minutes}m {seconds}s"
        )

    print("\nMÉTRICAS")

    for metric in report["metrics"]:
        value = metric["value"]
        value_text = f"{value:.2f} %" if value is not None else "N/D"

        print(
            f"  {metric['metric'].upper():<8} "
            f"{value_text:<12} "
            f"{metric['status']:<8} "
            f"- {metric['message']}"
        )
    services = report.get("services")

    if services:
        print("\nSERVICIOS")
        print(f"  Estado: {services['status']}")
        print(f"  {services['message']}")

        if services["failed"]:
            for service in services["failed"]:
                print(
                    f"  - {service['unit']}: "
                    f"{service['active']} ({service['description']})"
                )
    logs = report.get("logs")

    if logs:
        print("\nLOGS DEL SISTEMA")
        print(f"  Estado: {logs['status']}")
        print(f"  {logs['message']}")

        if logs["entries"]:
            for entry in logs["entries"]:
                print(f"  - {entry}")

    summary = report["summary"]

    print("\nRESUMEN")
    print(f"  Total de métricas: {summary['total']}")
    print(f"  OK:                {summary['ok']}")
    print(f"  WARNING:           {summary['warning']}")
    print(f"  CRITICAL:          {summary['critical']}")
    print(f"  UNKNOWN:           {summary['unknown']}")

    print("=" * 50)

    return EXIT_CODES[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
