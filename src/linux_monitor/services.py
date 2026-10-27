"""Consulta el estado de los servicios gestionados por systemd."""

import subprocess


def failed_services() -> list[dict[str, str]]:
    """Devuelve las unidades fallidas de systemd."""
    result = subprocess.run(
        [
            "systemctl",
            "list-units",
            "--failed",
            "--no-legend",
            "--no-pager",
            "--plain",
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )

    services = []

    for line in result.stdout.splitlines():
        fields = line.split(None, 4)

        if len(fields) >= 4:
            services.append(
                {
                    "unit": fields[0],
                    "load": fields[1],
                    "active": fields[2],
                    "sub": fields[3],
                    "description": fields[4] if len(fields) == 5 else "",
                }
            )

    return services
