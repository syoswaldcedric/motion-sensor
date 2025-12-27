import psutil
import random
import time


class SystemMonitor:
    def __init__(self):
        self.data_history = {
            "Timestamp": [],
            "CPU": [],
            "RAM": [],
            "DISK": [],
            "Motion": [],
        }

    def get_system_metrics(self):
        """
        Get the current system usage metrics.
        Returns:
            dict: {
                "CPU": "used;total;unit",
                "RAM": "used;total;unit",
                "DISK": "used;total;unit",
                "Motion": "value"
            }
        """
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=None)  # Non-blocking

        # RAM usage
        ram = psutil.virtual_memory()

        # Disk usage
        disk = psutil.disk_usage("/")

        # Simulated Motion Sensor (Low/High or 0-10)
        # Random value between 0 and 10 to simulate intensity or frequency
        motion_value = random.randint(0, 10)

        metrics = {
            "RAM": f"{round(ram.used / (1024**3), 2)};{round(ram.total / (1024**3), 2)};GB",
            "DISK": f"{round(disk.used / (1024**3), 2)};{round(disk.total / (1024**3), 2)};GB",
            "CPU": f"{cpu_percent};100;%",
            "Motion": f"{motion_value};10;Level",
        }

        self._update_history(metrics)
        return metrics

    def _update_history(self, metrics):
        timestamp = time.strftime("%d-%m-%Y %H:%M:%S")
        self.data_history["Timestamp"].append(timestamp)

        for key, value in metrics.items():
            val = value.split(";")[0]
            if key not in self.data_history:
                self.data_history[key] = []
            self.data_history[key].append(val)

    def get_history(self):
        return self.data_history
