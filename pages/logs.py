import tkinter as tk
from .base_page import BasePage

# import project metadata
from metadata import PROJECT_METADATA


# -----------------------------
# Logs Page
# -----------------------------
class LogsPage(BasePage):
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
        logs_frame = tk.LabelFrame(
            self,
            text="Performance Logs",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8, "bold"),
        )
        logs_frame.grid(row=1, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.logs_text = tk.Label(
            logs_frame,
            text="CPU: -- %",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8),
        )
        self.logs_text.pack(anchor="w", padx=10, pady=2)

    def update_data(self, metrics, motion_series, logs):
        # logs = metrics.get("logs", "Logs not sent")
        print(logs)
        logs = metrics.get("logs", "Logs not sent")

        self.logs_text.config(text=f"Logs: {logs}")

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
