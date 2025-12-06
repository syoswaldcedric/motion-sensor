import time
from tkinter import (
    Scrollbar,
    Listbox,
    PhotoImage,
    RIGHT,
    StringVar,
    Label,
    Button,
    LEFT,
    Y,
    BOTH,
    END,
    Tk,
    Menu,
    mainloop,
    Frame,
    PhotoImage,
)


class MotionSensorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Motion Sensor Application")
        self.icon = PhotoImage(file="./assets/graph.png")
        self.root.iconphoto(True, self.icon)
        self.root.resizable(False, False)

        self.window_width = 800
        self.window_height = 600
        self.center_window(self.window_width, self.window_height)
        self.root.minsize(1000, 600)

        # Create a frame to hold widgets
        self.frame = Frame(root)
        self.frame.pack(fill=BOTH, expand=True)

        # create the menu
        self.menu = Menu(self.root, tearoff=0)  # tearoff=0 to disable dashed line
        filemenu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=filemenu)

        filemenu.add_command(label="New")
        filemenu.add_command(label="Open...")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)

        helpmenu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About")

        self.root.config(menu=self.menu)
        self.on_off_frame = Frame(self.frame)
        self.main_frame = Frame(self.frame)

        self.tab_list = [
            {"name": "plot", "icon": PhotoImage(file="./assets/graph.png")},
            {
                "name": "performance",
                "icon": PhotoImage(file="./assets/performance.png"),
            },
            {"name": "status", "icon": PhotoImage(file="./assets/status.png")},
        ]

        # image references
        self.light_off_img = PhotoImage(file="./assets/light_off.png")
        self.light_on_img = PhotoImage(file="./assets/light_on.png")
        self.power_img = PhotoImage(file="./assets/power_btn_lg.png")
        self.power_img_sm = PhotoImage(file="./assets/power_btn.png")

        # Variables
        # allows easy access to the light status
        self.light_status = StringVar()
        self.light_status.set("LIGHT OFF")

        self.date_time_var = StringVar()
        self.date_time_var.set("06:12:2025 00:00:00")

        # build all the screens
        self.build_on_off_screen()
        self.build_main_screen()

        # show the on_off_screen
        self.show_screen(self.on_off_frame)

        # start date_time_update
        self.root.after(1000, self.date_time_update)  # call again in 1 second

    def show_screen(self, new_frame):
        if new_frame == self.on_off_frame:
            self.main_frame.pack_forget()
            self.on_off_frame.pack(fill=BOTH, expand=True)
        elif new_frame == self.main_frame:
            self.on_off_frame.pack_forget()
            self.main_frame.pack(fill=BOTH, expand=True)

    def build_on_off_screen(self):
        frame = Frame(self.on_off_frame)
        frame.pack(fill=BOTH, expand=True)

        btn = Button(
            frame,
            image=self.power_img,
            # command=self.show_main_screen,
            command=lambda: self.show_screen(self.main_frame),
            # command=lambda: self.on_off_frame.pack_forget(),
            bd=0,
            highlightthickness=0,
            relief="flat",
            text="POWER ON",
            bg=self.frame.cget("bg"),  # match parent's bg color
            activebackground=self.frame.cget("bg"),
            cursor="hand2",
            compound="top",
            pady=15,
            fg="blue",  # Text color
            activeforeground="blue",
            font=("Arial", 22, "bold"),
        )
        btn.pack(expand=True)

    def build_main_screen(self):
        # Add widgets in a grid
        left_frame = Frame(self.main_frame)
        right_frame = Frame(self.main_frame)

        # left side widgets
        left_frame.place(relx=0, rely=0, relwidth=0.4, relheight=1)
        right_frame.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

        left_top_frame = Frame(left_frame)
        left_top_frame.place(relx=0, rely=0, relwidth=1, relheight=0.25)

        # timer
        time_label = Label(
            left_top_frame,
            textvariable=self.date_time_var,
            font=("Arial", 12, "bold"),
            fg="blue",  # Text color
        )
        time_label.pack(expand=True, fill="x")

        tabs_frame = Frame(left_top_frame)
        tabs_frame.pack(expand=True)

        for index, tab in enumerate(self.tab_list):
            btn = Button(
                tabs_frame,
                text=tab["name"].capitalize(),
                image=tab["icon"],
                relief="raised",
                activebackground=self.frame.cget("bg"),
                cursor="hand2",
                compound="top",
                # pady=5,
                fg="blue",  # Text color
                activeforeground="blue",
                font=("Arial", 16, "normal"),
            )
            btn.grid(row=1, column=index, padx=5, pady=5)

        light_frame = Frame(left_frame)
        light_frame.pack(expand=True)

        bulb_label = Label(
            light_frame,
            image=self.light_on_img,
            textvariable=self.light_status,
            relief="flat",
            activebackground=self.frame.cget("bg"),
            compound="top",
            fg="blue",  # Text color
            activeforeground="blue",
            font=("Arial", 20, "bold"),
        )
        bulb_label.pack(expand=True)

        # right side widgets
        power_frame = Frame(right_frame, bg="red")
        power_frame.place(relx=0, rely=0, relwidth=1, relheight=0.3)

        metrics_frame = Frame(right_frame, bg="blue")
        metrics_frame.place(relx=0, rely=0.3, relwidth=1, relheight=0.7)

        power_off_btn = Button(
            power_frame,
            image=self.power_img_sm,
            command=lambda: self.show_screen(self.on_off_frame),
            relief="flat",
            activebackground=self.frame.cget("bg"),
            cursor="hand2",
            compound="top",
            fg="blue",  # Text color
            activeforeground="blue",
        )
        power_off_btn.pack(
            anchor="ne",
            padx=10,
            pady=10,
        )

    def date_time_update(self):
        self.date_time_var.set(time.strftime("%d-%m-%Y %H:%M:%S"))
        self.root.after(1000, self.date_time_update)

    def center_window(self, width, height):
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate position
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Apply geometry
        self.root.geometry(f"{width}x{height}+{x}+{y}")


if __name__ == "__main__":
    root = Tk()
    # create the application
    app = MotionSensorApp(root)
    # start the program
    root.mainloop()
