from tkinter import ttk
from .base_page import BasePage


# -----------------------------
# Dashboard Page
# -----------------------------
class DashboardPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Motion status card
        motion_frame = ttk.Labelframe(
            self, text="Motion Sensor", style="Card.TLabelframe"
        )
        motion_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.motion_value_label = ttk.Label(
            motion_frame, text="0.0", style="Value.TLabel"
        )
        self.motion_value_label.pack(anchor="center", pady=10)

        self.motion_state_label = ttk.Label(
            motion_frame, text="No motion", style="Main.TLabel"
        )
        self.motion_state_label.pack(anchor="center", pady=5)

        # System status card
        sys_frame = ttk.Labelframe(
            self, text="Control Station Status", style="Card.TLabelframe"
        )
        sys_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.cpu_label = ttk.Label(sys_frame, text="CPU: -- %", style="Main.TLabel")
        self.cpu_label.pack(anchor="w", padx=10, pady=2)

        self.ram_label = ttk.Label(sys_frame, text="RAM: -- %", style="Main.TLabel")
        self.ram_label.pack(anchor="w", padx=10, pady=2)

        self.disk_label = ttk.Label(sys_frame, text="Disk: -- %", style="Main.TLabel")
        self.disk_label.pack(anchor="w", padx=10, pady=2)

        self.net_label = ttk.Label(
            sys_frame, text="Net: up -- kB/s, down -- kB/s", style="Main.TLabel"
        )
        self.net_label.pack(anchor="w", padx=10, pady=2)

        # System control state
        control_frame = ttk.Labelframe(
            self, text="System Control", style="Card.TLabelframe"
        )
        control_frame.grid(
            row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10
        )

        self.system_state_label = ttk.Label(
            control_frame, text="System is OFF", style="Main.TLabel"
        )
        self.system_state_label.pack(anchor="w", padx=10, pady=5)

        info_label = ttk.Label(
            control_frame,
            text="Use the toolbar to turn the system ON/OFF and switch between pages.",
            style="Main.TLabel",
        )
        info_label.pack(anchor="w", padx=10, pady=5)

    def update_data(self, metrics, motion_series):
        mv = metrics["motion"]
        self.motion_value_label.config(text=f"{mv:.2f}")
        self.motion_state_label.config(
            text="Motion Present" if mv >= 0.5 else "Motion Absent"
        )

        self.cpu_label.config(text=f"CPU: {metrics['cpu']:.1f} %")
        self.ram_label.config(text=f"RAM: {metrics['ram']:.1f} %")
        self.disk_label.config(text=f"Disk: {metrics['disk']:.1f} %")
        self.net_label.config(
            text=f"Net: up {metrics['net_up']:.1f} kB/s, down {metrics['net_down']:.1f} kB/s"
        )

        self.system_state_label.config(
            text="System is ON" if self.controller.system_on else "System is OFF"
        )
