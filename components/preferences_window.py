import tkinter as tk
from tkinter import messagebox
from utils.constants import HMI_COLORS, CONSTANTS
from utils.settings_manager import SettingsManager


class PreferencesWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Preferences")
        self.resizable(False, False)
        self.configure(bg=HMI_COLORS["BACKGROUND"])

        # Center the window
        window_width = CONSTANTS.get("DEFAULT_SCREEN_SIZE", [480, 300])[0]
        # window_height = 550  # Increased height for new fields
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # use set a reasonable max
        window_height = CONSTANTS.get("DEFAULT_SCREEN_SIZE", [480, 300])[1]

        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        # Scrollable Frame setup for preferences because it's getting long
        # But for simplicity, let's try to fit everything or use a canvas if needed.
        # Given the number of items (approx 8-10 rows), it might fit in 550px.

        container = tk.Frame(self, bg=HMI_COLORS["BACKGROUND"])
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=HMI_COLORS["BACKGROUND"], highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(
            canvas, bg=HMI_COLORS["BACKGROUND"], padx=20, pady=20
        )

        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame = self.scrollable_frame

        # Serial Port
        tk.Label(
            frame,
            text="Serial Port:",
            bg=HMI_COLORS["BACKGROUND"],
            fg=HMI_COLORS["FOREGROUND"],
            font=("Segoe UI", 10),
        ).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_port = tk.Entry(
            frame, bg="#3E3E42", fg="#FFFFFF", insertbackground="white"
        )
        self.entry_port.insert(0, CONSTANTS.get("DEFAULT_SERIAL_PORT", ""))
        self.entry_port.grid(row=0, column=1, sticky="ew", pady=5)

        # Baudrate
        tk.Label(
            frame,
            text="Baudrate:",
            bg=HMI_COLORS["BACKGROUND"],
            fg=HMI_COLORS["FOREGROUND"],
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_baud = tk.Entry(
            frame, bg="#3E3E42", fg="#FFFFFF", insertbackground="white"
        )
        self.entry_baud.insert(0, str(CONSTANTS.get("DEFAULT_BAUDRATE", "")))
        self.entry_baud.grid(row=1, column=1, sticky="ew", pady=5)

        # Motion History Length
        tk.Label(
            frame,
            text="Motion History:",
            bg=HMI_COLORS["BACKGROUND"],
            fg=HMI_COLORS["FOREGROUND"],
            font=("Segoe UI", 10),
        ).grid(row=2, column=0, sticky="w", pady=5)
        self.spin_motion = tk.Spinbox(
            frame,
            from_=10,
            to=1000,
            bg="#3E3E42",
            fg="#FFFFFF",
            buttonbackground="#252526",
        )
        self.spin_motion.delete(0, "end")
        self.spin_motion.insert(0, CONSTANTS.get("MOTION_HISTORY_LENGTH", 50))
        self.spin_motion.grid(row=2, column=1, sticky="ew", pady=5)

        # Logs History Length
        tk.Label(
            frame,
            text="Logs History:",
            bg=HMI_COLORS["BACKGROUND"],
            fg=HMI_COLORS["FOREGROUND"],
            font=("Segoe UI", 10),
        ).grid(row=3, column=0, sticky="w", pady=5)
        self.spin_logs = tk.Spinbox(
            frame,
            from_=5,
            to=500,
            bg="#3E3E42",
            fg="#FFFFFF",
            buttonbackground="#252526",
        )
        self.spin_logs.delete(0, "end")
        self.spin_logs.insert(0, CONSTANTS.get("LOGS_HISTORY_LENGTH", 10))
        self.spin_logs.grid(row=3, column=1, sticky="ew", pady=5)

        # Use Mock Data
        self.var_mock = tk.BooleanVar(value=CONSTANTS.get("USE_MOCK_DATA", False))
        self.check_mock = tk.Checkbutton(
            frame,
            text="Use Mock Data",
            variable=self.var_mock,
            bg=HMI_COLORS["BACKGROUND"],
            fg=HMI_COLORS["FOREGROUND"],
            selectcolor="#252526",
            activebackground=HMI_COLORS["BACKGROUND"],
            activeforeground=HMI_COLORS["FOREGROUND"],
            font=("Segoe UI", 10),
        )
        self.check_mock.grid(row=4, column=0, columnspan=2, sticky="w", pady=10)

        # -----------------------------
        # Advanced Settings
        # -----------------------------

        # Device Version (Control Station)
        tk.Label(
            frame,
            text="Station Version:",
            bg=HMI_COLORS["BACKGROUND"],
            fg=HMI_COLORS["FOREGROUND"],
            font=("Segoe UI", 10),
        ).grid(row=5, column=0, sticky="w", pady=5)
        self.entry_version = tk.Entry(
            frame, bg="#3E3E42", fg="#FFFFFF", insertbackground="white"
        )
        dev_ver = CONSTANTS.get("DEVICE_VERSION", {}).get("control_station", "")
        self.entry_version.insert(0, dev_ver)
        self.entry_version.grid(row=5, column=1, sticky="ew", pady=5)

        # Message Types (Editable Keys)
        tk.Label(
            frame,
            text="Message Types:",
            bg=HMI_COLORS["BACKGROUND"],
            fg=HMI_COLORS["FOREGROUND"],
            font=("Segoe UI", 10, "bold"),
        ).grid(row=6, column=0, sticky="w", pady=(10, 5))

        self.msg_type_entries = {}
        msg_types = CONSTANTS.get("MESSAGE_TYPES", {})
        row_idx = 7
        for key, val in msg_types.items():
            tk.Label(
                frame,
                text=f"{key}:",
                bg=HMI_COLORS["BACKGROUND"],
                fg=HMI_COLORS["FOREGROUND"],
                font=("Segoe UI", 9),
            ).grid(row=row_idx, column=0, sticky="e", pady=2)

            entry = tk.Entry(
                frame, bg="#3E3E42", fg="#FFFFFF", insertbackground="white"
            )
            entry.insert(0, val)
            entry.grid(row=row_idx, column=1, sticky="ew", pady=2)
            self.msg_type_entries[key] = entry
            row_idx += 1

        # Buttons
        btn_frame = tk.Frame(frame, bg=HMI_COLORS["BACKGROUND"])
        btn_frame.grid(row=row_idx, column=0, columnspan=2, pady=20)

        tk.Button(
            btn_frame,
            text="Save",
            command=self.save_preferences,
            bg=HMI_COLORS["PRIMARY"],
            fg="white",
            width=10,
            relief="flat",
        ).pack(side="left", padx=10)
        tk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            bg=HMI_COLORS["DANGER"],
            fg="white",
            width=10,
            relief="flat",
        ).pack(side="left", padx=10)

        # frame.columnconfigure(1, weight=1)

    def save_preferences(self):
        full_settings = SettingsManager.load_settings()
        constants_settings = full_settings.get("CONSTANTS", {})

        # Validation could be added here
        constants_settings["DEFAULT_SERIAL_PORT"] = self.entry_port.get()

        try:
            constants_settings["DEFAULT_BAUDRATE"] = int(self.entry_baud.get())
        except ValueError:
            messagebox.showerror("Error", "Baudrate must be an integer.")
            return

        try:
            constants_settings["MOTION_HISTORY_LENGTH"] = int(self.spin_motion.get())
        except ValueError:
            messagebox.showerror("Error", "Motion History must be an integer.")
            return

        try:
            constants_settings["LOGS_HISTORY_LENGTH"] = int(self.spin_logs.get())
        except ValueError:
            messagebox.showerror("Error", "Logs History must be an integer.")
            return

        constants_settings["USE_MOCK_DATA"] = self.var_mock.get()

        # Advanced settings
        if "DEVICE_VERSION" not in constants_settings:
            constants_settings["DEVICE_VERSION"] = {}
        constants_settings["DEVICE_VERSION"]["control_station"] = (
            self.entry_version.get()
        )

        if "MESSAGE_TYPES" not in constants_settings:
            constants_settings["MESSAGE_TYPES"] = {}

        for key, entry in self.msg_type_entries.items():
            constants_settings["MESSAGE_TYPES"][key] = entry.get()

        full_settings["CONSTANTS"] = constants_settings

        if SettingsManager.save_settings(full_settings):
            messagebox.showinfo(
                "Success",
                "Preferences saved. Please restart the application for changes to take effect.",
            )
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to save preferences.")
