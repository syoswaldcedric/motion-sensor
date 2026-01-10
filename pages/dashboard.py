import tkinter as tk
from tkinter import PhotoImage
import platform


# import project metadata
from .base_page import BasePage
from metadata import CONSTANTS

os_name = platform.system()
os_version = platform.version()
os_release = platform.release()


# -----------------------------
# Dashboard Page
# -----------------------------
class DashboardPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.last_metrics = None
        self.selected_station = "control_station"

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.light_on_img = PhotoImage(file="./assets/light_on_resized.png")
        self.light_off_img = PhotoImage(file="./assets/light_off_resized.png")

        self.motion_state_var = tk.StringVar()
        self.motion_state_var.set("Motion Absent")

        # Motion status card
        motion_frame = tk.LabelFrame(
            self,
            text="Motion Sensor",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
        )
        motion_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.motion_value_label = tk.Label(
            motion_frame,
            image=self.light_on_img
            if self.motion_state_var.get() == "Motion Present"
            else self.light_off_img,
            text="0.0",
            bg="#252526",
            fg="#00ff9f",
            font=("Segoe UI", 9, "bold"),
        )
        self.motion_value_label.pack(anchor="center", pady=10)

        self.motion_state_label = tk.Label(
            motion_frame,
            textvariable=self.motion_state_var,
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 10),
        )
        self.motion_state_label.pack(anchor="center", pady=5)

        # System status card
        self.sys_frame = tk.Frame(
            self,
            bg="#252526",
        )
        self.sys_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Station selection buttons
        btn_frame = tk.Frame(self.sys_frame, bg="#1e1e1e")
        btn_frame.pack(fill="x", padx=10, pady=3)

        self.btn_control = tk.Button(
            btn_frame,
            text="Control Station",
            font=("Segoe UI", 9, "bold"),
            bg="#333333",
            fg="#ffffff",
            activebackground="#007acc",
            activeforeground="#ffffff",
            command=lambda: self.set_station("control_station"),
        )
        self.btn_control.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_transmitter = tk.Button(
            btn_frame,
            text="Transmitter",
            font=("Segoe UI", 9, "bold"),
            bg="#333333",
            fg="#ffffff",
            activebackground="#007acc",
            activeforeground="#ffffff",
            command=lambda: self.set_station("transmitter"),
        )
        self.btn_transmitter.pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.cpu_label = tk.Label(
            self.sys_frame,
            text="CPU: -- %",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8),
        )
        self.cpu_label.pack(anchor="w", padx=10, pady=1)

        self.ram_label = tk.Label(
            self.sys_frame,
            text="RAM: -- %",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8),
        )
        self.ram_label.pack(anchor="w", padx=10, pady=1)

        self.device_label = tk.Label(
            self.sys_frame,
            text="Device: --",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 10),
        )
        self.device_label.pack(anchor="w", padx=10, pady=1)
        self.os_label = tk.Label(
            self.sys_frame,
            text="OS: --",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8),
        )
        self.os_label.pack(anchor="w", padx=10, pady=1)

        self.disk_label = tk.Label(
            self.sys_frame,
            text="Disk: -- %",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8),
        )
        self.disk_label.pack(anchor="w", padx=10, pady=1)

        self.net_label = tk.Label(
            self.sys_frame,
            text="Net: up -- kB/s, down -- kB/s",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 8),
        )
        self.net_label.pack(
            anchor="w", padx=10, pady=0
        )  # remove padding from last element

        # System control frame
        control_frame = tk.LabelFrame(
            self,
            text="System Control",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
        )
        control_frame.grid(
            row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5, ipady=1
        )

        self.system_state_label = tk.Label(
            control_frame,
            text="System is OFF",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 10),
        )
        self.system_state_label.pack(anchor="w", padx=10, pady=3)

        info_label = tk.Label(
            control_frame,
            text="Use the toolbar to turn the system ON/OFF and switch between pages.",
            bg="#252526",
            fg="#ffffff",
            font=("Segoe UI", 10),
        )
        info_label.pack(anchor="w", padx=10)

        # Initial button state
        self.set_station(self.selected_station)

    def update_data(self, metrics, motion_series):
        self.last_metrics = metrics
        mv = metrics["motion"]
        self.motion_value_label.config(text=f"{mv:.2f}")

        self.motion_state_var.set("Motion Present" if mv >= 0.5 else "Motion Absent")

        # dynamic image update
        # if mv >= 0.5:
        if mv == 1:
            self.motion_value_label.config(image=self.light_on_img)
        else:
            # wait for 5 seconds
            self.motion_value_label.config(image=self.light_off_img)

        self.update_display()

    def set_station(self, station):
        self.selected_station = station
        # Update button styles
        if station == "control_station":
            self.btn_control.config(bg="#007acc", fg="#ffffff")
            self.btn_transmitter.config(bg="#333333", fg="#ffffff")
        else:
            self.btn_control.config(bg="#333333", fg="#ffffff")
            self.btn_transmitter.config(bg="#007acc", fg="#ffffff")

        if self.last_metrics:
            self.update_display()

    def update_display(self):
        if not self.last_metrics:
            return

        ms = self.last_metrics
        # Select dataset
        if self.selected_station == "transmitter":
            # Use mock transmitter data
            data = ms.get("transmitter", {})
            # Ensure safe fallback if data missing
            cpu = data.get("cpu", 0.0)
            ram = data.get("ram", 0.0)
            disk = data.get("disk", 0.0)
            net_up = data.get("net_up", 0.0)
            net_down = data.get("net_down", 0.0)
            os_label = ms.get("os", "---")
        else:
            # Default control station
            cpu = ms.get("cpu", 0.0)
            ram = ms.get("ram", 0.0)
            disk = ms.get("disk", 0.0)
            net_up = ms.get("net_up", 0.0)
            net_down = ms.get("net_down", 0.0)
            os_label = ms.get("os", f"{os_name} {os_version} {os_release}")

        self.cpu_label.config(text=f"CPU: {cpu:.1f} %")
        self.ram_label.config(text=f"RAM: {ram:.1f} %")
        self.disk_label.config(text=f"Disk: {disk:.1f} %")
        self.os_label.config(text=f"OS: {os_label}")
        self.device_label.config(
            text=f"Device: {CONSTANTS.get('DEVICE_VERSION').get(self.selected_station.lower())}"
        )
        self.net_label.config(
            text=f"Net: up {net_up:.1f} kB/s, down {net_down:.1f} kB/s"
        )

        self.system_state_label.config(
            text="System is ON" if self.controller.system_on else "System is OFF"
        )
