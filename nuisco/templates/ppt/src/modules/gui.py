from PySide6.QtWidgets import QWidget, QMainWindow, QApplication
from PySide6.QtCore import Qt, Signal
import sys
from . import link

def gui_init():
    global log
    log = link.log

class TppGui(QMainWindow):
    changed = Signal(str)  # Signal to notify about changes

    def __init__(self, parent=None):
        log(12)
        super().__init__(parent)
        self._data = "Initial Data"
        # Setup the GUI here (widgets, layout, etc.)

    def update_data(self, new_data):
        """Public method to update data and reflect changes in GUI."""
        self._data = new_data
        self.changed.emit(new_data)  # Emit signal when data is updated
        # Update GUI elements here as needed

    def get_data(self):
        """Public method to get current data."""
        return self._data

class MainController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        self.gui = TppGui()
        
        # Connect signals to controller methods
        self.gui.changed.connect(self.on_gui_data_changed)

    def on_gui_data_changed(self, new_data):
        print(f"GUI data changed: {new_data}")
        # Handle GUI data change here

    def start(self):
        self.gui.update_data("New Data from MainController")
        self.gui.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = MainController()
    controller.start()
