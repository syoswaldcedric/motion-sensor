from tkinter import Frame
from project_utils.utils import plot_graph
# or we can refactor utils, but re-using existing logic is fine for now,
# though we need to update the plot dynamically.
# The existing utils function creates a new Figure every time.
# Better to implement a class here that updates line data.

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class GraphFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=parent.cget("bg"))
        self.frame_id = "plot"
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        (self.line,) = self.ax.plot([], [])

        self.ax.set_xlabel("Time (Ticks)")
        self.ax.set_ylabel("Motion Value")
        self.ax.set_ylim(0, 12)  # Assuming 0-10 value

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.data_points = []

    def update_graph(self, new_value):
        # new_value should be a float/int
        self.data_points.append(float(new_value))
        if len(self.data_points) > 12:
            self.data_points.pop(0)

        x_data = range(len(self.data_points))
        self.line.set_data(x_data, self.data_points)
        self.ax.set_xlim(0, max(11, len(self.data_points) - 1))

        self.canvas.draw()
