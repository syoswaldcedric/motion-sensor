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
            font=("Segoe UI", 9, "bold"),
        )
        dev_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

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
        self.logs_frame = tk.LabelFrame(
            self,
            text="Performance Logs",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8, "bold"),
        )
        self.logs_frame.grid(row=1, columnspan=2, sticky="nsew", padx=10, pady=5)

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(
            self.logs_frame, bg="#252526", height=150, highlightthickness=0
        )
        self.scrollbar = tk.Scrollbar(
            self.logs_frame, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg="#252526")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.logs_text = tk.Label(
            self.scrollable_frame,
            text="Logs: No logs yet",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8),
        )
        self.logs_text.pack(anchor="w", padx=10, pady=2)

    def update_data(self, metrics, motion_series, logs):
        pass
        # Let's clear the frame first to be safe and clean.
        # logs = metrics.get("logs", "Logs not sent")

        # print(f'logs: {logs}')
        # if len(logs) > 0:
        #     for widget in self.scrollable_frame.winfo_children():
        #         widget.destroy()

        #     for log in logs:
        #         label = tk.Label(
        #             self.scrollable_frame,
        #             text=f"{log}",
        #             bg="#252526",
        #             fg="#ffffff",
        #             font=("Segoe UI", 8),
        #         )
        #         label.pack(anchor="w", padx=10, pady=1)

        # # if self.controller.system_on and motion_series and any(motion_series):
        # if not self.controller.transmitter_status:
        #     tx_status = "Transmitter: Unreachable"
        # elif self.controller.system_on:
        #     tx_status = "Transmitter: Connected"
        # else:
        #     tx_status = "Transmitter: Off"

        # self.lbl_tx_status.config(text=tx_status)
        # self.lbl_rx_status.config(
        #     text="Control Station: Receiving data"
        #     if self.controller.system_on
        #     else "Control Station: Idle"
        # )
