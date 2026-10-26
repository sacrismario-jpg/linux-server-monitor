"""Pruebas de los códigos de salida de Linux Server Monitor."""

import json
import unittest
from unittest.mock import patch

from linux_monitor.__main__ import main


class TestMainExitCodes(unittest.TestCase):
    """Comprueba los códigos de salida de la aplicación."""

    def run_with_status(self, status):
        """Ejecuta main simulando un estado de diagnóstico."""
        report = {
            "status": status,
            "metrics": [],
            "summary": {
                "total": 4,
                "ok": 0,
                "warning": 0,
                "critical": 0,
                "unknown": 0,
            },
        }

        with (
            patch("linux_monitor.__main__.collect_and_diagnose",
                  return_value=report),
            patch("sys.argv", ["linux_monitor", "--json"]),
            patch("builtins.print") as mock_print,
        ):
            exit_code = main()

        output = mock_print.call_args.args[0]
        parsed_report = json.loads(output)

        self.assertEqual(parsed_report["status"], status)

        return exit_code

    def test_ok_returns_zero(self):
        self.assertEqual(self.run_with_status("OK"), 0)

    def test_warning_returns_one(self):
        self.assertEqual(self.run_with_status("WARNING"), 1)

    def test_critical_returns_two(self):
        self.assertEqual(self.run_with_status("CRITICAL"), 2)

    def test_unknown_returns_three(self):
        self.assertEqual(self.run_with_status("UNKNOWN"), 3)

    def test_internal_error_returns_four(self):
        with (
            patch("linux_monitor.__main__.collect_and_diagnose",
                  side_effect=RuntimeError("Error simulado")),
            patch("sys.argv", ["linux_monitor", "--json"]),
            patch("sys.stderr") as mock_stderr,
        ):
            exit_code = main()

        self.assertEqual(exit_code, 4)
        mock_stderr.write.assert_called()


if __name__ == "__main__":
    unittest.main()
