import unittest

from src.linux_monitor.diagnostics import (
    DEFAULT_THRESHOLDS,
    Status,
    evaluate_metric,
    diagnose_system,
)


class TestEvaluateMetric(unittest.TestCase):

    def test_ok(self):
        result = evaluate_metric("cpu", 25, 80, 95)
        self.assertEqual(result["status"], Status.OK.value)

    def test_warning_at_threshold(self):
        result = evaluate_metric("cpu", 80, 80, 95)
        self.assertEqual(result["status"], Status.WARNING.value)

    def test_critical_at_threshold(self):
        result = evaluate_metric("cpu", 95, 80, 95)
        self.assertEqual(result["status"], Status.CRITICAL.value)

    def test_unknown_when_value_is_missing(self):
        result = evaluate_metric("cpu", None, 80, 95)
        self.assertEqual(result["status"], Status.UNKNOWN.value)

    def test_unknown_when_value_is_out_of_range(self):
        result = evaluate_metric("cpu", 101, 80, 95)
        self.assertEqual(result["status"], Status.UNKNOWN.value)

    def test_unknown_when_value_is_negative(self):
        result = evaluate_metric("cpu", -1, 80, 95)
        self.assertEqual(result["status"], Status.UNKNOWN.value)

    def test_invalid_thresholds_are_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_metric("cpu", 50, 95, 80)

    def test_default_thresholds_exist(self):
        self.assertEqual(DEFAULT_THRESHOLDS["cpu"], (80.0, 95.0))
        self.assertEqual(DEFAULT_THRESHOLDS["ram"], (80.0, 95.0))
        self.assertEqual(DEFAULT_THRESHOLDS["swap"], (50.0, 80.0))
        self.assertEqual(DEFAULT_THRESHOLDS["disk"], (80.0, 90.0))

    def test_global_diagnosis_ok(self):
        result = diagnose_system({
            "cpu": 25,
            "ram": 60,
            "swap": 10,
            "disk": 40,
        })
        self.assertEqual(result["status"], Status.OK.value)
        self.assertEqual(result["summary"]["ok"], 4)

    def test_global_diagnosis_critical(self):
        result = diagnose_system({
            "cpu": 97,
            "ram": 60,
            "swap": 10,
            "disk": 40,
        })
        self.assertEqual(result["status"], Status.CRITICAL.value)

    def test_global_diagnosis_warning(self):
        result = diagnose_system({
            "cpu": 85,
            "ram": 60,
            "swap": 10,
            "disk": 40,
        })
        self.assertEqual(result["status"], Status.WARNING.value)

    def test_global_diagnosis_missing_metric(self):
        result = diagnose_system({
            "cpu": 25,
            "ram": 60,
            "swap": 10,
        })
        self.assertEqual(result["status"], Status.UNKNOWN.value)
        self.assertEqual(result["summary"]["unknown"], 1)

    def test_critical_precedes_unknown(self):
        result = diagnose_system({
            "cpu": 97,
            "ram": 60,
            "swap": 10,
        })
        self.assertEqual(result["status"], Status.CRITICAL.value)
        self.assertEqual(result["summary"]["unknown"], 1)

if __name__ == "__main__":
    unittest.main()
