import tkinter as tk
# from tkinter import ttk


def CustomMessageBox(title, frame, message):
    win = tk.Toplevel()
    win.title(title)
    win.resizable(False, False)

    label = tk.Label(win, text=message, font=("Arial", 9))
    label.pack(pady=10)

    tk.Button(win, text="OK", command=win.destroy).pack(pady=(0, 10))

    win.transient()
    win.grab_set()
    win.wait_window()
