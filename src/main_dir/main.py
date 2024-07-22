from src.gui.mainGUI import Ui_MainWindow
from src.gui.guiConfig import GuiConfiguration
from src.gui import imagesresources_rc

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QVBoxLayout, QPushButton


# Variables

# methods

def func_message_box(data):
    message, title = data
    dict_icons = {'info': QtWidgets.QMessageBox.Icon.Information,
                  'Warning': QtWidgets.QMessageBox.Icon.Warning,
                  'Error': QtWidgets.QMessageBox.Icon.Critical}
    message_box = QtWidgets.QMessageBox()
    message_box.setWindowTitle(title)
    message_box.setText(message)
    message_box.addButton(QtWidgets.QMessageBox.StandardButton.Ok)
    message_box.setIcon(dict_icons.get(title))
    message_box.exec_()


def func_set_icon(data):
    widget, icon_path = data
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
    widget.setIcon(icon)


def func_set_pixmap(data):
    widget, pixmap = data
    if isinstance(pixmap, str):
        widget.setPixmap(QtGui.QPixmap(pixmap))
    elif isinstance(pixmap, QtGui.QPixmap):
        widget.setPixmap(pixmap)
    else:
        print('Invalid Pixmap')


def func_do_func(data):
    # This for loop is only simple retry
    for _ in range(5):
        try:
            data()
            break
        except Exception as ex:
            print('Ops we have some exception here', ex)
            continue


class Main:
    # Windows & Uis
    main_window: QtWidgets.QWidget
    ui: Ui_MainWindow
    gui_config: GuiConfiguration

    def __init__(self, platform: str, version: str):
        self.platform = platform
        self.version = version

        # Threads and Workers

        # Do some functions
        self.open_main_window()

        # gui

    def open_main_window(self):
        self.gui_config = GuiConfiguration(Ui_MainWindow, self.platform, True)
        self.main_window = self.gui_config.window
        self.ui: Ui_MainWindow = self.gui_config.ui
        self.main_window.show()

        self.ui_main_events()

    def ui_main_events(self):
        pass
