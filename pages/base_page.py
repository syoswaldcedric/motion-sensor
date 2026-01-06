import tkinter as tk

# -----------------------------
# Base page
# -----------------------------


class BasePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1e1e1e")
        self.controller = controller

    def update_data(self, metrics, motion_series):
        """
        Called every second by the controller.
        Child classes override this method.
        """
        pass
