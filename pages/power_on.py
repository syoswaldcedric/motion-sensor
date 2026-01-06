import tkinter as tk
from .base_page import BasePage

# import project metadata
from metadata import CONSTANTS, PROJECT_METADATA


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
        frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        frame.columnconfigure(0, weight=1)

        title = tk.Label(
            frame,
            text=PROJECT_METADATA.get("Name", "Motion Sensor HMI"),
            bg="#1e1e1e",
            fg="#ffffff",
            font=("Segoe UI", 16, "bold"),
            justify="center",
        )
        title.pack(pady=30, anchor="center")

        power_button = tk.Button(
            frame,
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
        power_button.pack(pady=40, ipadx=40, ipady=20)

    def _on_power_on_clicked(self):
        self.controller.turn_system_on()
        # show toolbar again using stored pack options
        if getattr(self.controller, "toolbar", None):
            self.controller.toolbar.pack(**self.controller._toolbar_pack_opts)
        self.controller.show_page("DashboardPage")
