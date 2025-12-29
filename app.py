import os
import sys
import time
import threading
from collections import deque
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess

import psutil
import serial  # pyserial
import serial.tools.list_ports

import matplotlib

matplotlib.use("Agg")  # backend for embeddable canvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import openpyxl

# import project metadata
from metadata import PROJECT_METADATA, ICONS, CONSTANTS


# -----------------------------
# Data acquisition (ZigBee)
# -----------------------------


class ZigBeeReceiver(threading.Thread):
    """
    Background thread that listens to a ZigBee serial port and
    pushes motion values to a shared deque.
    Replace the 'parse_motion_value' logic with your actual frame format.
    """

    def __init__(self, port, baudrate, motion_buffer, use_mock_if_fail=True):
        super().__init__(daemon=True)
        self.port_name = port
        self.baudrate = baudrate
        self.motion_buffer = motion_buffer
        self.use_mock_if_fail = use_mock_if_fail
        self.running = False
        self.serial = None

    def open_port(self):
        # Try the configured port first
        try:
            self.serial = serial.Serial(self.port_name, self.baudrate, timeout=1)
            print(f"Connected to ZigBee at {self.port_name}")
            return True
        except Exception:
            # Auto-detect if default failed
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                try:
                    # Avoid obviously wrong ports if possible, or just try the first available
                    self.serial = serial.Serial(p.device, self.baudrate, timeout=1)
                    print(f"Auto-detected and connected to ZigBee at {p.device}")
                    return True
                except Exception:
                    continue

            self.serial = None
            return False

    def parse_motion_value(self, raw_line):
        """
        Expect a simple protocol where the transmitter sends lines like:
        'MOTION:0' or 'MOTION:1' or an integer value 0..1023.
        """
        try:
            line = raw_line.strip().decode("utf-8")
            if not line:
                return None
            if "MOTION:" in line:
                _, val = line.split("MOTION:", 1)
                return float(val.strip())
            return float(line)
        except Exception:
            return None

    def mock_motion_value(self):
        """
        Simple mock generator: alternates between 0 and 1.
        Replace with a more realistic model if desired.
        """
        # Example: toggling or random 0/1
        import random

        return float(random.randint(0, 1))

    def run(self):
        self.running = True

        if not self.open_port() and not self.use_mock_if_fail:
            return

        while self.running:
            if self.serial:
                try:
                    raw = self.serial.readline()
                    value = self.parse_motion_value(raw)
                    if value is not None:
                        self.motion_buffer.append(value)
                except Exception:
                    # fall back to mock data if serial fails mid‑run
                    if self.use_mock_if_fail:
                        self.motion_buffer.append(self.mock_motion_value())
            else:
                # mock mode
                self.motion_buffer.append(self.mock_motion_value())

            time.sleep(0.1)  # Faster acquisition period for responsiveness

    def stop(self):
        self.running = False
        try:
            if self.serial and self.serial.is_open:
                self.serial.close()
        except Exception:
            pass


# -----------------------------
# Application core
# -----------------------------


class MotionApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(PROJECT_METADATA.get("Name"))
        self.geometry("1024x600")  # good default for LCD; resizable
        self.minsize(800, 480)
        self.iconphoto(True, tk.PhotoImage(file=ICONS.get("logo")))

        # shared state
        self.system_on = False
        self.motion_values = deque(maxlen=CONSTANTS.get("MOTION_HISTORY_LENGTH"))
        self.motion_values.extend([0] * CONSTANTS.get("MOTION_HISTORY_LENGTH"))
        self.measurement_history = []
        self.current_motion_value = 0.0

        # ZigBee receiver (lazy start when system is turned ON)
        self.zigbee_thread = None

        # main container for pages
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.container = container
        self.pages = {}

        self._create_styles()
        self._create_menu()
        self._create_toolbar()

        # create pages
        for PageClass in (PowerOnPage, DashboardPage, MonitoringPage, GraphsPage):
            page = PageClass(parent=container, controller=self)
            self.pages[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        # hide toolbar on landing screen
        self.toolbar.pack_forget()
        self.show_page("PowerOnPage")
        self.after(CONSTANTS.get("UPDATE_INTERVAL_MS"), self._periodic_update)

    # -----------------------------
    # UI building
    # -----------------------------

    def _create_styles(self):
        style = ttk.Style(self)
        if sys.platform == "win32":
            style.theme_use("clam")

        style.configure(
            "Main.TFrame",
            background="#1e1e1e",
        )
        style.configure(
            "Card.TLabelframe",
            background="#252526",
            foreground="#ffffff",
        )
        style.configure(
            "Card.TLabelframe.Label",
            background="#252526",
            foreground="#ffffff",
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "Main.TLabel",
            background="#1e1e1e",
            foreground="#ffffff",
            font=("Segoe UI", 11),
        )
        style.configure(
            "Value.TLabel",
            background="#252526",
            foreground="#00ff9f",
            font=("Segoe UI", 16, "bold"),
        )
        style.configure(
            "Nav.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=6,
        )
        style.map(
            "Nav.TButton",
            background=[("active", "#007acc")],
            foreground=[("active", "#ffffff")],
        )

    def _create_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=False)
        help_menu = tk.Menu(menubar, tearoff=False)

        file_menu.add_command(
            label="Save Measurements", command=self.save_measurements_to_excel
        )
        file_menu.add_command(label="View Saved Files", command=self.view_saved_files)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)

        help_menu.add_command(label="About", command=self.show_project_info)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

    def _create_toolbar(self):
        self.toolbar = ttk.Frame(self, style="Main.TFrame")

        # initial geometry config; we will pack/unpack this same widget
        self.toolbar.pack(side="top", fill="x")

        self.btn_on = ttk.Button(
            self.toolbar,
            text="Turn ON",
            style="Nav.TButton",
            command=self.turn_system_on,
        )
        # self.btn_on.pack(side="left", padx=5, pady=5)

        self.btn_off = ttk.Button(
            self.toolbar,
            text="Turn OFF",
            style="Nav.TButton",
            command=lambda: (
                self.turn_system_off,
                self.toolbar.pack_forget(),
                self.show_page("PowerOnPage"),
            ),
        )
        self.btn_off.pack(side="left", padx=5, pady=5)

        ttk.Button(
            self.toolbar,
            text="Dashboard",
            style="Nav.TButton",
            command=lambda: self.show_page("DashboardPage"),
        ).pack(side="right", padx=5)
        ttk.Button(
            self.toolbar,
            text="Graphs",
            style="Nav.TButton",
            command=lambda: self.show_page("GraphsPage"),
        ).pack(side="right", padx=5)
        ttk.Button(
            self.toolbar,
            text="Monitoring",
            style="Nav.TButton",
            command=lambda: self.show_page("MonitoringPage"),
        ).pack(side="right", padx=5)

        # remember pack options so we can show it again later
        self._toolbar_pack_opts = {"side": "top", "fill": "x"}

    # -----------------------------
    # Navigation and lifecycle
    # -----------------------------

    def show_page(self, name):
        page = self.pages[name]
        page.tkraise()

    def on_exit(self):
        if messagebox.askokcancel("Exit", "Close the HMI application?"):
            self.turn_system_off()
            self.destroy()

    # -----------------------------
    # System control
    # -----------------------------

    def turn_system_on(self):
        if self.system_on:
            return
        self.system_on = True

        # start ZigBee receiver
        if self.zigbee_thread is None or not self.zigbee_thread.is_alive():
            self.motion_values.clear()
            self.motion_values.extend([0] * CONSTANTS.get("MOTION_HISTORY_LENGTH"))
            self.measurement_history.clear()
            self.zigbee_thread = ZigBeeReceiver(
                port=CONSTANTS.get("DEFAULT_SERIAL_PORT"),
                baudrate=CONSTANTS.get("DEFAULT_BAUDRATE"),
                motion_buffer=self.motion_values,
                use_mock_if_fail=True,  # change to False for strict serial only
            )
            self.zigbee_thread.start()

        self.btn_on.state(["disabled"])
        self.btn_off.state(["!disabled"])

    def turn_system_off(self):
        self.system_on = False
        if self.zigbee_thread:
            self.zigbee_thread.stop()
        self.btn_on.state(["!disabled"])
        self.btn_off.state(["disabled"])

    # -----------------------------
    # Periodic update
    # -----------------------------

    def _periodic_update(self):
        # latest motion value
        if self.motion_values:
            self.current_motion_value = self.motion_values[-1]

        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent

        # simple network throughput estimation (kB/s)
        net1 = psutil.net_io_counters()
        time.sleep(0.1)
        net2 = psutil.net_io_counters()
        sent_kbps = (net2.bytes_sent - net1.bytes_sent) / 1024.0 / 0.1
        recv_kbps = (net2.bytes_recv - net1.bytes_recv) / 1024.0 / 0.1

        metrics = {
            "motion": self.current_motion_value,
            "cpu": cpu,
            "ram": ram,
            "disk": disk,
            "net_up": sent_kbps,
            "net_down": recv_kbps,
            "timestamp": datetime.now(),
        }

        if self.system_on:
            self.measurement_history.append(metrics)

        # propagate metrics to pages
        for page in self.pages.values():
            page.update_data(metrics, list(self.motion_values))

        self.after(CONSTANTS.get("UPDATE_INTERVAL_MS"), self._periodic_update)

    # -----------------------------
    # Menu actions
    # -----------------------------

    def show_project_info(self):
        msg = (
            f"Name: {PROJECT_METADATA.get('Name')}\n"
            f"Version: {PROJECT_METADATA.get('Version')}\n"
            f"Authors: {', '.join(PROJECT_METADATA.get('Authors', []))}\n\n"
            f"Description:\n{PROJECT_METADATA.get('Description')}\n\n"
            f"License: {PROJECT_METADATA.get('License')}\n"
            f"GitHub: {PROJECT_METADATA.get('GitHub URL')}\n"
            f"Issues: {PROJECT_METADATA.get('Issues')}"
        )
        messagebox.showinfo(f"About {PROJECT_METADATA.get('Name')}", msg)

    def _default_save_directory(self):
        base = os.path.join(os.path.expanduser("~"), "motion_measurements")
        os.makedirs(base, exist_ok=True)
        return base

    def save_measurements_to_excel(self):
        # let user choose directory
        target_dir = filedialog.askdirectory(
            title="Select directory to save measurements"
        )
        if not target_dir:  # user cancelled
            return

        filename = datetime.now().strftime("measurements_%Y%m%d_%H%M%S.xlsx")
        full_path = os.path.join(target_dir, filename)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Measurements"

        ws.append(
            [
                "Timestamp",
                "Motion Value",
                "CPU Usage (%)",
                "RAM Usage (%)",
                "Disk Usage (%)",
                "Net Up (kB/s)",
                "Net Down (kB/s)",
            ]
        )

        for item in self.measurement_history:
            ws.append(
                [
                    item["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                    item["motion"],
                    item["cpu"],
                    item["ram"],
                    item["disk"],
                    item["net_up"],
                    item["net_down"],
                ]
            )

        wb.save(full_path)
        messagebox.showinfo("Save Measurements", f"Measurements saved to:\n{full_path}")

    def view_saved_files(self):
        base_dir = self._default_save_directory()
        if not os.path.isdir(base_dir):
            messagebox.showinfo("Saved Files", "No saved measurement directory found.")
            return
        # simple file chooser pointing to the directory
        file_path = filedialog.askopenfilename(
            title="Open saved measurement",
            initialdir=base_dir,
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )

        if file_path:
            try:
                if os.name == "nt":  # Windows
                    os.startfile(file_path)
                elif os.uname().sysname == "Darwin":  # macOS
                    subprocess.call(("open", file_path))
                else:  # Linux (including RPi OS)
                    subprocess.call(("xdg-open", file_path))
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Could not open file explorer. Error: {e}"
                )


