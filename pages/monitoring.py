import tkinter as tk
from .base_page import BasePage

# import project metadata
from metadata import PROJECT_METADATA


class SimpleProgressBar(tk.Canvas):
    def __init__(
        self, parent, maximum=100, bg="#333333", fill_color="#007acc", **kwargs
    ):
        super().__init__(parent, bg=bg, height=20, highlightthickness=0, **kwargs)
        self.maximum = maximum
        self.fill_color = fill_color
        self.value = 0
        self.rect = self.create_rectangle(0, 0, 0, 20, fill=fill_color, width=0)
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        self._draw()

    def _draw(self):
        w = self.winfo_width()
        h = self.winfo_height()
        pct = max(0, min(1, self.value / self.maximum)) if self.maximum > 0 else 0
        self.coords(self.rect, 0, 0, w * pct, h)

    def __setitem__(self, key, value):
        if key == "value":
            self.value = value
            self._draw()


# -----------------------------
# Monitoring Page
# -----------------------------
class MonitoringPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        for i in range(2):
            self.columnconfigure(i, weight=1)
        for i in range(3):
            self.rowconfigure(i, weight=1)

        # Device status
        dev_frame = tk.LabelFrame(
            self,
            text="Device Status",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 10, "bold"),
        )
        dev_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.lbl_tx_status = tk.Label(
            dev_frame,
            text="Transmitter: Unknown",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8),
        )
        self.lbl_tx_status.pack(anchor="w", padx=10, pady=2)

        self.lbl_rx_status = tk.Label(
            dev_frame,
            text="Control Station: Connected",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8),
        )
        self.lbl_rx_status.pack(anchor="w", padx=10, pady=2)

        # Performance cards
        perf_frame = tk.LabelFrame(
            self,
            text="Performance Logs",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8, "bold"),
        )
        perf_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.cpu_bar = SimpleProgressBar(perf_frame, maximum=100)
        self.cpu_bar.pack(fill="x", padx=10, pady=2)
        self.cpu_text = tk.Label(
            perf_frame,
            text="CPU: -- %",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8),
        )
        self.cpu_text.pack(anchor="w", padx=10, pady=2)

        self.ram_bar = SimpleProgressBar(perf_frame, maximum=100)
        self.ram_bar.pack(fill="x", padx=10, pady=2)
        self.ram_text = tk.Label(
            perf_frame,
            text="RAM: -- %",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8),
        )
        self.ram_text.pack(anchor="w", padx=10, pady=2)

        self.disk_bar = SimpleProgressBar(perf_frame, maximum=100)
        self.disk_bar.pack(fill="x", padx=10, pady=2)
        self.disk_text = tk.Label(
            perf_frame,
            text="Disk: -- %",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8),
        )
        self.disk_text.pack(anchor="w", padx=10, pady=2)

        net_frame = tk.LabelFrame(
            self,
            text="Network",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8, "bold"),
        )
        net_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.net_up_label = tk.Label(
            net_frame,
            text="Up: -- kB/s",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8),
        )
        self.net_up_label.pack(anchor="w", padx=10, pady=1)

        self.net_down_label = tk.Label(
            net_frame,
            text="Down: -- kB/s",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8),
        )
        self.net_down_label.pack(anchor="w", padx=10, pady=1)

        self.software_version_label = tk.Label(
            net_frame,
            text=f"Software version: {PROJECT_METADATA.get('Version')}",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8),
        )
        self.software_version_label.pack(anchor="w", padx=10, pady=3)

    def update_data(self, metrics, motion_series, logs):
        cpu = metrics["cpu"]
        ram = metrics["ram"]
        disk = metrics["disk"]

        self.cpu_bar["value"] = cpu
        self.ram_bar["value"] = ram
        self.disk_bar["value"] = disk

        self.cpu_text.config(text=f"CPU: {cpu:.1f} %")
        self.ram_text.config(text=f"RAM: {ram:.1f} %")
        self.disk_text.config(text=f"Disk: {disk:.1f} %")

        self.net_up_label.config(text=f"Up: {metrics['net_up']:.1f} kB/s")
        self.net_down_label.config(text=f"Down: {metrics['net_down']:.1f} kB/s")

        if self.controller.system_on and motion_series and any(motion_series):
            tx_status = "Transmitter: Sending data"
        elif self.controller.system_on:
            tx_status = "Transmitter: Connected"
        else:
            tx_status = "Transmitter: Off"

        self.lbl_tx_status.config(text=tx_status)
        self.lbl_rx_status.config(
            text="Control Station: Receiving data"
            if self.controller.system_on
            else "Control Station: Idle"
        )
