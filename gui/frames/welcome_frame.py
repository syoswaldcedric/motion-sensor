from tkinter import Frame, Button, BOTH


class WelcomeFrame(Frame):
    def __init__(self, parent, switch_callback, images):
        super().__init__(parent)
        self.switch_callback = switch_callback
        self.images = images
        self.configure(bg=parent.cget("bg"))
        self._build_ui()

    def _build_ui(self):
        btn = Button(
            self,
            image=self.images["power_lg"],
            command=self.switch_callback,
            bd=0,
            highlightthickness=0,
            relief="flat",
            text="POWER ON",
            bg=self.cget("bg"),
            activebackground=self.cget("bg"),
            cursor="hand2",
            compound="top",
            pady=15,
            fg="blue",
            activeforeground="blue",
            font=("Arial", 22, "bold"),
        )
        btn.pack(expand=True)
