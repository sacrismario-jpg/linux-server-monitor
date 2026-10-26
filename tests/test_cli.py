import json
import subprocess
import sys
import unittest


class TestCommandLineInterface(unittest.TestCase):

    def run_monitor(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "linux_monitor", *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_json_output_is_valid(self):
        result = self.run_monitor("--json")

        self.assertIn(result.returncode, (0, 1, 2, 3))

        report = json.loads(result.stdout)

        self.assertIn(
            report["status"],
            ("OK", "WARNING", "CRITICAL", "UNKNOWN"),
        )
        self.assertEqual(len(report["metrics"]), 4)
        self.assertEqual(report["summary"]["total"], 4)

    def test_json_contains_expected_metrics(self):
        result = self.run_monitor("--json")
        report = json.loads(result.stdout)

        metric_names = {
            metric["metric"] for metric in report["metrics"]
        }

        self.assertEqual(
            metric_names,
            {"cpu", "ram", "swap", "disk"},
        )


if __name__ == "__main__":
    unittest.main()
