from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

from src.gui.mainGUI import Ui_MainWindow
from src.gui.joystick_widget import Joystick
from src.gui.analog_gauge import AnalogGaugeWidget


# methods
def func_set_icon(data):
    widget, icon_path = data
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
    widget.setIcon(icon)


class ValueChangedEvent:
    def __init__(self):
        self._value = None
        self._handlers = set()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value != self._value:
            self._value = new_value
            for handler in self._handlers:
                handler(new_value)

    def connect(self, handler):
        self._handlers.add(handler)

    def disconnect(self, handler):
        self._handlers.discard(handler)


class GuiConfiguration:
    p_size: float = 1.0
    saved_social_btn_icon_size: QtCore.QSize
    side_menu: bool = False
    _loading: bool = False

    # other classes

    # Icons PATHS...

    # Special Variables
    dict_actions_page_config: dict = {'socials': [], 'state': ''}

    def __init__(self, ui, platform: str, is_main_window: bool = False, args=None):
        self.platform = platform
        self.window = QtWidgets.QWidget()
        self.ui = Ui_MainWindow()
        if not args:
            self.ui.setupUi(self.window)
        else:
            self.ui.setupUi(self.window, args)
        if platform == 'MAC':
            self.p_size = 1.5
            self.setup_font_point_size(self.window.findChildren(QtWidgets.QLabel))
            self.setup_font_point_size(self.window.findChildren(QtWidgets.QPushButton))
            self.setup_font_point_size(self.window.findChildren(QtWidgets.QCheckBox))
            self.setup_font_point_size(self.window.findChildren(QtWidgets.QRadioButton))
            self.setup_font_point_size(self.window.findChildren(QtWidgets.QLineEdit))
            self.setup_font_point_size(self.window.findChildren(QtWidgets.QPlainTextEdit))
            self.setup_font_point_size(self.window.findChildren(QtWidgets.QComboBox))
        elif platform == 'WINDOWS':
            pass
        elif platform == 'LINUX':
            pass
        self.remove_focus_policy(self.window.findChildren(QtWidgets.QPushButton))
        self.remove_focus_policy(self.window.findChildren(QtWidgets.QCheckBox))
        self.remove_focus_policy(self.window.findChildren(QtWidgets.QRadioButton))

        if is_main_window:
            # Workers & Threads

            # Normal Variables
            self.animation = QtCore.QPropertyAnimation(self.ui.frameLeftMenu, b"minimumWidth")
            self.animation_spacing = QtCore.QPropertyAnimation(self.ui.horizontalLayout_4, b"spacing")

            # Special Variables
            self.screen_events()

    def setup_font_point_size(self, parent):
        for child in parent:
            font = child.font()
            font.setPointSize(int(font.pointSize() * self.p_size))
            child.setFont(font)

    @staticmethod
    def remove_focus_policy(parent):
        for child in parent:
            child.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    @staticmethod
    def remove_pages_style_sheet(btn: QtWidgets.QPushButton):
        btn.setStyleSheet('')

    @staticmethod
    def setup_pages_style_sheet(btn: QtWidgets.QPushButton):
        btn.setStyleSheet(
            '''background-color: #343b47; border-top-left-radius: 12px; border-bottom-left-radius: 12px;''')

    def side_menu_coll_exp(self):
        try:

            width = self.ui.frameLeftMenu.width()
            width_spacer = self.ui.horizontalLayout_4.spacing()
            width_extended = 75
            width_extended_spacer = 0

            # SET MAX WIDTH
            if width == 75:
                width_extended = 205
            if width_spacer == 0:
                width_extended_spacer = 75

            # ANIMATION
            self.animation.setDuration(500)
            self.animation.setStartValue(width)
            self.animation.setEndValue(width_extended)
            self.animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuart)
            self.animation.start()

            self.animation_spacing.setDuration(500)
            self.animation_spacing.setStartValue(width_spacer)
            self.animation_spacing.setEndValue(width_extended_spacer)
            self.animation_spacing.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuart)
            self.animation_spacing.start()

        except Exception as ex:
            print(ex)

    def screen_change_buttons_clicked(self):
        sender = self.window.sender()
        dict_sender: dict = {self.ui.btnGaugesScreen: 0,
                             self.ui.btnGoToPositionScreen: 1,
                             self.ui.btnReportsScreen: 2,
                             self.ui.btnSettingScreen: 3,
                             self.ui.btnHelpScreen: 4}

        self.page = dict_sender.get(sender, self.page)

    def screen_events(self):
        # Events
        self.ui.btnSideMenu.clicked.connect(self.side_menu_coll_exp)
        # Main Stacked Widget Pages Changing...
        self.ui.btnGaugesScreen.clicked.connect(lambda: self.screen_change_buttons_clicked())
        self.ui.btnGoToPositionScreen.clicked.connect(lambda: self.screen_change_buttons_clicked())
        self.ui.btnReportsScreen.clicked.connect(lambda: self.screen_change_buttons_clicked())
        self.ui.btnSettingScreen.clicked.connect(lambda: self.screen_change_buttons_clicked())
        self.ui.btnHelpScreen.clicked.connect(lambda: self.screen_change_buttons_clicked())
        # Gui
        # Main Pages Animation
        self.ui.swMain.setTransitionDirection(Qt.Horizontal)
        self.ui.swMain.setTransitionSpeed(450)
        self.ui.swMain.setTransitionEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.ui.swMain.setSlideTransition(True)
        self.ui.swMain.setFadeSpeed(450)
        self.ui.swMain.setFadeCurve(QtCore.QEasingCurve.InOutQuart)
        self.ui.swMain.setFadeTransition(True)

        # First View
        self.page = 0

        joystick = Joystick()
        joystick.setCursor(Qt.CursorShape.OpenHandCursor)
        self.ui.v_layout_joystick.setContentsMargins(0, 0, 0, 0)
        self.ui.v_layout_joystick.addWidget(joystick)

        self.ui.gauge_pan = AnalogGaugeWidget(theme=23)
        self.ui.gauge_pan.minValue = -180
        self.ui.gauge_pan.maxValue = 180
        self.ui.gauge_tilt = AnalogGaugeWidget(theme=24)

        self.ui.v_layout_pan_gauge.setContentsMargins(50, 50, 50, 50)
        self.ui.v_layout_tilt_gauge.setContentsMargins(50, 50, 50, 50)

        self.ui.v_layout_pan_gauge.addWidget(self.ui.gauge_pan)
        self.ui.v_layout_tilt_gauge.addWidget(self.ui.gauge_tilt)



    @property
    def page(self):
        return self.ui.swMain.currentIndex()

    @page.setter
    def page(self, value: int):
        dict_sender: dict = {self.ui.btnGaugesScreen: 0,
                             self.ui.btnGoToPositionScreen: 1,
                             self.ui.btnReportsScreen: 2,
                             self.ui.btnSettingScreen: 3,
                             self.ui.btnHelpScreen: 4}
        dict_sender_reverse = {v: k for k, v in dict_sender.items()}
        sender: QtWidgets.QPushButton = dict_sender_reverse.get(value)
        try:

            btn: QtWidgets.QPushButton = dict_sender_reverse.get(self.page)
            print('BTN is ', btn)
            if btn is not None:
                self.remove_pages_style_sheet(btn)
            self.ui.swMain.slideToWidgetIndex(value)
            for keys in dict_sender.keys():
                if keys == sender:
                    self.setup_pages_style_sheet(sender)
                    break

        except Exception as ex:
            print(ex)
