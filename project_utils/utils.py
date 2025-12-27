from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Frame

y = range(0, 50, 2)
x = range(0, len(y))


def plot_graph(
    parent: Frame,
    x_label: str = "X Label",
    y_label: str = "Y Label",
    values: list[float] = list(y),
) -> Frame:
    # Create a Matplotlib figure
    plot_frame = Frame(parent)
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_xlim(-0.5, max(11.5, len(y) - 0.5))

    ax.plot(x, values)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    # Put the figure into Tkinter canvas
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw_idle()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    return plot_frame
