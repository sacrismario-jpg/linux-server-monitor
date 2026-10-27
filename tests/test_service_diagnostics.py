"""Pruebas de integración del diagnóstico de servicios."""

import unittest
from unittest.mock import patch

from linux_monitor.diagnostics import Status, collect_and_diagnose


class TestServiceDiagnostics(unittest.TestCase):

    def configure_metrics(self, mock_cpu, mock_memory, mock_disk):
        mock_cpu.return_value = 10.0
        mock_memory.return_value = {
            "ram_used_percent": 40.0,
            "swap_used_percent": 0.0,
        }
        mock_disk.return_value = {"used_percent": 20.0}

    @patch("linux_monitor.services.failed_services")
    @patch("linux_monitor.collectors.disk_metrics")
    @patch("linux_monitor.collectors.memory_metrics")
    @patch("linux_monitor.collectors.cpu_usage")
    def test_failed_service_changes_global_status_to_warning(
        self, mock_cpu, mock_memory, mock_disk, mock_services
    ):
        self.configure_metrics(mock_cpu, mock_memory, mock_disk)
        mock_services.return_value = [
            {
                "unit": "nginx.service",
                "load": "loaded",
                "active": "failed",
                "sub": "failed",
                "description": "Web server",
            }
        ]

        report = collect_and_diagnose()

        self.assertEqual(report["status"], Status.WARNING.value)
        self.assertEqual(len(report["services"]["failed"]), 1)

    @patch("linux_monitor.services.failed_services")
    @patch("linux_monitor.collectors.disk_metrics")
    @patch("linux_monitor.collectors.memory_metrics")
    @patch("linux_monitor.collectors.cpu_usage")
    def test_service_check_error_changes_ok_to_unknown(
        self, mock_cpu, mock_memory, mock_disk, mock_services
    ):
        self.configure_metrics(mock_cpu, mock_memory, mock_disk)
        mock_services.side_effect = OSError("systemd unavailable")

        report = collect_and_diagnose()

        self.assertEqual(report["status"], Status.UNKNOWN.value)
        self.assertEqual(report["services"]["status"], "UNKNOWN")

    @patch("linux_monitor.services.failed_services")
    @patch("linux_monitor.collectors.disk_metrics")
    @patch("linux_monitor.collectors.memory_metrics")
    @patch("linux_monitor.collectors.cpu_usage")
    def test_service_check_error_preserves_critical_status(
        self, mock_cpu, mock_memory, mock_disk, mock_services
    ):
        self.configure_metrics(mock_cpu, mock_memory, mock_disk)
        mock_cpu.return_value = 99.0
        mock_services.side_effect = OSError("systemd unavailable")

        report = collect_and_diagnose()

        self.assertEqual(report["status"], Status.CRITICAL.value)
        self.assertEqual(report["services"]["status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
