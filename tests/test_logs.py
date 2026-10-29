"""Pruebas del módulo de consulta del journal."""

import subprocess
import unittest
from unittest.mock import patch

from linux_monitor.logs import journal_logs


class TestJournalLogs(unittest.TestCase):

    @patch("linux_monitor.logs.subprocess.run")
    def test_reads_recent_logs(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["journalctl"],
            returncode=0,
            stdout="Registro 1\nRegistro 2\n",
            stderr="",
        )

        result = journal_logs(lines=2)

        self.assertEqual(result, ["Registro 1", "Registro 2"])
        command = mock_run.call_args.args[0]
        self.assertIn("2", command)
        mock_run.assert_called_once()

    @patch("linux_monitor.logs.subprocess.run")
    def test_filters_by_unit(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["journalctl"],
            returncode=0,
            stdout="Registro de SSH\n",
            stderr="",
        )

        result = journal_logs(unit="ssh.service")

        self.assertEqual(result, ["Registro de SSH"])
        command = mock_run.call_args.args[0]
        self.assertIn("--unit", command)
        self.assertIn("ssh.service", command)

    @patch("linux_monitor.logs.subprocess.run")
    def test_filters_by_priority(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["journalctl"],
            returncode=0,
            stdout="Error de prueba\n",
            stderr="",
        )

        result = journal_logs(priority="err")

        self.assertEqual(result, ["Error de prueba"])
        command = mock_run.call_args.args[0]
        self.assertIn("--priority", command)
        self.assertIn("err", command)

    def test_rejects_invalid_line_count(self):
        for value in (0, 1001, -1, True, 2.5):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    journal_logs(lines=value)

    def test_rejects_invalid_unit(self):
        for value in ("", "-n", "ssh service"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    journal_logs(unit=value)

    def test_rejects_invalid_priority(self):
        with self.assertRaises(ValueError):
            journal_logs(priority="invalid")

    @patch("linux_monitor.logs.subprocess.run")
    def test_journal_error_propagates(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(
            1,
            ["journalctl"],
        )

        with self.assertRaises(subprocess.CalledProcessError):
            journal_logs()

    @patch("linux_monitor.logs.subprocess.run")
    def test_command_has_timeout(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["journalctl"],
            returncode=0,
            stdout="",
            stderr="",
        )

        journal_logs()

        self.assertEqual(
            mock_run.call_args.kwargs["timeout"],
            10,
        )


if __name__ == "__main__":
    unittest.main()
