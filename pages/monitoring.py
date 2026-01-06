from tkinter import ttk
from .base_page import BasePage

# import project metadata
from metadata import PROJECT_METADATA


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
        dev_frame = ttk.Labelframe(self, text="Device Status", style="Card.TLabelframe")
        dev_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.lbl_tx_status = ttk.Label(
            dev_frame, text="Transmitter: Unknown", style="Main.TLabel"
        )
        self.lbl_tx_status.pack(anchor="w", padx=10, pady=2)

        self.lbl_rx_status = ttk.Label(
            dev_frame, text="Control Station: Connected", style="Main.TLabel"
        )
        self.lbl_rx_status.pack(anchor="w", padx=10, pady=2)

        # Performance cards
        perf_frame = ttk.Labelframe(
            self, text="Performance Metrics", style="Card.TLabelframe"
        )
        perf_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.cpu_bar = ttk.Progressbar(perf_frame, maximum=100)
        self.cpu_bar.pack(fill="x", padx=10, pady=2)
        self.cpu_text = ttk.Label(perf_frame, text="CPU: -- %", style="Main.TLabel")
        self.cpu_text.pack(anchor="w", padx=10, pady=2)

        self.ram_bar = ttk.Progressbar(perf_frame, maximum=100)
        self.ram_bar.pack(fill="x", padx=10, pady=2)
        self.ram_text = ttk.Label(perf_frame, text="RAM: -- %", style="Main.TLabel")
        self.ram_text.pack(anchor="w", padx=10, pady=2)

        self.disk_bar = ttk.Progressbar(perf_frame, maximum=100)
        self.disk_bar.pack(fill="x", padx=10, pady=2)
        self.disk_text = ttk.Label(perf_frame, text="Disk: -- %", style="Main.TLabel")
        self.disk_text.pack(anchor="w", padx=10, pady=2)

        net_frame = ttk.Labelframe(self, text="Network", style="Card.TLabelframe")
        net_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.net_up_label = ttk.Label(
            net_frame, text="Up: -- kB/s", style="Main.TLabel"
        )
        self.net_up_label.pack(anchor="w", padx=10, pady=2)

        self.net_down_label = ttk.Label(
            net_frame, text="Down: -- kB/s", style="Main.TLabel"
        )
        self.net_down_label.pack(anchor="w", padx=10, pady=2)

        self.software_version_label = ttk.Label(
            net_frame,
            text=f"Software version: {PROJECT_METADATA.get('Version')}",
            style="Main.TLabel",
        )
        self.software_version_label.pack(anchor="w", padx=10, pady=6)

    def update_data(self, metrics, motion_series):
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

        # Simple transmitter status heuristic: if motion buffer changes, assume sending
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
