import tkinter as tk
from .base_page import BasePage

# import project metadata
from metadata import PROJECT_METADATA
from utils import CONSTANTS


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

        frame = tk.Frame(self, bg="#1e1e1e")
        frame.pack(fill="both", expand=True)
        # frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        # frame.columnconfigure(0, weight=1)

        center_frame = tk.Frame(frame, bg="#1e1e1e")
        center_frame.pack(anchor="center", expand=True)

        title = tk.Label(
            center_frame,
            text=PROJECT_METADATA.get("Name", "Motion Sensor HMI"),
            bg="#1e1e1e",
            fg="#ffffff",
            font=("Segoe UI", 14, "bold"),
            justify="center",
        )
        title.pack(anchor="center", pady=15)

        power_button = tk.Button(
            center_frame,
            # image=tk.PhotoImage(file="./assets/power_btn_lg.png"),
            text="POWER ON",
            compound="top",
            font=("Segoe UI", 14, "bold"),
            bg="#333333",
            fg="#ffffff",
            activebackground="#007acc",
            activeforeground="#ffffff",
            command=self._on_power_on_clicked,
        )
        power_button.pack(anchor="center", ipadx=40, ipady=10, expand=True)

    def _on_power_on_clicked(self):
        self.controller.turn_system_on()
        # show toolbar again using stored pack options
        print(getattr(self.controller, "toolbar", None))
        if getattr(self.controller, "toolbar", None):
            # self.controller.toolbar.pack(**self.controller._toolbar_pack_opts)
            self.controller.toolbar.grid(row=0, column=0, sticky="nsew")
        self.controller.show_page("DashboardPage")
