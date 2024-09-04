from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from time import sleep

from src.gui.mainGUI import Ui_MainWindow
from src.gui.joystick_widget import Joystick
from src.gui.analog_gauge import AnalogGaugeWidget
from src.gui.pipeline_gauge import PipelineGauge
from src.gui.range_slider import RangeSlider
from src.threads.worker import WorkerThread
from src.communication.serial_com import Serial


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
            self.thread_main_worker = WorkerThread(self.thread_main)

            # Normal Variables
            self.animation = QtCore.QPropertyAnimation(self.ui.frameLeftMenu, b"minimumWidth")
            self.animation_spacing = QtCore.QPropertyAnimation(self.ui.horizontalLayout_4, b"spacing")

            # Special Variables
            self.screen_events()

            self.thread_main_worker.start()

    def thread_main(self):
        while True:
            try:
                self.update_combobox()

            except Exception as ex:
                _ = ex
            sleep(0.00001)

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
                width_extended = 175
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
        dict_sender: dict = {self.ui.btnGoToPositionScreen: 1,
                             self.ui.btnGaugesScreen: 0,
                             self.ui.btnSettingScreen: 2}

        self.page = dict_sender.get(sender, self.page)

    def screen_events(self):
        # Events
        self.ui.btnSideMenu.clicked.connect(self.side_menu_coll_exp)
        # Main Stacked Widget Pages Changing...
        self.ui.btnGaugesScreen.clicked.connect(lambda: self.screen_change_buttons_clicked())
        self.ui.btnGoToPositionScreen.clicked.connect(lambda: self.screen_change_buttons_clicked())
        self.ui.btnSettingScreen.clicked.connect(lambda: self.screen_change_buttons_clicked())
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
        self.window.setGeometry(QtCore.QRect(0, 0, 1250, 750))
        self.page = 0
        self.ui.frameBufferRx.setMaximumWidth(520)
        self.ui.frameBufferRx.setMinimumWidth(480)
        self.ui.frameBufferTx.setMinimumWidth(320)
        self.ui.frameBufferTx.setMaximumWidth(350)
        self.ui.lblLANDataRecieve.setMaximumWidth(520)

        self.ui.cboxUart.clear()

        self.ui.joystick = Joystick(self.ui.frameJoystick)
        self.ui.joystick.setCursor(Qt.CursorShape.OpenHandCursor)
        self.ui.v_layout_joystick.setContentsMargins(0, 0, 0, 0)
        self.ui.v_layout_joystick.addWidget(self.ui.joystick)

        self.ui.gauge_pan = AnalogGaugeWidget(theme=23)
        self.ui.gauge_tilt = AnalogGaugeWidget(theme=24)
        self.ui.pipeline_temp_pan = PipelineGauge()
        self.ui.pipeline_torque_pan = PipelineGauge()
        self.ui.gauge_pan_speed = AnalogGaugeWidget(theme=23, use_limit=False)
        self.ui.pipeline_temp_tilt = PipelineGauge()
        self.ui.pipeline_torque_tilt = PipelineGauge()
        self.ui.gauge_tilt_speed = AnalogGaugeWidget(theme=24, use_limit=False)

        self.ui.gauge_pan_speed.initial_scale_fontsize = 28
        self.ui.gauge_tilt_speed.initial_scale_fontsize = 28
        self.ui.gauge_pan.initial_scale_fontsize = 23
        self.ui.gauge_tilt.initial_scale_fontsize = 23
        self.ui.gauge_pan_speed.setScalaCount(5)
        self.ui.gauge_tilt_speed.setScalaCount(5)

        # self.ui.v_layout_pan_gauge.setContentsMargins(50, 50, 50, 50)
        # self.ui.v_layout_tilt_gauge.setContentsMargins(50, 50, 50, 50)

        self.ui.v_layout_PAN_Pos_Gauge.addWidget(self.ui.gauge_pan)
        self.ui.v_layout_PAN_Temp_Gauge.addWidget(self.ui.pipeline_temp_pan)
        self.ui.v_layout_PAN_Torque_Gauge.addWidget(self.ui.pipeline_torque_pan)
        self.ui.v_layout_PAN_Speed_Gauge.addWidget(self.ui.gauge_pan_speed)
        self.ui.v_layout_Tilt_Pos_Gauge.addWidget(self.ui.gauge_tilt)
        self.ui.v_layout_Tilt_Temp_Gauge.addWidget(self.ui.pipeline_temp_tilt)
        self.ui.v_layout_Tilt_Torque_Gauge.addWidget(self.ui.pipeline_torque_tilt)
        self.ui.v_layout_Tilt_Speed_Gauge.addWidget(self.ui.gauge_tilt_speed)

        # spacerItem = QtWidgets.QSpacerItem(0, 60, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        # self.ui.verticalLayout_33.addItem(spacerItem)

        # Gauges events
        self.ui.gauge_pan.valueChanged.connect(
            lambda: self.ui.lblPANDegreeValue.setText(f'{format(self.ui.gauge_pan.value, ".3f")}°'))
        self.ui.gauge_pan_speed.valueChanged.connect(
            lambda: self.ui.lblPANSpeedValue.setText(f'{format(self.ui.gauge_pan_speed.value, ".2f")}°/s'))
        self.ui.gauge_tilt.valueChanged.connect(
            lambda: self.ui.lblTiltDegreeValue.setText(f'{format(-self.ui.gauge_tilt.value, ".3f")}°'))
        self.ui.gauge_tilt_speed.valueChanged.connect(
            lambda: self.ui.lblTiltSpeedValue.setText(f'{format(self.ui.gauge_tilt_speed.value, ".2f")}°/s'))

        # Gauges config
        self.ui.gauge_pan.minValue = -180.0
        self.ui.gauge_pan.maxValue = 180.0
        self.ui.gauge_pan.scale_angle_start_value = 90
        self.ui.gauge_pan.scale_angle_size = 360
        self.ui.gauge_pan.updateValue(0.0)
        self.ui.gauge_pan.update()

        self.ui.gauge_tilt.setMinValue(-180.0)
        self.ui.gauge_tilt.setMaxValue(180.0)
        self.ui.gauge_tilt.reverse = True
        self.ui.gauge_tilt.scale_angle_start_value = 180
        self.ui.gauge_tilt.scale_angle_size = 360
        self.ui.gauge_tilt.setScalaCount(8)
        self.ui.gauge_tilt.updateValue(0.0)
        self.ui.gauge_tilt.update()

        self.ui.gauge_pan_speed.minValue = 0.0
        self.ui.gauge_pan_speed.maxValue = 200.0
        self.ui.gauge_pan_speed.updateValue(0.0)
        self.ui.gauge_pan_speed.update()

        self.ui.gauge_tilt_speed.minValue = 0.0
        self.ui.gauge_tilt_speed.maxValue = 100.0
        self.ui.gauge_tilt_speed.updateValue(0.0)
        self.ui.gauge_tilt_speed.update()

        # PipeLines Config
        self.ui.pipeline_temp_pan.min_value = 0
        self.ui.pipeline_temp_pan.max_value = 99
        self.ui.pipeline_torque_pan.min_value = 0
        self.ui.pipeline_torque_pan.max_value = 100

        self.ui.pipeline_temp_tilt.min_value = 0
        self.ui.pipeline_temp_tilt.max_value = 99
        self.ui.pipeline_torque_tilt.min_value = 0
        self.ui.pipeline_torque_tilt.max_value = 100

        # PipeLines Events

        # Plain text to sliders edit Events
        self.ui.txtSpeedPAN.editingFinished.connect(self.plain_text_to_sliders)
        self.ui.txtSpeedTilt.editingFinished.connect(self.plain_text_to_sliders)
        self.ui.txtGotoPositionDegreePAN.editingFinished.connect(self.plain_text_to_sliders)
        self.ui.sliderGotoPositionDegreeTilt_2.editingFinished.connect(self.plain_text_to_sliders)
        self.ui.txtGotoPositionSpeedPAN.editingFinished.connect(self.plain_text_to_sliders)
        self.ui.txtGotoPositionSpeedTilt.editingFinished.connect(self.plain_text_to_sliders)
        self.ui.txtScanSpeed.editingFinished.connect(self.plain_text_to_sliders)
        # Plain text to range sliders edit Events
        self.ui.txtScanPANLow.editingFinished.connect(self.plain_text_to_range_sliders)
        self.ui.txtScanPANHigh.editingFinished.connect(self.plain_text_to_range_sliders)
        self.ui.txtScanTiltLow.editingFinished.connect(self.plain_text_to_range_sliders)
        self.ui.txtScanTiltHigh.editingFinished.connect(self.plain_text_to_range_sliders)
        self.ui.txtLimitClockwisePAN.editingFinished.connect(self.plain_text_to_range_sliders)
        self.ui.txtLimitAntiClockwisePAN.editingFinished.connect(self.plain_text_to_range_sliders)
        self.ui.txtLimitClockwiseTilt.editingFinished.connect(self.plain_text_to_range_sliders)
        self.ui.txtLimitAntiClockwiseTilt.editingFinished.connect(self.plain_text_to_range_sliders)

        # Sliders Events
        # Slider set text events
        self.ui.sliderScanSpeed.valueChanged.connect(
            lambda: self.set_text_for_slider(self.ui.txtScanSpeed, True))
        self.ui.sliderGotoPositionDegreePAN.valueChanged.connect(
            lambda: self.set_text_for_slider(self.ui.txtGotoPositionDegreePAN))
        self.ui.sliderGotoPositionDegreeTilt.valueChanged.connect(
            lambda: self.set_text_for_slider(self.ui.sliderGotoPositionDegreeTilt_2))
        self.ui.sliderGotoPositionSpeedPAN.valueChanged.connect(
            lambda: self.set_text_for_slider(self.ui.txtGotoPositionSpeedPAN, True))
        self.ui.sliderGotoPositionSpeedTilt.valueChanged.connect(
            lambda: self.set_text_for_slider(self.ui.txtGotoPositionSpeedTilt, True))
        self.ui.sliderSpeedPAN.valueChanged.connect(
            lambda: self.set_text_for_slider(self.ui.txtSpeedPAN, True))
        self.ui.sliderSpeedTilt.valueChanged.connect(
            lambda: self.set_text_for_slider(self.ui.txtSpeedTilt, True))
        # Range Slider set text events
        self.ui.sliderScanPAN.sliderMoved.connect(
            lambda: self.set_text_for_range_slider(self.ui.txtScanPANLow, self.ui.txtScanPANHigh))
        self.ui.sliderScanTilt.sliderMoved.connect(
            lambda: self.set_text_for_range_slider(self.ui.txtScanTiltLow, self.ui.txtScanTiltHigh))
        self.ui.sliderLimitClockwisePAN.sliderMoved.connect(
            lambda: self.set_text_for_range_slider(self.ui.txtLimitAntiClockwisePAN, self.ui.txtLimitClockwisePAN))
        self.ui.sliderLimitClockwiseTilt.sliderMoved.connect(
            lambda: self.set_text_for_range_slider(self.ui.txtLimitClockwiseTilt,
                                                   self.ui.txtLimitAntiClockwiseTilt))

        self.ui.sliderLimitClockwisePAN.sliderMoved.connect(lambda: self.limit_slider_to_gauge(self.ui.gauge_pan))
        self.ui.sliderLimitClockwiseTilt.sliderMoved.connect(lambda: self.limit_slider_to_gauge(self.ui.gauge_tilt))
        self.ui.txtLimitClockwisePAN.editingFinished.connect(
            lambda: self.limit_slider_to_gauge(self.ui.gauge_pan, self.ui.sliderLimitClockwisePAN))
        self.ui.txtLimitAntiClockwisePAN.editingFinished.connect(
            lambda: self.limit_slider_to_gauge(self.ui.gauge_pan, self.ui.sliderLimitClockwisePAN))
        self.ui.txtLimitClockwiseTilt.editingFinished.connect(
            lambda: self.limit_slider_to_gauge(self.ui.gauge_tilt, self.ui.sliderLimitClockwiseTilt))
        self.ui.txtLimitAntiClockwiseTilt.editingFinished.connect(
            lambda: self.limit_slider_to_gauge(self.ui.gauge_tilt, self.ui.sliderLimitClockwiseTilt))

        # Slider Setting
        self.ui.sliderScanSpeed.setMinimum(0)
        self.ui.sliderScanSpeed.setMaximum(10000)
        self.ui.sliderSpeedPAN.setMinimum(0)
        self.ui.sliderSpeedPAN.setMaximum(20000)
        self.ui.sliderSpeedTilt.setMinimum(0)
        self.ui.sliderSpeedTilt.setMaximum(10000)
        self.ui.sliderGotoPositionSpeedPAN.setMinimum(0)
        self.ui.sliderGotoPositionSpeedPAN.setMaximum(20000)
        self.ui.sliderGotoPositionSpeedTilt.setMinimum(0)
        self.ui.sliderGotoPositionSpeedTilt.setMaximum(10000)

        # print('maximum', self.ui.sliderLimitAntiClockwiseTilt.minimum())

        # self.ui.sliderLimitClockwiseTilt.setInvertedAppearance(True)

        # Range Slider Setting
        self.ui.txtScanPANLow.setText(str(round(self.ui.sliderScanPAN.low() / 1000, 2)))
        self.ui.txtScanPANHigh.setText(str(round(self.ui.sliderScanPAN.high() / 1000, 2)))
        self.ui.txtScanTiltLow.setText(str(round(self.ui.sliderScanTilt.low() / 1000, 2)))
        self.ui.txtScanTiltHigh.setText(str(round(self.ui.sliderScanTilt.high() / 1000, 2)))
        self.ui.txtLimitClockwiseTilt.setText(str(round(self.ui.sliderLimitClockwiseTilt.low() / 1000, 2)))
        self.ui.txtLimitAntiClockwiseTilt.setText(str(round(self.ui.sliderLimitClockwiseTilt.high() / 1000, 2)))
        self.ui.txtLimitAntiClockwisePAN.setText(str(round(self.ui.sliderLimitClockwisePAN.low() / 1000, 2)))
        self.ui.txtLimitClockwisePAN.setText(str(round(self.ui.sliderLimitClockwisePAN.high() / 1000, 2)))

        self.limit_slider_to_gauge(self.ui.gauge_pan, self.ui.sliderLimitClockwisePAN)
        self.limit_slider_to_gauge(self.ui.gauge_tilt, self.ui.sliderLimitClockwiseTilt)

    def plain_text_to_sliders(self):
        sender = self.ui.MainWindow.sender()
        dict_sender: dict = {self.ui.txtSpeedPAN: self.ui.sliderSpeedPAN,
                             self.ui.txtSpeedTilt: self.ui.sliderSpeedTilt,
                             self.ui.txtGotoPositionDegreePAN: self.ui.sliderGotoPositionDegreePAN,
                             self.ui.sliderGotoPositionDegreeTilt_2: self.ui.sliderGotoPositionDegreeTilt,
                             self.ui.txtGotoPositionSpeedPAN: self.ui.sliderGotoPositionSpeedPAN,
                             self.ui.txtGotoPositionSpeedTilt: self.ui.sliderGotoPositionSpeedTilt,
                             self.ui.txtScanSpeed: self.ui.sliderScanSpeed}
        slider: QtWidgets.QSlider = dict_sender.get(sender)
        if slider is None:
            return
        try:
            if 'speed' not in sender.objectName().lower():
                slider.setValue(int(float(sender.text()) * 1000))
            else:
                slider.setValue(int(float(sender.text()) * 100))
        except Exception as ex:
            print('Invalid text for sliders!', ex)
            if 'speed' not in sender.objectName().lower():
                sender.setText(str(round(slider.value() / 1000, 2)))
            else:
                sender.setText(str(round(slider.value() / 100, 2)))

    def plain_text_to_range_sliders(self):
        sender = self.ui.MainWindow.sender()
        dict_sender: dict = {self.ui.txtScanPANLow: (self.ui.sliderScanPAN, False),
                             self.ui.txtScanPANHigh: (self.ui.sliderScanPAN, True),
                             self.ui.txtScanTiltLow: (self.ui.sliderScanTilt, False),
                             self.ui.txtScanTiltHigh: (self.ui.sliderScanTilt, True),
                             self.ui.txtLimitAntiClockwisePAN: (self.ui.sliderLimitClockwisePAN, False),
                             self.ui.txtLimitClockwisePAN: (self.ui.sliderLimitClockwisePAN, True),
                             self.ui.txtLimitClockwiseTilt: (self.ui.sliderLimitClockwiseTilt, False),
                             self.ui.txtLimitAntiClockwiseTilt: (self.ui.sliderLimitClockwiseTilt, True)}
        range_slider, is_high = dict_sender.get(sender)
        if range_slider is None:
            return
        try:
            value = sender.text()
            if not range_slider.minimum() <= int(float(value) * 1000) <= range_slider.maximum():
                raise 'Invalid text for range_sliders!'
            if is_high:
                if int(float(value) * 1000) < range_slider.low():
                    raise 'Invalid text for range_sliders!'

                range_slider.setHigh(int(float(value) * 1000))
                sender.setText(str(round(range_slider.high() / 1000, 2)))
            else:
                if int(float(value) * 1000) > range_slider.high():
                    raise 'Invalid text for range_sliders!'
                range_slider.setLow(int(float(value) * 1000))
                sender.setText(str(round(range_slider.low() / 1000, 2)))
        except Exception as ex:
            print('Invalid text for range_sliders!', ex)
            if is_high:
                sender.setText(str(round(range_slider.high() / 1000, 2)))
            else:
                sender.setText(str(round(range_slider.low() / 1000, 2)))

    def set_text_for_slider(self, text_edit, speed=False):
        sender: QtWidgets.QSlider = self.ui.MainWindow.sender()
        if not speed:
            text_edit.setText(str(round(sender.value() / 1000, 2)))
        else:
            text_edit.setText(str(round(sender.value() / 100, 2)))

    def set_text_for_range_slider(self, text_edit_low, text_edit_high):
        sender: RangeSlider = self.ui.MainWindow.sender()
        text_edit_low.setText(str(round(sender.low() / 1000, 2)))
        text_edit_high.setText(str(round(sender.high() / 1000, 2)))

    def limit_slider_to_gauge(self, gauge: AnalogGaugeWidget, sender=None):
        sender: QtWidgets.QSlider = self.ui.MainWindow.sender() if sender is None else sender
        dict_sender: dict = {
            self.ui.sliderLimitClockwisePAN: (self.ui.txtLimitAntiClockwisePAN, self.ui.txtLimitClockwisePAN),
            self.ui.sliderLimitClockwiseTilt: (self.ui.txtLimitClockwiseTilt, self.ui.txtLimitAntiClockwiseTilt)}
        low, high = dict_sender.get(sender)
        low, high = int(float(low.text()) * 1000), int(float(high.text()) * 1000)
        minimum, maximum = sender.minimum(), sender.maximum()
        if sender == self.ui.sliderLimitClockwisePAN:
            gauge.high_limit = int((180000 - high) / 1000)
            gauge.low_limit = int(self.normalize_scale_x(low / 1000,
                                                         minimum / 1000,
                                                         maximum / 1000,
                                                         0,
                                                         gauge.scale_angle_size))
        elif sender == self.ui.sliderLimitClockwiseTilt:
            gauge.low_limit = int(self.normalize_scale_x(-(high / 1000),
                                                         minimum / 1000,
                                                         maximum / 1000,
                                                         0,
                                                         gauge.scale_angle_size))
            gauge.high_limit = int(self.normalize_scale_x(low / 1000,
                                                          minimum / 1000,
                                                          maximum / 1000,
                                                          0,
                                                          gauge.scale_angle_size))

        gauge.update()

    @staticmethod
    def normalize_scale_x(OldValue, OldMin, OldMax, NewMin, NewMax):
        """Normalizing data"""
        return (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin

    def update_combobox(self):
        ports = Serial.get_available_ports()
        for port in ports:
            if port.name + ' ' + port.description not in [self.ui.cboxUart.itemText(i) for i in
                                                          range(self.ui.cboxUart.count())]:
                self.ui.cboxUart.addItem(port.name + ' ' + port.description)
            if self.ui.cboxUart.count() > len(ports):
                for i in range(self.ui.cboxUart.count()):
                    if self.ui.cboxUart.itemText(i) not in [p.name + ' ' + p.description for p in ports]:
                        self.ui.cboxUart.removeItem(i)

    @property
    def page(self):
        return self.ui.swMain.currentIndex()

    @page.setter
    def page(self, value: int):
        dict_sender: dict = {self.ui.btnGoToPositionScreen: 1,
                             self.ui.btnGaugesScreen: 0,
                             self.ui.btnSettingScreen: 2}
        dict_sender_reverse = {v: k for k, v in dict_sender.items()}
        sender: QtWidgets.QPushButton = dict_sender_reverse.get(value)
        try:

            btn: QtWidgets.QPushButton = dict_sender_reverse.get(self.page)
            if btn is not None:
                self.remove_pages_style_sheet(btn)
            self.ui.swMain.slideToWidgetIndex(value)
            for keys in dict_sender.keys():
                if keys == sender:
                    self.setup_pages_style_sheet(sender)
                    break

        except Exception as ex:
            print(ex)
