from tkinter import Frame, Label


class DashboardFrame(Frame):
    def __init__(self, parent, app_styles):
        super().__init__(parent, bg=parent.cget("bg"))
        self.app_styles = app_styles
        self.widgets = {}
        self.frame_id = "performance"

    def update_metrics(self, data):
        """
        Update widgets with new data.
        data: dict { "CPU": "val;total;unit", ... }
        """
        cols = 2
        keys = list(data.keys())

        for index, key in enumerate(keys):
            if key not in self.widgets:
                row = index // cols
                col = index % cols
                self._create_widget(key, row, col)

            # Parse value
            raw_val = data[key]
            used, total, unit = raw_val.split(";")

            # Update Text
            self.widgets[key]["value_label"].config(text=f"{used} {unit}")

            # Update Color (simple logic)
            try:
                # CPU is 0-100, RAM/Disk we need to calc %
                if unit == "%":
                    percent = float(used)
                else:
                    percent = (float(used) / float(total)) * 100

                color = "green"
                if percent > 30:
                    color = "blue"
                if percent > 70:
                    color = "red"

                self.widgets[key]["value_label"].config(fg=color)
            except ValueError:
                pass

    def _create_widget(self, label, row, col):
        frame = Frame(self, bd=5, relief="raised")
        frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)

        # Configure grid expansion
        self.grid_columnconfigure(col, weight=1, minsize=150)
        self.grid_rowconfigure(row, weight=1, minsize=100)

        # Labels
        lbl_title = Label(
            frame, text=label.upper(), fg="blue", font=("Arial", 10, "bold")
        )
        lbl_title.pack(expand=True, anchor="center")

        lbl_value = Label(frame, text="--", fg="green", font=("Arial", 14, "normal"))
        lbl_value.pack(expand=True, fill="both", anchor="center")

        self.widgets[label] = {"frame": frame, "value_label": lbl_value}
