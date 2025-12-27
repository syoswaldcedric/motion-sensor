import time
import pandas as pd
from tkinter import (
    Tk,
    Frame,
    Menu,
    PhotoImage,
    font,
    filedialog,
    messagebox,
    BOTH,
    StringVar,
    Button,
    Label,
)
from gui.frames.welcome_frame import WelcomeFrame
from gui.frames.dashboard_frame import DashboardFrame
from gui.frames.graph_frame import GraphFrame
from gui.frames.status_frame import StatusFrame
from metadata import metadata  # Assuming run from root


class MainWindow:
    def __init__(self, system_monitor):
        self.root = Tk()
        self.monitor = system_monitor
        self.root.title(metadata["name"])
        try:
            self.icon = PhotoImage(file="./assets/graph.png")
            self.root.iconphoto(True, self.icon)
        except Exception:
            pass  # Icon might be missing

        self.root.resizable(False, False)

        self.window_width = 800
        self.window_height = 600
        self._center_window(self.window_width, self.window_height)

        # Styles / Resources
        self._load_styles_and_assets()

        # UI Setup
        self.main_container = Frame(self.root)
        self.main_container.pack(fill=BOTH, expand=True)

        self._setup_menu()

        # State
        self.current_frame = None
        self.active_tab_var = StringVar(value="Performance")
        self.active_tab_var.trace_add("write", self._on_tab_change)

        # Build Frames
        self.welcome_frame = WelcomeFrame(
            self.main_container, self.show_main_interface, self.images
        )
        self.app_interface = self._build_app_interface()

        # Start
        self.show_welcome_screen()

        # Update Loop
        self.root.after(1000, self._update_loop)

    def run(self):
        self.root.mainloop()

    def _load_styles_and_assets(self):
        self.label_style = {
            "relief": "flat",
            "compound": "top",
            "fg": "blue",
            "activeforeground": "blue",
            "font": font.Font(
                family="Helvetica", size=12, weight="bold", underline=True
            ),
        }

        # Load Images (Safe load)
        self.images = {}
        assets = [
            ("graph", "./assets/graph.png"),
            ("performance", "./assets/performance.png"),
            ("status", "./assets/status.png"),
            ("power_lg", "./assets/power_btn_lg.png"),
            ("power_sm", "./assets/power_btn.png"),
            ("light_on", "./assets/light_on_md.png"),
        ]
        for name, path in assets:
            try:
                self.images[name] = PhotoImage(file=path)
            except:
                print(f"Warning: Could not load {path}")
                self.images[name] = None

    def _setup_menu(self):
        menubar = Menu(self.root, tearoff=0)
        filemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Save", command=self._save_data)
        filemenu.add_command(label="View Saved File", command=self._view_saved_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)

        helpmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About", command=self._show_about)

        self.root.config(menu=menubar)

    def _build_app_interface(self):
        """
        Constructs the main app interface (sidebar + content area)
        Returns the container Frame.
        """
        container = Frame(self.main_container)

        # Layout
        left_frame = Frame(container)
        left_frame.place(relx=0, rely=0, relwidth=0.4, relheight=1)

        right_frame = Frame(container, bg="white")
        right_frame.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

        # Left Side Content
        self._build_sidebar(left_frame)

        # Right Side Content (Header + Tab Content)
        # Header (Power btn + Current Tab Label)
        header_frame = Frame(right_frame, bg=right_frame.cget("bg"))
        header_frame.place(relx=0, rely=0, relwidth=1, relheight=0.2)

        Button(
            header_frame,
            image=self.images["power_sm"],
            command=self.show_welcome_screen,
            relief="flat",
            bg=right_frame.cget("bg"),
            bd=0,
            cursor="hand2",
        ).pack(anchor="ne", padx=10, pady=10)

        Label(
            header_frame,
            textvariable=self.active_tab_var,
            bg=right_frame.cget("bg"),
            **self.label_style,
        ).pack(expand=True, anchor="center")

        # Content Area for Tabs
        self.content_area = Frame(right_frame, bg=right_frame.cget("bg"))
        self.content_area.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)

        # Initialize Frames
        self.frames = {
            "Performance": DashboardFrame(self.content_area, self.label_style),
            "Plot": GraphFrame(self.content_area),
            "Status": StatusFrame(self.content_area, self.label_style),
        }

        return container

    def _build_sidebar(self, parent):
        top_section = Frame(parent)
        top_section.place(
            relx=0, rely=0, relwidth=1, relheight=0.3
        )  # Increased height for tabs

        # Time
        self.time_var = StringVar()
        Label(
            top_section,
            textvariable=self.time_var,
            font=("Arial", 12, "bold"),
            fg="blue",
        ).pack(fill="x", pady=5)

        # Navigation Tabs
        nav_frame = Frame(top_section)
        nav_frame.pack(expand=True, fill="both", padx=5)

        tabs = [("Plot", "graph"), ("Performance", "performance"), ("Status", "status")]
        for idx, (name, icon_key) in enumerate(tabs):
            btn = Button(
                nav_frame,
                text=name,
                image=self.images[icon_key],
                compound="top",
                command=lambda n=name: self.active_tab_var.set(n),
                font=("Helvetica", 10, "bold"),
                fg="blue",
            )
            btn.grid(row=0, column=idx, sticky="nsew", padx=2)
            nav_frame.grid_columnconfigure(idx, weight=1)

        # Light Bulb Image
        bottom_section = Frame(parent)
        bottom_section.place(relx=0, rely=0.3, relwidth=1, relheight=0.7)
        Label(
            bottom_section,
            image=self.images["light_on"],
            text="LIGHT ON",
            compound="top",
            font=("Arial", 20, "bold"),
            fg="blue",
        ).pack(expand=True)

    def show_welcome_screen(self):
        if self.app_interface.winfo_ismapped():
            self.app_interface.pack_forget()
        self.welcome_frame.pack(fill=BOTH, expand=True)

    def show_main_interface(self):
        self.welcome_frame.pack_forget()
        self.app_interface.pack(fill=BOTH, expand=True)
        # Trigger initial tab show
        self._on_tab_change()

    def _on_tab_change(self, *args):
        target = self.active_tab_var.get()
        # Hide all
        for frame in self.frames.values():
            frame.pack_forget()

        if target in self.frames:
            self.frames[target].pack(expand=True, anchor="n", fill=BOTH)

    def _update_loop(self):
        # Update Time
        self.time_var.set(time.strftime("%d-%m-%Y %H:%M:%S"))

        # Get Metrics
        data = self.monitor.get_system_metrics()

        # Update Dashboard
        if "Performance" in self.frames:
            self.frames["Performance"].update_metrics(data)

        # Update Graph
        if "Plot" in self.frames:
            motion_val = data["Motion"].split(";")[0]
            self.frames["Plot"].update_graph(motion_val)

        self.root.after(1000, self._update_loop)

    def _save_data(self):
        history = self.monitor.get_history()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")],
        )
        if file_path:
            try:
                df = pd.DataFrame(history)
                if file_path.endswith(".csv"):
                    df.to_csv(file_path, index=False)
                else:
                    df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", f"Data saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _view_saved_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel/CSV files", "*.xlsx;*.csv")]
        )
        if file_path:
            import os

            try:
                os.startfile(file_path)
            except AttributeError:
                # macOS/Linux support
                import subprocess, sys

                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, file_path])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def _show_about(self):
        messagebox.showinfo(
            f"About {metadata['name']}",
            f"{metadata['description']}\n\nVersion: {metadata['version']}\nAuthors: {', '.join(metadata['authors'])}\nGitHub: {metadata['github_url']}",
        )

    def _center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
