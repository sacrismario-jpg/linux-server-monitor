"""Pruebas del recolector de servicios systemd."""

import subprocess
import unittest
from unittest.mock import patch

from linux_monitor.services import failed_services


class TestFailedServices(unittest.TestCase):

    @patch("linux_monitor.services.subprocess.run")
    def test_no_failed_services(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["systemctl"],
            returncode=0,
            stdout="",
            stderr="",
        )

        self.assertEqual(failed_services(), [])

    @patch("linux_monitor.services.subprocess.run")
    def test_failed_service_detected(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["systemctl"],
            returncode=0,
            stdout=(
                "nginx.service loaded failed failed "
                "A high performance web server\n"
            ),
            stderr="",
        )

        result = failed_services()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["unit"], "nginx.service")
        self.assertEqual(result[0]["active"], "failed")
        self.assertEqual(
            result[0]["description"],
            "A high performance web server",
        )

    @patch("linux_monitor.services.subprocess.run")
    def test_systemctl_error_propagates(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(
            1,
            ["systemctl"],
        )

        with self.assertRaises(subprocess.CalledProcessError):
            failed_services()


if __name__ == "__main__":
    unittest.main()
