from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QToolButton, QStackedWidget
import sys
import os

class MotionSensorApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.loader = QUiLoader()
        self.on_off_screen = None
        self.main_screen = None
        self.property_stack = None

        self.show_on_off_screen()

    def show_on_off_screen(self):
        # Load the on_off_screen.ui
        ui_file = self.get_file_path("on_off_screen.ui")
        self.on_off_screen = self.loader.load(ui_file)
        
        # Find the power button and connect the click event
        self.power_btn = self.on_off_screen.findChild(QToolButton, "power_btn")
        if self.power_btn:
            self.power_btn.clicked.connect(self.show_main_screen)
        else:
            print("Error: 'power_btn' not found in on_off_screen.ui")

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
        if self.on_off_screen:
            self.on_off_screen.hide()  # keep screen hidden for back navigation

           # Find propert buttons
        plot_btn = self.main_screen.findChild(QToolButton, "plot_btn")
        performance_btn = self.main_screen.findChild(QToolButton, "performance_btn")   
        status_btn = self.main_screen.findChild(QToolButton, "status_btn")
        
        # Find property stack
        self.property_stack = self.main_screen.findChild(QStackedWidget, "property_stack")
        if self.property_stack:
            if plot_btn:
                plot_btn.clicked.connect(lambda: self.set_current_property(0))
            if performance_btn:
                performance_btn.clicked.connect(lambda: self.set_current_property(1))
            if status_btn:
                status_btn.clicked.connect(lambda: self.set_current_property(2))
                self.property_stack.setCurrentIndex(0)
        else:
            print("Error: 'property_stack' not found in main_screen.ui")    
        
        # Find the power button and connect the click event
        self.power_btn = self.main_screen.findChild(QToolButton, "power_btn")
        if self.power_btn:
            self.power_btn.clicked.connect(self.show_on_off_screen)
        else:
            print("Error: 'power_btn' not found in main_screen.ui")

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    motion_app = MotionSensorApp()
    motion_app.run()
