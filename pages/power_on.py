from tkinter import ttk
from .base_page import BasePage

# import project metadata
from metadata import CONSTANTS


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
