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

from pages import DashboardPage, MonitoringPage, GraphsPage, PowerOnPage


# -----------------------------
# Data acquisition
# -----------------------------
class MotionReceiver(threading.Thread):
    """
    Background thread that listens to the defined serial port and
    pushes motion values to a shared deque.
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
        The transmitter sends lines like: 'MOTION:0' or 'MOTION:1'
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
        Simple motion value mock generator for testing: alternates between 0 and 1.
        """
        import random

        # toggling or random 0/1
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
            self.zigbee_thread = MotionReceiver(
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
        # instantiate workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Measurements"

        # write headers / column labels
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

        # write data rows
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
# Entry point
# -----------------------------
def main():
    app = MotionApp()
    app.mainloop()


if __name__ == "__main__":
    main()
