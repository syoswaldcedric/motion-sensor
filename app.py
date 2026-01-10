import os
import time

from collections import deque
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

import psutil
import random

import openpyxl


from project_utils import MotionReceiver

# import project metadata
from metadata import PROJECT_METADATA, ICONS, CONSTANTS

from pages import DashboardPage, MonitoringPage, GraphsPage, PowerOnPage, LogsPage


# -----------------------------
# Application core
# -----------------------------
class MotionApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(PROJECT_METADATA.get("Name"))
        self.resizable(False, False)
        self.geometry(
            f"{CONSTANTS.get('DEFAULT_SCREEN_SIZE')[0]}x{CONSTANTS.get('DEFAULT_SCREEN_SIZE')[1]}"
        )  # good default for LCD; resizable
        self.minsize(
            CONSTANTS.get("DEFAULT_SCREEN_SIZE")[0],
            CONSTANTS.get("DEFAULT_SCREEN_SIZE")[1],
        )
        self.iconphoto(True, tk.PhotoImage(file=ICONS.get("logo")))

        # shared state
        self.system_on = False
        self.motion_values = deque(maxlen=CONSTANTS.get("MOTION_HISTORY_LENGTH"))
        self.motion_values.extend([0] * CONSTANTS.get("MOTION_HISTORY_LENGTH"))
        self.measurement_history = []
        self.current_motion_value = 0.0

        # self.log_buffer = deque(maxlen=CONSTANTS.get("LOGS_HISTORY_LENGTH"))
        self.log_buffer = []

        # Motion receiver (lazy start when system is turned ON)
        self.background_thread = None

        self.nav_buttons = {}
        # Make window fullscreen
        # self.attributes("-fullscreen", True)

        # Optional: close fullscreen with Escape key
        self.bind("<Escape>", lambda e: self.destroy())

        # -----------------------------
        # Scrollable Main Layout
        # -----------------------------
        self._create_menu()

        # 3. Main layout frame (holds canvas area)
        main_layout = tk.Frame(self, bg="#1e1e1e")
        main_layout.pack(fill="both", expand=True)

        # 3. Canvas and Scrollbar setup
        self.canvas = tk.Canvas(main_layout, bg="#1e1e1e", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(
            main_layout, orient="vertical", command=self.canvas.yview
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # 4. Inner container for pages
        # container = tk.Frame(self.canvas, bg="#1e1e1e")
        container = tk.Frame(self.canvas, bg="red")

        # Grid config for the pages inside the container
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Create window inside canvas
        self.canvas_frame = self.canvas.create_window(
            (0, 0), window=container, anchor="nw"
        )
        self.container = container
        self.pages = {}
        # 2. Toolbar fixed at the top (sibling of main_layout)
        self._create_toolbar()

        # When container changes size (widgets added/removed), update scrollregion
        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        container.bind("<Configure>", on_frame_configure)

        # When canvas changes size (window resized), force container width to match
        def on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_frame, width=event.width)

        self.canvas.bind("<Configure>", on_canvas_configure)

        # create pages
        for PageClass in (
            PowerOnPage,
            DashboardPage,
            MonitoringPage,
            GraphsPage,
            LogsPage,
        ):
            # for PageClass in (
            #     DashboardPage,
            #     PowerOnPage,
            #     MonitoringPage,
            # ):
            page = PageClass(parent=container, controller=self)
            self.pages[PageClass.__name__] = page
            page.grid(row=1, column=0, sticky="nsew")

        # hide toolbar on landing screens
        # self.toolbar.pack_forget()
        self.toolbar.grid_forget()
        self.show_page("PowerOnPage")
        self.after(CONSTANTS.get("UPDATE_INTERVAL_MS"), self._periodic_update)

    def _create_menu(self):
        self.menubar = tk.Menu(self)

        self.file_menu = tk.Menu(self.menubar, tearoff=False)
        help_menu = tk.Menu(self.menubar, tearoff=False)

        self.file_menu.add_command(
            label="Save Measurements", command=self.save_measurements_to_excel
        )

        self.file_menu.add_command(
            label="View Saved Files",
            command=self.view_saved_files,
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_exit)

        help_menu.add_command(label="About", command=self.show_project_info)

        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=self.menubar)

    def _create_toolbar(self):
        # self.toolbar = tk.Frame(self, bg="#1e1e1e")
        # self.toolbar = tk.Frame(self.canvas, bg="#1e1e1e")
        self.toolbar = tk.Frame(self.container, bg="#1e1e1e")
        self.toolbar.grid(row=0, column=0, sticky="nsew")

        # initial geometry config; we will pack/unpack this same widget
        # self.toolbar.pack(side="top", fill="x")

        self.btn_on = tk.Button(
            self.toolbar,
            text="Turn ON",
            font=("Segoe UI", 9, "bold"),
            bg="#333333",
            fg="#ffffff",
            activebackground="#007acc",
            activeforeground="#ffffff",
            command=self.turn_system_on,
        )
        # self.btn_on.pack(side="left", padx=5, pady=5)

        self.btn_off = tk.Button(
            self.toolbar,
            text="Turn OFF",
            font=("Segoe UI", 9, "bold"),
            bg="#333333",
            fg="#ffffff",
            activebackground="#007acc",
            activeforeground="#ffffff",
            command=lambda: (
                self.turn_system_off,
                self.toolbar.grid_forget(),
                self.show_page("PowerOnPage"),
            ),
        )
        self.btn_off.pack(side="left", padx=5, pady=5)

        self.nav_buttons["DashboardPage"] = tk.Button(
            self.toolbar,
            text="Dashboard",
            font=("Segoe UI", 9, "bold"),
            bg="#333333",
            fg="#ffffff",
            activebackground="#007acc",
            activeforeground="#ffffff",
            command=lambda: self.show_page("DashboardPage"),
        )
        self.nav_buttons["DashboardPage"].pack(side="right", padx=5)

        self.nav_buttons["GraphsPage"] = tk.Button(
            self.toolbar,
            text="Graphs",
            font=("Segoe UI", 9, "bold"),
            bg="#333333",
            fg="#ffffff",
            activebackground="#007acc",
            activeforeground="#ffffff",
            command=lambda: self.show_page("GraphsPage"),
        )
        self.nav_buttons["GraphsPage"].pack(side="right", padx=5)

        self.nav_buttons["LogsPage"] = tk.Button(
            self.toolbar,
            text="Logs",
            font=("Segoe UI", 9, "bold"),
            bg="#333333",
            fg="#ffffff",
            activebackground="#007acc",
            activeforeground="#ffffff",
            command=lambda: self.show_page("LogsPage"),
        )
        self.nav_buttons["LogsPage"].pack(side="right", padx=5)

        self.nav_buttons["MonitoringPage"] = tk.Button(
            self.toolbar,
            text="Monitoring",
            font=("Segoe UI", 9, "bold"),
            bg="#333333",
            fg="#ffffff",
            activebackground="#007acc",
            activeforeground="#ffffff",
            command=lambda: self.show_page("MonitoringPage"),
        )
        self.nav_buttons["MonitoringPage"].pack(side="right", padx=5)

        # remember pack options so we can show it again later
        self._toolbar_pack_opts = {
            "side": "top",
            "fill": "x",
            # "before": self.controller,
        }

    # -----------------------------
    # Navigation and lifecycle
    # -----------------------------
    def enable_save_measurements(self):
        self.file_menu.entryconfig("Save Measurements", state="normal")

    def disable_save_measurements(self):
        self.file_menu.entryconfig("Save Measurements", state="disabled")

    # -----------------------------
    # Navigation and lifecycle
    # -----------------------------

    def show_page(self, name):
        # print(f"name: {name}")
        # disable save measurements if on power on page
        if name == "PowerOnPage":
            self.disable_save_measurements()
        else:
            self.enable_save_measurements()
        # Update button styles for navigation
        for page_name, btn in self.nav_buttons.items():
            if page_name == name:
                btn.config(bg="#007acc")
            else:
                btn.config(bg="#333333")

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

        # start Motion receiver thread
        if self.background_thread is None or not self.background_thread.is_alive():
            self.motion_values.clear()
            self.motion_values.extend([0] * CONSTANTS.get("MOTION_HISTORY_LENGTH"))
            self.measurement_history.clear()
            self.background_thread = MotionReceiver(
                port=CONSTANTS.get("DEFAULT_SERIAL_PORT"),
                baudrate=CONSTANTS.get("DEFAULT_BAUDRATE"),
                motion_buffer=self.motion_values,
                # TODO: set true in development only, change to False for strict serial only
                use_mock_if_fail=True,
            )
            self.background_thread.start()

        self.btn_on.config(state="disabled")
        self.btn_off.config(state="normal")

    def turn_system_off(self):
        self.system_on = False
        self.file_menu.entryconfig("Save Measurements", state="disabled")
        if self.background_thread:
            self.background_thread.stop()
        self.btn_on.config(state="normal")
        self.btn_off.config(state="disabled")

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
            "version": CONSTANTS.get("DEVICE_VERSION"),
            # "logs": "{type: 'info', message: 'System is on'}, {type: 'warning', message: 'Transmitter station is offline'}, {type: 'error', message: 'motion sensor is offline'}",
            "transmitter": {
                "log": "{type: 'info', message: 'System is on'}, {type: 'warning', message: 'Transmitter station is offline'}, {type: 'error', message: 'motion sensor is offline'}",
                "cpu": random.uniform(10, 40),
                "ram": random.uniform(20, 50),
                "disk": 45.0 + random.uniform(-0.5, 0.5),
                "net_up": random.uniform(0, 50),
                "net_down": random.uniform(0, 50),
                "version": CONSTANTS.get("DEVICE_VERSION"),
            },
        }

        if self.system_on:
            self.measurement_history.append(metrics)

        # propagate metrics to pages
        for page in self.pages.values():
            page.update_data(metrics, list(self.motion_values), self.log_buffer)

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
