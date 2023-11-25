from PySide6.QtWidgets import (QMessageBox)
from . import link

def clss_init():
    global log
    log = link.log

class AdvancedQMessageBox(QMessageBox):
    def __init__(self, parent=None, icon=None, windowTitle='', text='', detailedText='', 
                 checkbox=None, standardButtons=QMessageBox.Ok, defaultButton=None):
        """
        An advanced QMessageBox with additional configuration options.
        
        :param parent: The parent widget.
        :param icon: The icon to display.
        :param windowTitle: The title of the message box window.
        :param text: The text to display.
        :param detailedText: The detailed text to display.
        :param checkbox: A QCheckBox instance.
        :param standardButtons: The standard buttons to include.
        :param defaultButton: The default button.
        """
        super().__init__(parent)
        if icon: self.setIcon(icon)
        if windowTitle: self.setWindowTitle(windowTitle)
        if text: self.setText(text)
        if detailedText: self.setDetailedText(detailedText)
        if checkbox: self.setCheckBox(checkbox)
        self.setStandardButtons(standardButtons)
        if defaultButton: self.setDefaultButton(defaultButton)
        
