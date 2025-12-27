# main_app.py

import tkinter as tk
from tkinter import ttk, messagebox, Menu
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import subprocess  # For 'View Saved Files'

# Import local modules
from metadata import PROJECT_METADATA, HMI_COLORS
from data_handler import ZigBeeDataSimulator, SystemMetrics


class HMI_App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{PROJECT_METADATA['Name']} v{PROJECT_METADATA['Version']}")
        self.geometry("1024x600")  # Start size for RPi screen
        self.state("zoomed")  # Start maximized
        self.config(bg=HMI_COLORS["BACKGROUND"])

        # --- Data Handlers ---
        self.simulator = ZigBeeDataSimulator()
        self.metrics_handler = SystemMetrics(PROJECT_METADATA)
        self.data_log = []  # List to store all measurement dicts

        # --- Real-Time Data Storage ---
        self.motion_values = [0] * 12  # Last 12 motion values (for graph)
        self.is_system_on = False

        # --- UI Setup ---
        self.setup_styles()
        self.setup_menu_bar()
        self.setup_main_frame()
        self.create_pages()

        # --- Start Update Loop ---
        self.after(100, self.update_realtime_data)  # Initial call

    def setup_styles(self):
        """Configures ttk styles for an HMI look."""
        style = ttk.Style(self)
        style.theme_use("clam")

        # Primary frame style
        style.configure("HMI.TFrame", background=HMI_COLORS["BACKGROUND"])

        # Label styles
        style.configure(
            "HMI.TLabel",
            background=HMI_COLORS["BACKGROUND"],
            foreground=HMI_COLORS["FOREGROUND"],
            font=("Arial", 14),
        )
        style.configure(
            "HMI.THeading.TLabel",
            background=HMI_COLORS["BACKGROUND"],
            foreground=HMI_COLORS["PRIMARY"],
            font=("Arial", 20, "bold"),
        )

        # Button styles
        style.configure(
            "HMI.TButton",
            background=HMI_COLORS["INFO"],
            foreground=HMI_COLORS["TEXT_BRIGHT"],
            font=("Arial", 12, "bold"),
            padding=10,
        )
        style.map("HMI.TButton", background=[("active", HMI_COLORS["ACCENT"])])

        # Data Display Label (for real-time values)
        style.configure(
            "Data.TLabel",
            background=HMI_COLORS["BACKGROUND"],
            foreground=HMI_COLORS["TEXT_BRIGHT"],
            font=("Consolas", 24, "bold"),
        )

    # --- Menu Bar ---
    def setup_menu_bar(self):
        """Creates the application's top menu bar."""
        menu_bar = Menu(self)
        self.config(menu=menu_bar)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(
            label="Save Measurements (Excel)",
            command=lambda: self.metrics_handler.save_measurements(self.data_log),
        )
        file_menu.add_command(label="View Saved Files", command=self.view_saved_files)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(
            label="Project Information", command=self.show_project_info
        )
        help_menu.add_command(
            label="View Schematics",
            command=lambda: self.show_image_asset("schematics.jpeg"),
        )
        help_menu.add_command(
            label="View HMI Flowchart",
            command=lambda: self.show_image_asset("HMI_flowchart.jpeg"),
        )

        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)

    def show_project_info(self):
        """Displays project metadata in a popup."""
        info = "\n".join([f"{k}: {v}" for k, v in PROJECT_METADATA.items()])
        messagebox.showinfo("Project Information", info)

    def view_saved_files(self):
        """
        Attempts to open the default file explorer for the user to view
        saved data. This is OS-dependent.
        """
        try:
            # We will use the current directory as a starting point.
            start_path = os.getcwd()

            if os.name == "nt":  # Windows
                os.startfile(start_path)
            elif os.uname().sysname == "Darwin":  # macOS
                subprocess.call(("open", start_path))
            else:  # Linux (including RPi OS)
                subprocess.call(("xdg-open", start_path))
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file explorer. Error: {e}")

    def show_image_asset(self, filename):
        """Simulates showing an asset (e.g., in a new window or default viewer)."""
        messagebox.showinfo(
            "Asset Viewer",
            f"--- SIMULATION ---\n\nWould normally open the file:\nassets/{filename}",
        )

    # --- Main Frame and Navigation ---
    def setup_main_frame(self):
        """Sets up the main layout with a left Navigation Frame and a right Content Frame."""

        # Grid Configuration (Responsive Layout)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Nav Frame fixed size
        self.grid_columnconfigure(1, weight=1)  # Content Frame expands

        # 1. Navigation Frame (Fixed Width)
        nav_frame = ttk.Frame(self, style="HMI.TFrame", width=200, padding="10 0 10 0")
        nav_frame.grid(row=0, column=0, sticky="ns")
        nav_frame.grid_propagate(False)  # Prevents frame from resizing based on content

        ttk.Label(
            nav_frame,
            text="HMI Controls",
            style="HMI.THeading.TLabel",
            foreground=HMI_COLORS["TEXT_BRIGHT"],
        ).pack(pady=10)

        # 2. Content Frame (Expands)
        self.content_frame = ttk.Frame(self, style="HMI.TFrame", padding=20)
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        # System Control Buttons (Top of Nav Frame)
        self.btn_on = self.create_nav_button(
            nav_frame,
            "Turn ON System",
            lambda: self.toggle_system(True),
            HMI_COLORS["PRIMARY"],
        )
        self.btn_off = self.create_nav_button(
            nav_frame,
            "Turn OFF System",
            lambda: self.toggle_system(False),
            HMI_COLORS["ACCENT"],
        )

        # Initial state setup
        self.btn_off.config(state=tk.DISABLED)

        # Navigation Buttons (Dashboard, Monitoring, Graphs)
        ttk.Separator(nav_frame, orient="horizontal").pack(fill="x", pady=15)
        self.create_nav_button(
            nav_frame, "Dashboard", lambda: self.show_frame(self.dashboard_frame)
        ).pack(fill="x", pady=5)
        self.create_nav_button(
            nav_frame,
            "System Monitoring",
            lambda: self.show_frame(self.monitoring_frame),
        ).pack(fill="x", pady=5)
        self.create_nav_button(
            nav_frame, "Graphs & Analytics", lambda: self.show_frame(self.graphs_frame)
        ).pack(fill="x", pady=5)

    def create_nav_button(self, parent, text, command, color=HMI_COLORS["INFO"]):
        """Helper to create stylized navigation/control buttons."""
        # In a real app, we would use ImageTk to load icons from the assets folder.
        # Since we can't load images, we style the button heavily.
        btn = ttk.Button(parent, text=text, command=command, style="HMI.TButton")
        btn.config(style="HMI.TButton", padding=(10, 15))  # Make it larger
        btn.pack(fill="x", pady=5)
        return btn

    def show_frame(self, frame):
        """Brings the specified frame to the front (smooth transition placeholder)."""
        # A simple lift() for frame transition
        frame.tkraise()

    def toggle_system(self, state):
        """Toggles the system ON/OFF state."""
        self.is_system_on = state
        self.simulator.toggle_system(state)

        status_text = "OPERATIONAL" if state else "STANDBY"
        status_color = HMI_COLORS["PRIMARY"] if state else HMI_COLORS["ACCENT"]

        # Update UI labels
        self.system_status_var.set(status_text)
        self.status_label.config(foreground=status_color)

        # Update control button states
        self.btn_on.config(state=tk.DISABLED if state else tk.NORMAL)
        self.btn_off.config(state=tk.NORMAL if state else tk.DISABLED)

        messagebox.showinfo("System Control", f"System is now set to {status_text}.")

    # --- Page Creation ---
    def create_pages(self):
        """Creates all application pages (frames) and places them in the content_frame."""
        self.frames = {}

        # 1. Dashboard
        self.dashboard_frame = self.create_dashboard_page(self.content_frame)
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
        self.frames["Dashboard"] = self.dashboard_frame

        # 2. System Monitoring
        self.monitoring_frame = self.create_monitoring_page(self.content_frame)
        self.monitoring_frame.grid(row=0, column=0, sticky="nsew")
        self.frames["Monitoring"] = self.monitoring_frame

        # 3. Graphs & Analytics
        self.graphs_frame = self.create_graphs_page(self.content_frame)
        self.graphs_frame.grid(row=0, column=0, sticky="nsew")
        self.frames["Graphs"] = self.graphs_frame

        # Show the initial page
        self.show_frame(self.dashboard_frame)

    # --- Dashboard Page ---
    def create_dashboard_page(self, parent):
        """
        Creates the main Dashboard page.
        Displays system status and latest sensor data.
        """
        frame = ttk.Frame(parent, style="HMI.TFrame")
        frame.grid_columnconfigure((0, 1), weight=1)

        ttk.Label(frame, text="DASHBOARD", style="HMI.THeading.TLabel").grid(
            row=0, column=0, columnspan=2, pady=10, sticky="w"
        )
        ttk.Separator(frame, orient="horizontal").grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20)
        )

        # --- System Status Panel ---
        status_panel = self.create_panel(frame, "System Status", 2, 0)

        self.system_status_var = tk.StringVar(value="STANDBY")
        self.status_label = ttk.Label(
            status_panel,
            textvariable=self.system_status_var,
            font=("Consolas", 36, "bold"),
            background=HMI_COLORS["BACKGROUND"],
            foreground=HMI_COLORS["ACCENT"],
        )
        self.status_label.pack(pady=20, padx=20)

        # --- Real-Time Sensor Data Panel ---
        sensor_panel = self.create_panel(frame, "Motion Sensor Data", 2, 1)

        self.motion_var = tk.StringVar(value="--")
        self.signal_var = tk.StringVar(value="--")

        self.create_data_display(
            sensor_panel, "Motion Detected:", self.motion_var
        ).pack(pady=5)
        self.create_data_display(sensor_panel, "Signal Quality:", self.signal_var).pack(
            pady=5
        )

        return frame

    # --- System Monitoring Page ---
    def create_monitoring_page(self, parent):
        """
        Creates the System Monitoring page.
        Displays Control Station CPU, RAM, Disk, and Network usage.
        """
        frame = ttk.Frame(parent, style="HMI.TFrame")
        frame.grid_columnconfigure(0, weight=1)

        ttk.Label(
            frame, text="CONTROL STATION MONITORING", style="HMI.THeading.TLabel"
        ).pack(pady=10, anchor="w")
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=(0, 20))

        # Metrics Panel
        metrics_panel = ttk.Frame(frame, style="HMI.TFrame")
        metrics_panel.pack(fill="x", padx=50)
        metrics_panel.grid_columnconfigure((0, 1), weight=1)

        # Variables for real-time updates
        self.cpu_var = tk.StringVar(value="--")
        self.ram_var = tk.StringVar(value="--")
        self.disk_var = tk.StringVar(value="--")
        self.net_var = tk.StringVar(value="--")
        self.time_var = tk.StringVar(value="--")

        # Place metric displays
        self.create_data_display(metrics_panel, "System Time:", self.time_var).grid(
            row=0, column=0, sticky="w", pady=10
        )
        self.create_data_display(metrics_panel, "CPU Usage:", self.cpu_var).grid(
            row=1, column=0, sticky="w", pady=10
        )
        self.create_data_display(metrics_panel, "RAM Usage:", self.ram_var).grid(
            row=2, column=0, sticky="w", pady=10
        )
        self.create_data_display(metrics_panel, "Disk Usage:", self.disk_var).grid(
            row=1, column=1, sticky="w", pady=10
        )
        self.create_data_display(metrics_panel, "Network Speed:", self.net_var).grid(
            row=2, column=1, sticky="w", pady=10
        )

        return frame

    # --- Graphs & Analytics Page ---
    def create_graphs_page(self, parent):
        """
        Creates the Graphs & Analytics page.
        Features a dynamic Matplotlib line graph.
        """
        frame = ttk.Frame(parent, style="HMI.TFrame")
        frame.grid_columnconfigure(0, weight=1)

        ttk.Label(frame, text="GRAPHS & ANALYTICS", style="HMI.THeading.TLabel").pack(
            pady=10, anchor="w"
        )
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=(0, 20))

        # Matplotlib Figure Setup
        # Use a dark style for HMI look
        plt.style.use("dark_background")
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.fig.patch.set_facecolor(HMI_COLORS["BACKGROUND"])
        self.ax.set_facecolor(HMI_COLORS["BACKGROUND"])

        self.ax.set_title(
            "Motion Detection History (Last 12 Values)", color=HMI_COLORS["FOREGROUND"]
        )
        self.ax.set_xlabel("Sample Index", color=HMI_COLORS["TEXT_DIM"])
        self.ax.set_ylabel("Motion Detected (1=Yes)", color=HMI_COLORS["TEXT_DIM"])
        self.ax.tick_params(axis="x", colors=HMI_COLORS["TEXT_DIM"])
        self.ax.tick_params(axis="y", colors=HMI_COLORS["TEXT_DIM"])
        self.ax.set_yticks([0, 1])
        self.ax.set_ylim(-0.1, 1.1)
        (self.line,) = self.ax.plot(
            range(12), self.motion_values, color=HMI_COLORS["PRIMARY"], marker="o"
        )

        # Matplotlib Canvas Integration
        canvas = FigureCanvasTkAgg(self.fig, master=frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=20, pady=20)

        return frame

    # --- Utility UI Components ---
    def create_panel(self, parent, title, row, col):
        """Creates a common panel structure for data grouping."""
        panel = ttk.LabelFrame(parent, text=title, padding=20)
        panel.grid(row=row, column=col, padx=20, pady=10, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        return panel

    def create_data_display(self, parent, label_text, data_var):
        """Creates a structure for a label and its corresponding real-time data value."""
        data_frame = ttk.Frame(parent, style="HMI.TFrame")

        # Label (Description)
        ttk.Label(data_frame, text=label_text, style="HMI.TLabel").pack(
            side="left", padx=(0, 10)
        )

        # Data Value (Large, Bold)
        ttk.Label(data_frame, textvariable=data_var, style="Data.TLabel").pack(
            side="left"
        )

        return data_frame

    # --- Real-Time Update Logic ---
    def update_realtime_data(self):
        """
        The main loop for updating all real-time data in the GUI.
        Called every 1 second.
        """
        # 1. Get Motion Sensor Data (Simulated ZigBee)
        timestamp, motion, signal = self.simulator.get_latest_motion_data()

        # Update motion history
        self.motion_values.pop(0)
        self.motion_values.append(motion)

        # Update Dashboard
        self.motion_var.set("MOTION" if motion == 1 else "Clear")
        self.signal_var.set(f"{signal}%")

        # 2. Get Control Station System Metrics (Real psutil)
        metrics = self.metrics_handler.get_control_station_metrics()

        # Update Monitoring Page
        self.cpu_var.set(metrics["CPU Usage"])
        self.ram_var.set(metrics["RAM Usage"])
        self.disk_var.set(metrics["Disk Usage"])
        self.net_var.set(metrics["Network Speed"])
        self.time_var.set(metrics["System Time"])

        # 3. Update Data Log
        log_entry = {
            "Timestamp": timestamp,
            "Motion_Detected": motion,
            "Signal_Quality": signal,
            "CPU_Usage": metrics["CPU Usage"],
            "RAM_Usage": metrics["RAM Usage"],
            "Disk_Usage": metrics["Disk Usage"],
            "Network_Speed": metrics["Network Speed"],
        }
        self.data_log.append(log_entry)

        # 4. Update Graph
        self.line.set_ydata(self.motion_values)
        self.fig.canvas.draw_idle()

        # 5. Loop the update
        self.after(1000, self.update_realtime_data)  # Re-schedule for 1000ms (1 second)

    def on_closing(self):
        """Handles application closing."""
        if messagebox.askyesno("Exit Application", "Do you want to shut down the HMI?"):
            self.destroy()


if __name__ == "__main__":
    app = HMI_App()
    app.mainloop()
