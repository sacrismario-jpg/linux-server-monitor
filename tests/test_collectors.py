import unittest
from unittest.mock import patch

from src.linux_monitor.collectors import (
    cpu_usage,
    disk_metrics,
    memory_metrics,
)


class TestCPUUsage(unittest.TestCase):

    @patch("src.linux_monitor.collectors.time.sleep")
    @patch(
        "src.linux_monitor.collectors.read_cpu_times",
        side_effect=[
            [100, 0, 50, 800, 20],
            [150, 0, 70, 850, 30],
        ],
    )
    def test_cpu_usage_calculation(self, _mock_times, _mock_sleep):
        result = cpu_usage(interval=0.5)
        self.assertEqual(result, 53.85)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 100)

    def test_cpu_rejects_invalid_interval(self):
        with self.assertRaises(ValueError):
            cpu_usage(interval=0)

    @patch(
        "src.linux_monitor.collectors.read_cpu_times",
        side_effect=OSError("No se puede leer /proc/stat"),
    )
    def test_cpu_read_error(self, _mock_times):
        with self.assertRaises(OSError):
            cpu_usage(interval=0.5)

    @patch("src.linux_monitor.collectors.time.sleep")
    @patch(
        "src.linux_monitor.collectors.read_cpu_times",
        side_effect=[
            [100, 0, 50, 800, 20],
            [100, 0, 50, 800, 20],
        ],
    )
    def test_cpu_rejects_zero_delta(self, _mock_times, _mock_sleep):
        with self.assertRaises(RuntimeError):
            cpu_usage(interval=0.5)


class TestMemoryMetrics(unittest.TestCase):

    @patch(
        "src.linux_monitor.collectors.read_meminfo",
        return_value={
            "MemTotal": 1000,
            "MemAvailable": 250,
            "SwapTotal": 500,
            "SwapFree": 100,
        },
    )
    def test_memory_percentages(self, _mock_meminfo):
        result = memory_metrics()
        self.assertEqual(result["ram_used_percent"], 75.0)
        self.assertEqual(result["swap_used_percent"], 80.0)
        self.assertEqual(result["ram_available_kib"], 250)

    @patch(
        "src.linux_monitor.collectors.read_meminfo",
        return_value={
            "MemTotal": 0,
            "MemAvailable": 0,
            "SwapTotal": 0,
            "SwapFree": 0,
        },
    )
    def test_invalid_memory_data(self, _mock_meminfo):
        with self.assertRaises(RuntimeError):
            memory_metrics()

    @patch(
        "src.linux_monitor.collectors.read_meminfo",
        side_effect=OSError("Permiso denegado"),
    )
    def test_memory_read_error(self, _mock_meminfo):
        with self.assertRaises(OSError):
            memory_metrics()

    @patch(
        "src.linux_monitor.collectors.read_meminfo",
        return_value={
            "MemTotal": 1000,
            "MemAvailable": 1200,
            "SwapTotal": 500,
            "SwapFree": 100,
        },
    )
    def test_available_memory_cannot_exceed_total(self, _mock_meminfo):
        with self.assertRaises(RuntimeError):
            memory_metrics()

class TestDiskMetrics(unittest.TestCase):

    @patch(
        "src.linux_monitor.collectors.shutil.disk_usage",
        return_value=type(
            "Usage",
            (),
            {"total": 1000, "used": 700, "free": 300},
        )(),
    )
    def test_disk_percentages(self, _mock_disk_usage):
        result = disk_metrics("/")
        self.assertEqual(result["used_percent"], 70.0)
        self.assertEqual(result["free_bytes"], 300)

    @patch(
        "src.linux_monitor.collectors.shutil.disk_usage",
        side_effect=OSError("No se puede consultar el disco"),
    )
    def test_disk_read_error(self, _mock_disk_usage):
        with self.assertRaises(OSError):
            disk_metrics("/")

    @patch(
        "src.linux_monitor.collectors.shutil.disk_usage",
        return_value=type(
            "Usage",
            (),
            {"total": 0, "used": 0, "free": 0},
        )(),
    )
    def test_disk_rejects_zero_total(self, _mock_disk_usage):
        with self.assertRaises(RuntimeError):
            disk_metrics("/")
    @patch(
        "src.linux_monitor.collectors.shutil.disk_usage",
        return_value=type(
            "Usage",
            (),
            {"total": 1000, "used": 1200, "free": 0},
        )(),
    )
    def test_disk_rejects_inconsistent_values(self, _mock_disk_usage):
        with self.assertRaises(RuntimeError):
            disk_metrics("/")

if __name__ == "__main__":
    unittest.main()
