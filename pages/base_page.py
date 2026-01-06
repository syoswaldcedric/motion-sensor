from tkinter import ttk

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
