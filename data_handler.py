# data_handler.py

import random
import time
import os
import psutil
import pandas as pd
from tkinter import filedialog, messagebox


# --- MOCK HARDWARE/ZIGBEE SERIAL CLASS ---
class ZigBeeDataSimulator:
    """
    Simulates receiving data from the Transmitter Pi via ZigBee serial.
    In a real application, this would use a library like 'pyserial'.
    """

    def __init__(self):
        self._is_system_on = False

    def toggle_system(self, state):
        """Toggle the simulated system status."""
        self._is_system_on = state

    def get_latest_motion_data(self):
        """
        Simulates reading the latest motion data packet (e.g., via serial).
        Returns: Tuple (timestamp, motion_detected, signal_quality)
        """
        if not self._is_system_on:
            return (time.time(), 0, 0)  # System off, no motion, no signal

        # Simulate a motion detection every 5-15 seconds
        motion_detected = 1 if random.random() < 0.1 else 0

        # Simulate ZigBee signal quality (0-100)
        signal_quality = random.randint(70, 100)

        return (time.time(), motion_detected, signal_quality)


# --- SYSTEM METRICS AND DATA LOGGING ---
class SystemMetrics:
    """
    Handles fetching control station system metrics and logging data.
    """

    def __init__(self, metadata):
        self.metadata = metadata

    def get_control_station_metrics(self):
        """
        Gathers real-time CPU, RAM, Disk, and Network usage using psutil.
        """
        # CPU
        cpu_percent = psutil.cpu_percent(interval=None)  # Non-blocking

        # RAM
        ram = psutil.virtual_memory()
        ram_percent = ram.percent

        # Disk
        disk = psutil.disk_usage("/")
        disk_percent = disk.percent

        # Network Speed (Placeholder for simplicity, psutil provides counters)
        net_speed = f"{random.randint(10, 500)} KB/s"

        return {
            "CPU Usage": f"{cpu_percent:.1f}%",
            "RAM Usage": f"{ram_percent:.1f}%",
            "Disk Usage": f"{disk_percent:.1f}%",
            "Network Speed": net_speed,
            "System Time": time.strftime("%H:%M:%S"),
        }

    def save_measurements(self, data_log):
        """
        Saves the logged sensor readings and system metrics to an Excel file.
        """
        if not data_log:
            messagebox.showinfo("Save Data", "No measurements recorded yet to save.")
            return

        # Prompt user to select a directory
        save_dir = filedialog.askdirectory(title="Select Folder to Save Measurements")

        if save_dir:
            try:
                # Create a DataFrame from the log
                df = pd.DataFrame(data_log)

                # Format filename with timestamp
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"MovementLog_{timestamp}.xlsx"
                full_path = os.path.join(save_dir, filename)

                # Save to Excel
                df.to_excel(full_path, index=False)

                messagebox.showinfo(
                    "Save Success", f"Measurements saved successfully to:\n{full_path}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Save Error", f"An error occurred while saving:\n{e}"
                )
