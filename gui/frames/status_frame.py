from tkinter import Frame, Label


class StatusFrame(Frame):
    def __init__(self, parent, app_styles):
        super().__init__(parent, bg=parent.cget("bg"))
        self.frame_id = "status"

        Label(
            self, text="Project Status: Active", bg=parent.cget("bg"), **app_styles
        ).pack(expand=True, anchor="center")

        Label(
            self,
            text="Connection: Simulated",
            bg=parent.cget("bg"),
            fg="gray",
            font=("Arial", 10),
        ).pack(ipady=10)
