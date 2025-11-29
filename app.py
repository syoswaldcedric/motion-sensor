from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QToolButton, QStackedWidget, QLabel
from PySide6.QtCore import QTimer, QObject, QDateTime
import sys
import os

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
        self.date_time_label= None
        self.show_main_screen()

         # Timer: call update_time() every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)   # 1000 ms = 1 second

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
    
    def set_current_property(self, index):
        if self.property_stack:
            self.property_stack.setCurrentIndex(index)
        else:
            print("Error: 'property_stack' not found in main_screen.ui")

    def show_main_screen(self):
        # Load the main_screen.ui
        ui_file = self.get_file_path("main_screen.ui")
        self.main_screen = self.loader.load(ui_file)

        self.main_screen.show()
        # if self.on_off_screen:
        #     self.on_off_screen.hide()  # keep screen hidden for back navigation

           # Find propert buttons
        self.plot_btn = self.main_screen.findChild(QToolButton, "plot_btn")
        self.performance_btn = self.main_screen.findChild(QToolButton, "performance_btn")   
        self.status_btn = self.main_screen.findChild(QToolButton, "status_btn")
        self.date_time_label = self.main_screen.findChild(QLabel, "date_time_label")
        
        # Find property stack
        self.property_stack = self.main_screen.findChild(QStackedWidget, "property_stack")
        # Find screen stack
        self.screen_stack = self.main_screen.findChild(QStackedWidget, "screen_stack")
        if not self.screen_stack:
            print("Error: 'screen_stack' not found in main_screen.ui")
        if self.property_stack:
            if self.plot_btn:
                self.plot_btn.clicked.connect(lambda: self.set_current_property(0))
            if self.performance_btn:
                self.performance_btn.clicked.connect(lambda: self.set_current_property(1))
            if self.status_btn:
                self.status_btn.clicked.connect(lambda: self.set_current_property(2))
                self.property_stack.setCurrentIndex(0)
        else:
            print("Error: 'property_stack' not found in main_screen.ui")    
        
        # Find the power buttons and connect the click event
        self.power_off_btn = self.main_screen.findChild(QToolButton, "power_off_btn")
        self.power_on_btn = self.main_screen.findChild(QToolButton, "power_on_btn")
        if self.power_off_btn:
            # self.power_off_btn.clicked.connect(self.show_on_off_screen)
            self.power_off_btn.clicked.connect(lambda: self.screen_stack.setCurrentIndex(0))
        else:
            print("Error: 'power_off_btn' not found in main_screen.ui")
        if self.power_on_btn:
            self.power_on_btn.clicked.connect(lambda: self.screen_stack.setCurrentIndex(1))
        else:
            print("Error: 'power_on_btn' not found in main_screen.ui")

    def update_time(self):
        current_time = QDateTime.currentDateTime()
        time_text = current_time.toString("yyyy-MM-dd hh:mm:ss")
        self.date_time_label.setText(time_text)

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    motion_app = MotionSensorApp()
    motion_app.run()
