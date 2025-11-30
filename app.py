from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QToolButton,
    QStackedWidget,
    QLabel,
    QFrame,
    QVBoxLayout,
    QGridLayout,
    QSizePolicy,
)
from PySide6.QtCore import QTimer, QObject, QDateTime, Qt
import sys
import time
import os
import psutil


class MotionSensorApp(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.loader = QUiLoader()
        self.on_off_screen = None
        self.main_screen = None
        self.property_stack = None
        self.screen_stack = None
        self.power_off_btn = None
        self.power_on_btn = None
        self.date_time_label = None
        self.performance_grid = None
        self.properties_monitored = dict()
        self.is_monitoring = False

        self.show_main_screen()

        # Timer: call update_time() every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 1000 ms = 1 second

    def show_on_off_screen(self):
        # Load the on_off_screen.ui
        ui_file = self.get_file_path("on_off_screen.ui")
        self.on_off_screen = self.loader.load(ui_file)

        # Find the power button and connect the click event
        self.power_off_btn = self.on_off_screen.findChild(QToolButton, "power_off_btn")
        if self.power_off_btn:
            self.power_off_btn.clicked.connect(self.show_main_screen)
        else:
            print("Error: 'power_off_btn' not found in on_off_screen.ui")

        self.on_off_screen.show()

    def get_file_path(self, ui_file):
        return os.path.join(os.path.dirname(__file__), ui_file)

    def show_main_screen(self):
        """
        Show the main screen
        Args:
            None
        Returns:
            None
        """
        # Load the main_screen.ui
        ui_file = self.get_file_path("main_screen.ui")
        self.main_screen = self.loader.load(ui_file)

        self.main_screen.show()
        # if self.on_off_screen:
        #     self.on_off_screen.hide()  # keep screen hidden for back navigation

        # Find propert buttons
        self.plot_btn = self.main_screen.findChild(QToolButton, "plot_btn")
        self.performance_btn = self.main_screen.findChild(
            QToolButton, "performance_btn"
        )
        self.status_btn = self.main_screen.findChild(QToolButton, "status_btn")
        self.date_time_label = self.main_screen.findChild(QLabel, "date_time_label")
        self.performance_grid = self.main_screen.findChild(
            QGridLayout, "performance_grid"
        )

        # Find property stack
        self.property_stack = self.main_screen.findChild(
            QStackedWidget, "property_stack"
        )
        # Find screen stack
        self.screen_stack = self.main_screen.findChild(QStackedWidget, "screen_stack")
        if not self.screen_stack:
            print("Error: 'screen_stack' not found in main_screen.ui")
        if self.performance_grid:
            system_usage = self.get_system_usage()
            cols = 2
            for index, (key, value) in enumerate(system_usage.items()):
                row = index // cols
                col = index % cols
                performance = self.create_performance_widget(key, value)
                self.performance_grid.addWidget(performance, row, col)
            # set is_monitoring to True
            self.is_monitoring = True
        else:
            print("Error: 'performance_grid' not found in main_screen.ui")
        if self.property_stack:
            if self.plot_btn:
                self.plot_btn.clicked.connect(
                    lambda: self.property_stack.setCurrentIndex(0)
                )
            if self.performance_btn:
                self.performance_btn.clicked.connect(
                    lambda: self.property_stack.setCurrentIndex(1)
                )
            if self.status_btn:
                self.status_btn.clicked.connect(
                    lambda: self.property_stack.setCurrentIndex(2)
                )
        else:
            print("Error: 'property_stack' not found in main_screen.ui")

        # Find the power buttons and connect the click event
        self.power_off_btn = self.main_screen.findChild(QToolButton, "power_off_btn")
        self.power_on_btn = self.main_screen.findChild(QToolButton, "power_on_btn")
        if self.power_off_btn:
            # self.power_off_btn.clicked.connect(self.show_on_off_screen)
            self.power_off_btn.clicked.connect(
                lambda: self.screen_stack.setCurrentIndex(0)
            )
        else:
            print("Error: 'power_off_btn' not found in main_screen.ui")
        if self.power_on_btn:
            self.power_on_btn.clicked.connect(
                lambda: self.screen_stack.setCurrentIndex(1)
            )
        else:
            print("Error: 'power_on_btn' not found in main_screen.ui")

    def update_time(self):
        """
        Update the time
        Args:
            None
        Returns:
            None
        """
        current_time = QDateTime.currentDateTime()
        time_text = current_time.toString("yyyy-MM-dd hh:mm:ss")
        self.date_time_label.setText(time_text)

        if self.is_monitoring:
            self.update_properties()

    def update_properties(self):
        """
        Update the properties
        Args:
            None
        Returns:
            None
        """
        system_usage = self.get_system_usage()

        for key, value in system_usage.items():
            used, total, unit = value.split(";")
            performance = self.properties_monitored[key]
            performance.setText(f"{used} {unit}")
            # calculate the percentage used
            percent_used = (float(used) / float(total)) * 100
            very_good_condition = percent_used <= 30
            good_condition = percent_used > 30 and percent_used <= 69
            performance.setStyleSheet(
                f"color: {'green' if very_good_condition else 'blue' if good_condition else 'red'};"
            )

    def get_system_usage(self):
        """
        Get the system usage
        Args:
            None
        Returns:
            dict: The system usage with the format:
                {
                    "key": "used;total;unit",
                    "cpu": "used;100%;%",
                }
        """
        # CPU usage
        cpu_percent = psutil.cpu_percent(
            interval=0
        )  # interval=0 for instant usage (non blocking main thread)
        # cpu_freq = psutil.cpu_freq()

        # RAM usage
        ram = psutil.virtual_memory()

        # Disk usage (root partition)
        disk = psutil.disk_usage("/")

        return {
            # "ram": f"{round(ram.used / (1024**3), 2)}/{round(ram.total / (1024**3), 2)}",
            "ram": f"{round(ram.used / (1024**3), 2)};{round(ram.total / (1024**3), 2)};GB",
            # "Memory": f"{round(disk.used / (1024**3), 2)}/{round(disk.total / (1024**3), 2)}",
            "Memory": f"{round(disk.used / (1024**3), 2)};{round(disk.total / (1024**3), 2)};GB",
            "cpu": f"{cpu_percent};100;%",
        }

    def create_performance_widget(self, label, value):
        """
        Create a performance widget at runtime
        Args:
            label (str): The label of the performance widget
            value (str): The value of the performance widget
        Returns:
            QFrame: The performance widget
                children Widget:
                    performance_label (QLabel): The label of the performance widget
                    performance_value (QLabel): The value of the performance widget
        """
        # create a frame at runtime
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)  # optional styling
        # Set maximum size
        # frame.setFixedSize(100, 70)
        # Set background color to white
        frame.setStyleSheet("background-color: white; border-radius: 10px;")
        # create label and make it a child of the frame
        performance_label = QLabel(label.upper())
        performance_label.setAlignment(Qt.AlignCenter)
        performance_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        performance_label.setStyleSheet(
            "color: blue; font-weight: bold; font-size: 12px;"
        )
        # create performance value and make it a child of the layout
        performance_value = QLabel(str(value))
        performance_value.setObjectName(label)
        performance_value.setAlignment(Qt.AlignCenter)
        performance_value.setStyleSheet(
            "color: green; font-size: 14px; font-weight: bold;"
            # f"color: {'blue' if int(value) < 70 else 'red'}; font-size: 12px; font-weight: bold;"
        )
        # add performance value to the properties_monitored dictionary
        self.properties_monitored[label] = performance_value
        # (optional) add a layout inside the frame to manage children properly
        frame_layout = QVBoxLayout(frame)
        frame.setFixedSize(100, 70)
        frame_layout.addWidget(performance_label)  # add label to the frame
        frame_layout.addWidget(performance_value)  # add value to the frame
        frame_layout.setAlignment(Qt.AlignCenter)

        return frame

    def run(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    motion_app = MotionSensorApp()
    motion_app.run()
