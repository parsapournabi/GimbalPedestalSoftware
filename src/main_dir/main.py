import random
import traceback

from src.gui.mainGUI import Ui_MainWindow
from src.gui.guiConfig import GuiConfiguration
from src.communication.serial_com import Serial
from src.communication.server import ServerSocket
from src.threads.worker import WorkerThread
from src.gui.joystick_widget import Direction
from src.communication.controller import Controller
from src.gui import imagesresources_rc

from PyQt5 import QtWidgets, QtGui
from time import sleep


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


def func_set_gauge_value(data):
    data[0].updateValue(data[1])
    data[0].update()


def func_set_pipeline_value(data):
    data[0].setValue(data[1])


class Main:
    # Windows & Uis
    main_window: QtWidgets.QWidget
    ui: Ui_MainWindow
    gui_config: GuiConfiguration

    # other classes
    sp: Serial = Serial()
    server: ServerSocket = ServerSocket()
    controller: Controller = Controller()

    # Variables
    joystick_hold: bool = False
    external_joystick_hold: bool = False
    controller_buttons_hold: bool = False

    def __init__(self, platform: str, version: str):
        self.platform = platform
        self.version = version

        # Threads and Workers
        self.thread_main_worker = WorkerThread(self.thread_main)
        self.server_loop_worker = WorkerThread(self.server_loop)
        self.controller_loop_worker = WorkerThread(self.controller_loop)
        # Do some functions
        self.open_main_window()

        self.thread_main_worker.signal_set_text.connect(lambda data: data[0].setText(data[1]))
        self.thread_main_worker.signal_set_style.connect(lambda data: data[0].setStyleSheet(data[1]))
        self.thread_main_worker.signal_set_gauge_value.connect(func_set_gauge_value)
        self.thread_main_worker.signal_message_box.connect(func_message_box)
        self.thread_main_worker.signal_set_value.connect(func_set_pipeline_value)

        self.controller_loop_worker.signal_message_box.connect(func_message_box)

        self.thread_main_worker.start()
        self.controller_loop_worker.start()
        # gui

    def open_main_window(self):
        self.gui_config = GuiConfiguration(Ui_MainWindow, self.platform, True)
        self.main_window = self.gui_config.window
        self.ui: Ui_MainWindow = self.gui_config.ui
        self.main_window.show()

        self.ui_main_events()

    def ui_main_events(self):
        self.ui.cboxUart.currentIndexChanged.connect(self.combo_box_changed)
        self.ui.btnUartConnect.clicked.connect(self.serial_connect)
        self.ui.btnLanConnect.clicked.connect(self.server_connect)
        self.ui.btnT.pressed.connect(self.keypad_t)
        self.ui.btnB.pressed.connect(self.keypad_b)
        self.ui.btnR.pressed.connect(self.keypad_r)
        self.ui.btnL.pressed.connect(self.keypad_l)
        self.ui.btnRT.pressed.connect(self.keypad_rt)
        self.ui.btnRB.pressed.connect(self.keypad_rb)
        self.ui.btnLT.pressed.connect(self.keypad_lt)
        self.ui.btnLB.pressed.connect(self.keypad_lb)
        self.ui.btnT.released.connect(self.keypad_released)
        self.ui.btnB.released.connect(self.keypad_released)
        self.ui.btnR.released.connect(self.keypad_released)
        self.ui.btnL.released.connect(self.keypad_released)
        self.ui.btnRT.released.connect(self.keypad_released)
        self.ui.btnRB.released.connect(self.keypad_released)
        self.ui.btnLT.released.connect(self.keypad_released)
        self.ui.btnLB.released.connect(self.keypad_released)
        self.ui.btnGotoPosition.clicked.connect(self.go_to_position)
        self.ui.btnZeroEncoder.clicked.connect(self.zero_encoder)
        self.ui.btnRefrence.clicked.connect(self.go_to_reference)
        self.ui.btnSetLimit.clicked.connect(self.assign_limitation)
        self.ui.btnScan.clicked.connect(self.scan_mode)
        self.ui.btnSettingCustomSend_1.clicked.connect(lambda: self.send_numbers(0))
        self.ui.btnSettingCustomSend_2.clicked.connect(lambda: self.send_numbers(1))
        self.ui.btnSettingCustomSend_3.clicked.connect(lambda: self.send_numbers(2))
        self.ui.btnSettingCustomSend_4.clicked.connect(lambda: self.send_numbers(3))
        self.ui.btnSettingCustomSend_5.clicked.connect(lambda: self.send_numbers(4))
        self.ui.btnSettingCustomSend_6.clicked.connect(lambda: self.send_numbers(5))
        self.ui.btnSettingCustomSend_7.clicked.connect(lambda: self.send_numbers(6))
        self.ui.btnSettingCustomSend_8.clicked.connect(lambda: self.send_numbers(7))
        self.ui.btnSettingCustomSend_9.clicked.connect(lambda: self.send_numbers(8))
        self.ui.btnSettingCustomSend_10.clicked.connect(lambda: self.send_numbers(9))
        # self.ui.joystick.movingOffset.connect(lambda : print('salam parsa'))

    def thread_main(self):
        cnt_serial_timeout = 0
        timeout_max = 5_000
        while True:
            try:
                if self.ui.joystick.grabCenter:
                    self.joystick_hold = True
                    self.joystick_movement()
                elif self.joystick_hold:
                    self.keypad_released()
                    self.joystick_hold = False
                try:
                    if self.sp.connected:
                        self.sp.read_all = self.sp.serial.read_all()
                        if cnt_serial_timeout >= timeout_max:
                            self.sp.timeout = True
                            self.thread_main_worker.set_style_sheet(self.ui.btnUartConnect, 'background-color: yellow')
                            cnt_serial_timeout = 0

                        if self.sp.read_all:
                            if self.sp.timeout:
                                self.thread_main_worker.set_style_sheet(self.ui.btnUartConnect,
                                                                        'background-color: green;')
                            self.sp.timeout = False
                            self.serial_update_data()
                            cnt_serial_timeout = 0
                        else:
                            cnt_serial_timeout += 1
                except Exception as ex1:
                    print(f'Exception at thread_main with serial {ex1}')

            except Exception as ex:
                print(ex)
            sleep(0.001)

    def server_loop(self):
        while self.server.connected:
            try:
                if not self.server.accept:
                    self.server.accepting()

                else:
                    if 'green' not in self.ui.btnLanConnect.styleSheet():
                        self.thread_main_worker.set_style_sheet(self.ui.btnLanConnect, 'background-color: green')
                        self.thread_main_worker.set_text(self.ui.btnLanConnect, 'Connected')
                    self.server.read_all = self.server.client_connected.recv(1024)
                    self.serial_update_data(use_lan=True)
                    sleep(0.001)
            except Exception as ex:
                print(f'Exception on server_loop {ex}')
                traceback.print_exc()

    def controller_loop(self):
        cnt_hold_option = 0
        hold_time = 285
        while True:
            try:
                if self.controller.connected and self.controller.use_controller:
                    self.ui.btnT.setEnabled(False)
                    self.ui.btnB.setEnabled(False)
                    self.ui.btnR.setEnabled(False)
                    self.ui.btnL.setEnabled(False)
                    self.ui.btnRT.setEnabled(False)
                    self.ui.btnRB.setEnabled(False)
                    self.ui.btnLT.setEnabled(False)
                    self.ui.btnLB.setEnabled(False)
                    self.ui.joystick.setEnabled(False)
                else:
                    self.ui.btnT.setEnabled(True)
                    self.ui.btnB.setEnabled(True)
                    self.ui.btnR.setEnabled(True)
                    self.ui.btnL.setEnabled(True)
                    self.ui.btnRT.setEnabled(True)
                    self.ui.btnRB.setEnabled(True)
                    self.ui.btnLT.setEnabled(True)
                    self.ui.btnLB.setEnabled(True)
                    self.ui.joystick.setEnabled(True)

                if not self.controller.connected:
                    self.controller.get_connection()
                    if self.controller.connected:
                        self.controller_loop_worker.message_box('Controller has been connected', 'info')
                if self.controller.connected:
                    result = self.controller.joystickDirection()
                    if isinstance(result, dict):
                        self.controller_loop_worker.message_box(result['message'], result['title'])
                    elif isinstance(result, tuple):
                        if self.controller.option_button is True:
                            cnt_hold_option += 1
                        else:
                            cnt_hold_option = 0
                        if cnt_hold_option >= hold_time and self.controller.use_controller is False:
                            self.controller.use_controller = True
                            cnt_hold_option = 0
                            self.controller_loop_worker.message_box('External Joystick ENABLED', 'Warning')
                        if cnt_hold_option >= hold_time and self.controller.use_controller is True:
                            self.controller.use_controller = False
                            cnt_hold_option = 0
                            self.controller_loop_worker.message_box('External Joystick DISABLED', 'Warning')
                        if self.controller.use_controller:
                            direction, distance = result
                            if distance > 0.3:
                                self.external_joystick_movement(direction=direction,
                                                                distance=distance)
                                self.external_joystick_hold = True
                            elif self.external_joystick_hold:
                                self.keypad_released()
                                self.external_joystick_hold = False
                            if int(self.controller.string_binary_0 + self.controller.string_binary_1):
                                print(self.controller.string_binary_0, self.controller.string_binary_1)
                                self.controller_buttons_clicked()
                                self.controller_buttons_hold = True
                            elif self.controller_buttons_hold:
                                self.controller_buttons_clicked()
                                self.controller_buttons_hold = False
            except Exception as ex:
                print('Exception on controller_loop', ex)
            sleep(0.001)

    def combo_box_changed(self):
        self.sp.port = self.ui.cboxUart.currentText().split()[0]

    def serial_connect(self):
        if self.sp.connected:
            func_message_box(self.sp.disconnect())
        else:
            func_message_box(self.sp.connect())
        if self.sp.connected:
            self.ui.btnUartConnect.setStyleSheet('background-color: green')
            self.ui.btnUartConnect.setText('Connected')
            self.ui.btnLanConnect.setEnabled(False)
        else:
            self.ui.btnUartConnect.setStyleSheet('background-color: #2c313c}')
            self.ui.btnUartConnect.setText('Not connected')
            self.ui.btnLanConnect.setEnabled(True)

    def server_connect(self):
        if self.server.connected:
            func_message_box(self.server.disconnect())
        else:
            self.server.host = self.ui.txtLanIp.text()
            self.server.port = int(self.ui.txtLanPort.text()) if self.ui.txtLanPort.text() else 0
            func_message_box(self.server.connect())
        if self.server.connected:
            self.ui.btnLanConnect.setStyleSheet('background-color: blue')
            self.ui.btnLanConnect.setText('Listening')
            self.ui.btnUartConnect.setEnabled(False)
            self.server_loop_worker.start()
        else:
            self.ui.btnLanConnect.setStyleSheet('background-color: #2c313c}')
            self.ui.btnLanConnect.setText('Not connected')
            self.ui.btnUartConnect.setEnabled(True)
            self.server_loop_worker.quit()

    def serial_update_data(self, use_lan: bool = False):
        try:
            hex_str = self.sp.read_all.hex() if not use_lan else self.server.read_all.hex()
            hex_list = [(hex_str[i:i + 2]) for i in range(0, len(hex_str), 2)]
            if len(hex_list) > 30:
                return False
            self.thread_main_worker.set_text(self.ui.lblLANDataRecieve, '-'.join(hex_list).upper())
            resp_parse = self.sp.parse_reading(hex_list) if not use_lan else self.server.parse_reading(hex_list)
            if isinstance(resp_parse, dict):
                self.thread_main_worker.set_gauge_value(self.ui.gauge_pan,
                                                        resp_parse['panDegree'] / 1000 if resp_parse['signPan'] else -
                                                                                                                     resp_parse[
                                                                                                                         'panDegree'] / 1000)
                self.thread_main_worker.set_gauge_value(self.ui.gauge_tilt,
                                                        -resp_parse['tiltDegree'] / 1000 if resp_parse['signTilt'] else
                                                        resp_parse['tiltDegree'] / 1000)
                self.thread_main_worker.set_gauge_value(self.ui.gauge_pan_speed,
                                                        resp_parse['panSpeed'] / 100)
                self.thread_main_worker.set_gauge_value(self.ui.gauge_tilt_speed,
                                                        resp_parse['tiltSpeed'] / 100)
                self.thread_main_worker.set_text(self.ui.lblPANSpeedValue, str(resp_parse['panSpeed'] / 100))
                self.thread_main_worker.set_text(self.ui.lblTiltSpeedValue, str(resp_parse['tiltSpeed'] / 100))

                self.thread_main_worker.set_value(self.ui.pipeline_temp_pan,
                                                  resp_parse['panMotorTemp'] if resp_parse['panMotorTempSign'] else -
                                                  resp_parse['panMotorTemp'])
                self.thread_main_worker.set_text(self.ui.lblPANTempValue,
                                                 str(resp_parse['panMotorTemp']) + '°C' if resp_parse[
                                                     'panMotorTempSign'] else str(-
                                                                                  resp_parse['panMotorTemp']) + '°C')
                self.thread_main_worker.set_value(self.ui.pipeline_torque_pan, resp_parse['panMotorTorque'])
                self.thread_main_worker.set_text(self.ui.lblPANTorqueValue, str(resp_parse['panMotorTorque']) + '%')

                self.thread_main_worker.set_value(self.ui.pipeline_temp_tilt,
                                                  resp_parse['tiltMotorTemp'] if resp_parse['tiltMotorTempSign'] else -
                                                  resp_parse['tiltMotorTemp'])
                self.thread_main_worker.set_text(self.ui.lblTiltTempValue,
                                                 str(resp_parse['tiltMotorTemp']) + '°C' if resp_parse[
                                                     'tiltMotorTempSign'] else str(-resp_parse['tiltMotorTemp']) + '°C')
                self.thread_main_worker.set_value(self.ui.pipeline_torque_tilt, resp_parse['tiltMotorTorque'])
                self.thread_main_worker.set_text(self.ui.lblTiltTorqueValue, str(resp_parse['tiltMotorTorque']) + '%')

                print(resp_parse['panDegree'], resp_parse['tiltDegree'])
                if resp_parse['panPositionReached']:
                    self.thread_main_worker.set_style_sheet(self.ui.outPANPOSDONE,
                                                            '''background-color: green;
                                                                border-radius: 7px;''')
                else:
                    self.thread_main_worker.set_style_sheet(self.ui.outPANPOSDONE,
                                                            '''background-color: #838ea2;
                                                                border-radius: 7px;''')
                if resp_parse['tiltPositionReached']:
                    self.thread_main_worker.set_style_sheet(self.ui.outTiltPOSDONE,
                                                            '''background-color: green;
                                                                border-radius: 7px;''')
                else:
                    self.thread_main_worker.set_style_sheet(self.ui.outTiltPOSDONE,
                                                            '''background-color: #838ea2;
                                                                border-radius: 7px;''')
                if resp_parse['panOverVoltage']:
                    self.thread_main_worker.set_style_sheet(self.ui.outOVPAN,
                                                            '''background-color: red;
                                                                border-radius: 7px;''')
                else:
                    self.thread_main_worker.set_style_sheet(self.ui.outOVPAN,
                                                            '''background-color: green;
                                                                border-radius: 7px;''')
                if resp_parse['panUnderVoltage']:
                    self.thread_main_worker.set_style_sheet(self.ui.outUVPAN,
                                                            '''background-color: red;
                                                                border-radius: 7px;''')
                else:
                    self.thread_main_worker.set_style_sheet(self.ui.outUVPAN,
                                                            '''background-color: green;
                                                                border-radius: 7px;''')
                if resp_parse['tiltOverVoltage']:
                    self.thread_main_worker.set_style_sheet(self.ui.outOVTilt,
                                                            '''background-color: red;
                                                                border-radius: 7px;''')
                else:
                    self.thread_main_worker.set_style_sheet(self.ui.outOVTilt,
                                                            '''background-color: green;
                                                                border-radius: 7px;''')
                if resp_parse['tiltUnderVoltage']:
                    self.thread_main_worker.set_style_sheet(self.ui.outUVTilt,
                                                            '''background-color: red;
                                                                border-radius: 7px;''')
                else:
                    self.thread_main_worker.set_style_sheet(self.ui.outUVTilt,
                                                            '''background-color: green;
                                                                border-radius: 7px;''')
                if resp_parse['panMotorEnable']:
                    self.thread_main_worker.set_style_sheet(self.ui.outMEPAN,
                                                            '''background-color: red;
                                                                border-radius: 7px;''')
                else:
                    self.thread_main_worker.set_style_sheet(self.ui.outMEPAN,
                                                            '''background-color: green;
                                                                border-radius: 7px;''')

                if resp_parse['panPositiveLimitSwitch']:
                    self.thread_main_worker.set_style_sheet(self.ui.outPLPAN,
                                                            '''background-color: red;
                                                                border-radius: 7px;''')
                else:
                    self.thread_main_worker.set_style_sheet(self.ui.outPLPAN,
                                                            '''background-color: green;
                                                                border-radius: 7px;''')
                if resp_parse['panNegativeLimitSwitch']:
                    self.thread_main_worker.set_style_sheet(self.ui.outNLPAN,
                                                            '''background-color: red;
                                                                border-radius: 7px;''')
                else:
                    self.thread_main_worker.set_style_sheet(self.ui.outNLPAN,
                                                            '''background-color: green;
                                                                border-radius: 7px;''')

                if resp_parse['panTracking']:
                    self.thread_main_worker.set_style_sheet(self.ui.outTrackingPAN,
                                                            '''background-color: red;
                                                                border-radius: 7px;''')
                else:
                    self.thread_main_worker.set_style_sheet(self.ui.outTrackingPAN,
                                                            '''background-color: green;
                                                                border-radius: 7px;''')
                if resp_parse['tiltMotorEnable']:
                    self.thread_main_worker.set_style_sheet(self.ui.outMETilt,
                                                            '''background-color: red;
                                                                border-radius: 7px;''')
                else:
                    self.thread_main_worker.set_style_sheet(self.ui.outMETilt,
                                                            '''background-color: green;
                                                                border-radius: 7px;''')

                if resp_parse['tiltUpLimitSwitch']:
                    self.thread_main_worker.set_style_sheet(self.ui.outPLTilt,
                                                            '''background-color: red;
                                                                border-radius: 7px;''')
                else:
                    self.thread_main_worker.set_style_sheet(self.ui.outPLTilt,
                                                            '''background-color: green;
                                                                border-radius: 7px;''')
                if resp_parse['tiltDownLimitSwitch']:
                    self.thread_main_worker.set_style_sheet(self.ui.outNLTilt,
                                                            '''background-color: red;
                                                                border-radius: 7px;''')
                else:
                    self.thread_main_worker.set_style_sheet(self.ui.outNLTilt,
                                                            '''background-color: green;
                                                                border-radius: 7px;''')

                if resp_parse['tiltTracking']:
                    self.thread_main_worker.set_style_sheet(self.ui.outTrackingTilt,
                                                            '''background-color: red;
                                                                border-radius: 7px;''')
                else:
                    self.thread_main_worker.set_style_sheet(self.ui.outTrackingTilt,
                                                            '''background-color: green;
                                                                border-radius: 7px;''')
            elif isinstance(resp_parse, str):
                raise 'Invalid Checksum'
            return True
        except Exception as ex:
            print(f'Exception at serial_update_data {ex}')
            traceback.print_exc()
        return False

    def joystick_movement(self):
        try:
            dict_direction: dict = {Direction.Down: self.keypad_b,
                                    Direction.Right: self.keypad_r,
                                    Direction.Left: self.keypad_l,
                                    Direction.Up: self.keypad_t,
                                    Direction.TopRight: self.keypad_rt,
                                    Direction.TopLef: self.keypad_lt,
                                    Direction.DownRight: self.keypad_rb,
                                    Direction.DownLeft: self.keypad_lb}
            direction, distance = self.ui.joystick.joystickDirection()
            func = dict_direction.get(direction)
            func(distance)

        except Exception as ex:
            print(f'Exception at joystick_movement {ex}')
            traceback.print_exc()

    def external_joystick_movement(self, direction, distance):
        try:
            dict_direction: dict = {Direction.Down: self.keypad_b,
                                    Direction.Right: self.keypad_r,
                                    Direction.Left: self.keypad_l,
                                    Direction.Up: self.keypad_t,
                                    Direction.TopRight: self.keypad_rt,
                                    Direction.TopLef: self.keypad_lt,
                                    Direction.DownRight: self.keypad_rb,
                                    Direction.DownLeft: self.keypad_lb}
            func = dict_direction.get(direction)
            func(distance)

        except Exception as ex:
            print(f'Exception at external_joystick_movement {ex}')
            traceback.print_exc()

    def keypad_t(self, distance: float = 1.0):
        try:
            if self.sp.connected:
                hex_str = self.sp.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=0,
                    tilt_dir=0,
                    pan_on=0,
                    tilt_on=1)
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=0,
                    tilt_dir=0,
                    pan_on=0,
                    tilt_on=1)
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))
            sleep(0.001)
        except Exception as ex:
            print(f"Exception at keypad_up {ex}")
            traceback.print_exc()

    def keypad_b(self, distance: float = 1.0):
        try:
            if self.sp.connected:
                hex_str = self.sp.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=0,
                    tilt_dir=1,
                    pan_on=0,
                    tilt_on=1)
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=0,
                    tilt_dir=1,
                    pan_on=0,
                    tilt_on=1)
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))
            sleep(0.001)
        except Exception as ex:
            print(f"Exception at keypad_up {ex}")
            traceback.print_exc()

    def keypad_r(self, distance: float = 1.0):
        try:
            if self.sp.connected:
                hex_str = self.sp.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=0,
                    tilt_dir=0,
                    pan_on=1,
                    tilt_on=0)
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=0,
                    tilt_dir=0,
                    pan_on=1,
                    tilt_on=0)
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))
            sleep(0.001)
        except Exception as ex:
            print(f"Exception at keypad_up {ex}")
            traceback.print_exc()

    def keypad_l(self, distance: float = 1.0):
        try:
            if self.sp.connected:
                hex_str = self.sp.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=1,
                    tilt_dir=0,
                    pan_on=1,
                    tilt_on=0)
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=1,
                    tilt_dir=0,
                    pan_on=1,
                    tilt_on=0)
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))

            sleep(0.001)
        except Exception as ex:
            print(f"Exception at keypad_up {ex}")
            traceback.print_exc()

    def keypad_rt(self, distance: float = 1.0):
        try:
            if self.sp.connected:
                hex_str = self.sp.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=0,
                    tilt_dir=0,
                    pan_on=1,
                    tilt_on=1)
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=0,
                    tilt_dir=0,
                    pan_on=1,
                    tilt_on=1)
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))

            sleep(0.001)
        except Exception as ex:
            print(f"Exception at keypad_up {ex}")
            traceback.print_exc()

    def keypad_rb(self, distance: float = 1.0):
        try:
            if self.sp.connected:
                hex_str = self.sp.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=0,
                    tilt_dir=1,
                    pan_on=1,
                    tilt_on=1)
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=0,
                    tilt_dir=1,
                    pan_on=1,
                    tilt_on=1)
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))

            sleep(0.001)
        except Exception as ex:
            print(f"Exception at keypad_up {ex}")
            traceback.print_exc()

    def keypad_lt(self, distance: float = 1.0):
        try:
            if self.sp.connected:
                hex_str = self.sp.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=1,
                    tilt_dir=0,
                    pan_on=1,
                    tilt_on=1)
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=1,
                    tilt_dir=0,
                    pan_on=1,
                    tilt_on=1)
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))

            sleep(0.001)
        except Exception as ex:
            print(f"Exception at keypad_up {ex}")
            traceback.print_exc()

    def keypad_lb(self, distance: float = 1.0):
        try:
            if self.sp.connected:
                hex_str = self.sp.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=1,
                    tilt_dir=1,
                    pan_on=1,
                    tilt_on=1)
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_joystick_movement(
                    pan_speed=int(float(self.ui.txtSpeedPAN.text()) * 100 * distance),
                    tilt_speed=int(float(self.ui.txtSpeedTilt.text()) * 100 * distance),
                    pan_dir=1,
                    tilt_dir=1,
                    pan_on=1,
                    tilt_on=1)
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))

            sleep(0.001)
        except Exception as ex:
            print(f"Exception at keypad_up {ex}")
            traceback.print_exc()

    def keypad_released(self):
        try:
            if self.sp.connected:
                hex_str = self.sp.parse_sending_joystick_movement(
                    pan_speed=0,
                    tilt_speed=0,
                    pan_dir=0,
                    tilt_dir=0,
                    pan_on=0,
                    tilt_on=0)
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_joystick_movement(
                    pan_speed=0,
                    tilt_speed=0,
                    pan_dir=0,
                    tilt_dir=0,
                    pan_on=0,
                    tilt_on=0)
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))

            sleep(0.001)
        except Exception as ex:
            print(f"Exception at keypad_up {ex}")
            traceback.print_exc()

    def go_to_position(self):
        try:
            if self.sp.connected:
                hex_str = self.sp.parse_sending_goto_position(
                    pan_degree=abs(int(float(self.ui.txtGotoPositionDegreePAN.text()) * 100)),
                    tilt_degree=abs(int(float(self.ui.sliderGotoPositionDegreeTilt_2.text()) * 100)),
                    pan_speed=int(float(self.ui.txtGotoPositionSpeedPAN.text()) * 100),
                    tilt_speed=int(float(self.ui.txtGotoPositionSpeedTilt.text()) * 100),
                    pan_goto_position_on=int(self.ui.cbPANGotoPosition.isChecked()),
                    tilt_goto_position_on=int(self.ui.cbTiltGotoPosition.isChecked()),
                    pan_dir=1 if int(float(self.ui.txtGotoPositionDegreePAN.text()) * 100) >= 0 else 0,
                    tilt_dir=1 if int(float(self.ui.sliderGotoPositionDegreeTilt_2.text()) * 100) >= 0 else 0)
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_goto_position(
                    pan_degree=abs(int(float(self.ui.txtGotoPositionDegreePAN.text()) * 100)),
                    tilt_degree=abs(int(float(self.ui.sliderGotoPositionDegreeTilt_2.text()) * 100)),
                    pan_speed=int(float(self.ui.txtGotoPositionSpeedPAN.text()) * 100),
                    tilt_speed=int(float(self.ui.txtGotoPositionSpeedTilt.text()) * 100),
                    pan_goto_position_on=int(self.ui.cbPANGotoPosition.isChecked()),
                    tilt_goto_position_on=int(self.ui.cbTiltGotoPosition.isChecked()),
                    pan_dir=1 if int(float(self.ui.txtGotoPositionDegreePAN.text()) * 100) >= 0 else 0,
                    tilt_dir=1 if int(float(self.ui.sliderGotoPositionDegreeTilt_2.text()) * 100) >= 0 else 0)
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))

            sleep(0.001)
        except Exception as ex:
            print(f"Exception at keypad_up {ex}")
            traceback.print_exc()

    def zero_encoder(self):
        try:
            if self.sp.connected:
                hex_str = self.sp.parse_sending_zero_encoder(pan_zero=int(self.ui.cbPANZero.isChecked()),
                                                             tilt_zero=int(self.ui.cbTiltZero.isChecked()))
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_zero_encoder(pan_zero=int(self.ui.cbPANZero.isChecked()),
                                                                 tilt_zero=int(self.ui.cbTiltZero.isChecked()))
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))

            sleep(0.001)
        except Exception as ex:
            print(f"Exception at keypad_up {ex}")
            traceback.print_exc()

    def assign_limitation(self):
        try:
            if self.sp.connected:
                hex_str = self.sp.parse_sending_assign_limitation(
                    pan_degree_right=abs(int(float(self.ui.txtLimitClockwisePAN.text()) * 100)),
                    pan_degree_left=abs(int(float(self.ui.txtLimitAntiClockwisePAN.text()) * 100)),
                    tilt_degree_up=abs(int(float(
                        self.ui.txtLimitClockwiseTilt.text()) * 100)),
                    tilt_degree_down=abs(int(float(
                        self.ui.txtLimitAntiClockwiseTilt.text()) * 100)),
                    pan_limit_on=0 if abs(int(float(self.ui.txtLimitAntiClockwisePAN.text()) * 100)) == 18000 and abs(
                        int(float(self.ui.txtLimitClockwisePAN.text()) * 100)) == 0 else 1,
                    tilt_limit_on=0 if abs(int(float(self.ui.txtLimitClockwiseTilt.text()) * 100)) == 9000 and abs(
                        int(float(self.ui.txtLimitAntiClockwiseTilt.text()) * 100)) == 9000 else 1,
                    pan_dir_right=1 if int(float(self.ui.txtLimitClockwisePAN.text()) * 100) >= 0 else 0,
                    pan_dir_left=1 if int(float(self.ui.txtLimitAntiClockwisePAN.text()) * 100) >= 0 else 0,
                    tilt_dir_up=1 if int(float(self.ui.txtLimitClockwiseTilt.text()) * 100) >= 0 else 0,
                    tilt_dir_down=1 if int(float(self.ui.txtLimitAntiClockwiseTilt.text()) * 100) >= 0 else 0)
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_assign_limitation(
                    pan_degree_right=abs(int(float(self.ui.txtLimitClockwisePAN.text()) * 100)),
                    pan_degree_left=abs(int(float(self.ui.txtLimitAntiClockwisePAN.text()) * 100)),
                    tilt_degree_up=abs(int(float(
                        self.ui.txtLimitClockwiseTilt.text()) * 100)),
                    tilt_degree_down=abs(int(float(
                        self.ui.txtLimitAntiClockwiseTilt.text()) * 100)),
                    pan_limit_on=0 if abs(int(float(self.ui.txtLimitAntiClockwisePAN.text()) * 100)) == 18000 and abs(
                        int(float(self.ui.txtLimitClockwisePAN.text()) * 100)) == 0 else 1,
                    tilt_limit_on=0 if abs(int(float(self.ui.txtLimitClockwiseTilt.text()) * 100)) == 9000 and abs(
                        int(float(self.ui.txtLimitAntiClockwiseTilt.text()) * 100)) == 9000 else 1,
                    pan_dir_right=1 if int(float(self.ui.txtLimitClockwisePAN.text()) * 100) >= 0 else 0,
                    pan_dir_left=1 if int(float(self.ui.txtLimitAntiClockwisePAN.text()) * 100) >= 0 else 0,
                    tilt_dir_up=1 if int(float(self.ui.txtLimitClockwiseTilt.text()) * 100) >= 0 else 0,
                    tilt_dir_down=1 if int(float(self.ui.txtLimitAntiClockwiseTilt.text()) * 100) >= 0 else 0)
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))

            sleep(0.001)
        except Exception as ex:
            print(f"Exception at keypad_up {ex}")
            traceback.print_exc()

    def go_to_reference(self):
        try:
            if self.sp.connected:
                hex_str = self.sp.parse_sending_goto_reference(pan_reference=int(self.ui.cbPANRefrence.isChecked()),
                                                               tilt_reference=int(self.ui.cbTiltRefrence.isChecked()))
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_goto_reference(pan_reference=int(self.ui.cbPANRefrence.isChecked()),
                                                                   tilt_reference=int(
                                                                       self.ui.cbTiltRefrence.isChecked()))
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))

            sleep(0.001)
        except Exception as ex:
            print(f"Exception at keypad_up {ex}")
            traceback.print_exc()

    def scan_mode(self):
        try:
            if self.sp.connected:
                hex_str = self.sp.parse_sending_scan_mode(
                    pan_degree_right=abs(int(float(self.ui.txtScanPANHigh.text()) * 100)),
                    pan_degree_left=abs(int(float(self.ui.txtScanPANLow.text()) * 100)),
                    tilt_degree_up=abs(int(float(self.ui.txtScanTiltHigh.text()) * 100)),
                    tilt_degree_down=abs(int(float(self.ui.txtScanTiltLow.text()) * 100)),
                    pan_scan_on=int(self.ui.cbPANScan.isChecked()),
                    tilt_scan_on=int(self.ui.cbTiltScan.isChecked()),
                    pan_dir_right=1 if int(float(self.ui.txtScanPANHigh.text()) * 100) >= 0 else 0,
                    pan_dir_left=1 if int(float(self.ui.txtScanPANLow.text()) * 100) >= 0 else 0,
                    tilt_dir_up=1 if int(float(self.ui.txtScanTiltHigh.text()) * 100) >= 0 else 0,
                    tilt_dir_down=1 if int(float(self.ui.txtScanTiltLow.text()) * 100) >= 0 else 0,
                    scan_speed=int(float(self.ui.txtScanSpeed.text()) * 100))
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_scan_mode(
                    pan_degree_right=abs(int(float(self.ui.txtScanPANHigh.text()) * 100)),
                    pan_degree_left=abs(int(float(self.ui.txtScanPANLow.text()) * 100)),
                    tilt_degree_up=abs(int(float(self.ui.txtScanTiltHigh.text()) * 100)),
                    tilt_degree_down=abs(int(float(self.ui.txtScanTiltLow.text()) * 100)),
                    pan_scan_on=int(self.ui.cbPANScan.isChecked()),
                    tilt_scan_on=int(self.ui.cbTiltScan.isChecked()),
                    pan_dir_right=1 if int(float(self.ui.txtScanPANHigh.text()) * 100) >= 0 else 0,
                    pan_dir_left=1 if int(float(self.ui.txtScanPANLow.text()) * 100) >= 0 else 0,
                    tilt_dir_up=1 if int(float(self.ui.txtScanTiltHigh.text()) * 100) >= 0 else 0,
                    tilt_dir_down=1 if int(float(self.ui.txtScanTiltLow.text()) * 100) >= 0 else 0,
                    scan_speed=int(float(self.ui.txtScanSpeed.text()) * 100))
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))

            sleep(0.001)
        except Exception as ex:
            print(f"Exception at keypad_up {ex}")
            traceback.print_exc()

    def send_numbers(self, which_number: int):
        try:
            dict_numbers: dict = {0: self.ui.txtSettingFloat_1,
                                  1: self.ui.txtSettingFloat_2,
                                  2: self.ui.txtSettingFloat_3,
                                  3: self.ui.txtSettingFloat_4,
                                  4: self.ui.txtSettingFloat_5,
                                  5: self.ui.txtSettingFloat_6,
                                  6: self.ui.txtSettingFloat_7,
                                  7: self.ui.txtSettingFloat_8,
                                  8: self.ui.txtSettingFloat_9,
                                  9: self.ui.txtSettingFloat_10}
            if self.sp.connected:
                hex_str = self.sp.parse_sending_numbers(
                    number=abs(int(float(dict_numbers.get(which_number).text()) * 1000)),
                    which_number=which_number,
                    sign_number=0 if int(float(dict_numbers.get(which_number).text()) * 1000) < 0 else 1)
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_numbers(
                    number=abs(int(float(dict_numbers.get(which_number).text()) * 1000)),
                    which_number=which_number,
                    sign_number=0 if int(float(dict_numbers.get(which_number).text()) * 1000) < 0 else 1)
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))

            sleep(0.001)
        except Exception as ex:
            print(f"Exception at keypad_up {ex}")
            traceback.print_exc()

    def controller_buttons_clicked(self):
        try:
            if self.sp.connected:
                hex_str = self.sp.parse_sending_controller_buttons(string_binary_0=self.controller.string_binary_0,
                                                                   string_binary_1=self.controller.string_binary_1)
                self.tx_label(hex_str)
                print('Writing data', self.sp.serial.write(bytes.fromhex(hex_str)))
            elif self.server.connected:
                hex_str = self.server.parse_sending_controller_buttons(string_binary_0=self.controller.string_binary_0,
                                                                       string_binary_1=self.controller.string_binary_1)
                self.tx_label(hex_str)
                print('Writing data', self.server.client_connected.send(bytes.fromhex(hex_str)))

            sleep(0.001)
        except Exception as ex:
            print(f"Exception at controller_buttons_clicked {ex}")
            traceback.print_exc()

    def tx_label(self, hex_str):
        hex_list = [(hex_str[i:i + 2]) for i in range(0, len(hex_str), 2)]
        self.thread_main_worker.set_text(self.ui.lblLANDataSend, '-'.join(hex_list).upper())

    # def test(self):
    #     try:
    #         rnd = random.randint(-5000, 20000)
    #         self.thread_main_worker.set_gauge_value(self.ui.gauge_tilt_speed, rnd / 100)
    #         sleep(0.0001)
    #
    #     except Exception as ex:
    #         print(f"Exception at keypad_up {ex}")
    #         traceback.print_exc()
