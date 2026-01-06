import tkinter as tk
from .base_page import BasePage
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import matplotlib

matplotlib.use("Agg")  # backend for embeddable canvas

# import project metadata
from metadata import CONSTANTS


# -----------------------------
# Graphs Page
# -----------------------------
class GraphsPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        frame = tk.LabelFrame(
            self,
            text="Motion Sensor History",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
        )
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Last 12 Motion Values")
        self.ax.set_xlabel("Sample")
        self.ax.set_ylabel("Value")
        self.ax.set_ylim(-0.1, 1.1)
        (self.line,) = self.ax.plot(
            range(CONSTANTS.get("MOTION_HISTORY_LENGTH")),
            [0] * CONSTANTS.get("MOTION_HISTORY_LENGTH"),
            "-o",
        )

        self.canvas = FigureCanvasTkAgg(self.figure, master=frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_data(self, metrics, motion_series):
        if not motion_series:
            return

        y = motion_series[-CONSTANTS.get("MOTION_HISTORY_LENGTH") :]
        x = list(range(len(y)))
        self.line.set_xdata(x)
        self.line.set_ydata(y)
        self.ax.set_xlim(-0.5, max(11.5, len(y)))
        self.canvas.draw_idle()
