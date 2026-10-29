"""Consulta de registros del journal de systemd."""

import subprocess


VALID_PRIORITIES = {
    "emerg",
    "alert",
    "crit",
    "err",
    "warning",
    "notice",
    "info",
    "debug",
}


def journal_logs(
    lines: int = 20,
    unit: str | None = None,
    priority: str | None = None,
) -> list[str]:
    """Devuelve registros recientes del journal con filtros opcionales."""

    if not isinstance(lines, int) or isinstance(lines, bool):
        raise ValueError("El número de líneas debe ser un entero")

    if not 1 <= lines <= 1000:
        raise ValueError("El número de líneas debe estar entre 1 y 1000")

    if unit is not None:
        if (
            not isinstance(unit, str)
            or not unit
            or unit.startswith("-")
            or any(char.isspace() for char in unit)
        ):
            raise ValueError("El nombre de la unidad no es válido")

    if priority is not None:
        if not isinstance(priority, str) or priority not in VALID_PRIORITIES:
            raise ValueError("La prioridad indicada no es válida")

    command = [
        "journalctl",
        "-n",
        str(lines),
        "--no-pager",
        "-o",
        "short-iso",
    ]

    if unit is not None:
        command.extend(["--unit", unit])

    if priority is not None:
        command.extend(["--priority", priority])

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )

    return result.stdout.splitlines()
