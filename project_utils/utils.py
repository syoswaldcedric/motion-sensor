from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Frame

x = [1, 2, 3, 4, 5]


def plot_graph(
    parent: Frame,
    x_label: str = "X Label",
    y_label: str = "Y Label",
    values: list[float] = x,
) -> Frame:
    # Create a Matplotlib figure
    plot_frame = Frame(parent)
    fig = Figure(figsize=(5, 4), dpi=100)
    plot1 = fig.add_subplot(111)

    # Sample plot
    # y = [10, 5, 8, 12, 7]
    plot1.plot(values)
    plot1.set_xlabel(x_label)
    plot1.set_ylabel(y_label)

    # Put the figure into Tkinter canvas
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    return plot_frame
