from core.system_monitor import SystemMonitor
from gui.main_window import MainWindow

if __name__ == "__main__":
    monitor = SystemMonitor()
    app = MainWindow(monitor)
    app.run()