# -----------------------------
# Base page
# -----------------------------


class BasePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller

    def update_data(self, metrics, motion_series):
        """
        Called every second by the controller.
        Child classes override this method.
        """
        pass


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


# -----------------------------
# Graphs Page
# -----------------------------


class GraphsPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        frame = ttk.Labelframe(
            self, text="Motion Sensor History", style="Card.TLabelframe"
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
        self.ax.set_xlim(-0.5, max(11.5, len(y) - 0.5))
        self.canvas.draw_idle()


# -----------------------------
# Power ON Page
# -----------------------------


class PowerOnPage(BasePage):
    """
    Landing screen shown at startup.
    Contains a large Power ON button; when pressed, it turns the
    system on and navigates to the Dashboard page.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        frame = ttk.Frame(self, style="Main.TFrame")
        frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        title = ttk.Label(
            frame,
            text=CONSTANTS.get("APP_TITLE"),
            style="Main.TLabel",
            font=("Segoe UI", 18, "bold"),
        )
        title.pack(pady=30)

        # subtitle = ttk.Label(
        #     frame,
        #     text="Press POWER ON to start the Control Station HMI",
        #     style="Main.TLabel",
        # )
        # subtitle.pack(pady=10)

        power_button = ttk.Button(
            frame,
            # image=tk.PhotoImage(file="./assets/power_btn_lg.png"),
            text="POWER ON",
            compound="top",
            # style="Nav.TButton",
            command=self._on_power_on_clicked,
        )
        power_button.pack(pady=40, ipadx=40, ipady=20)

    def _on_power_on_clicked(self):
        self.controller.turn_system_on()
        # show toolbar again using stored pack options
        if getattr(self.controller, "toolbar", None):
            self.controller.toolbar.pack(**self.controller._toolbar_pack_opts)
        self.controller.show_page("DashboardPage")


# -----------------------------
# Entry point
# -----------------------------


def main():
    app = MotionApp()
    app.mainloop()


if __name__ == "__main__":
    main()
