import traceback

from src.gui.joystick_widget import Direction
# from src.communication.common import Communication
import hid
from time import sleep
import math
from math import sqrt


class Controller:
    connected: bool = False
    logger: str = ''
    game_pad = None
    use_controller: bool = False
    option_button: bool = False
    string_binary_0: str = ''
    string_binary_1: str = ''

    def get_connection(self):
        try:
            for device in hid.enumerate():
                vendor_id = int(f"0x{device['vendor_id']:04x}", 16)
                product_id = int(f"0x{device['product_id']:04x}", 16)
                product_string = f"{device['product_string']}"
                if vendor_id == 1356 and 'wireless controller' in product_string.lower():
                    self.game_pad = hid.device()
                    self.game_pad.open(vendor_id, product_id)
                    self.game_pad.set_nonblocking(True)
                    self.connected = True
                    return True
        except Exception as ex:
            self.logger = str(ex)
            self.connected = False
        finally:
            return False

    def joystickDirection(self):
        try:
            data = self.game_pad.read(32)
            if data:
                byte_six = format(data[6], '08b')
                if len(byte_six) >= 3:
                    self.option_button = bool(int(byte_six[2]))
                byte_five = format(data[5], '08b')
                byte_seven = format(data[7], '08b')
                self.string_binary_0 = byte_five[:4] + byte_six[4:]
                self.string_binary_1 = byte_six[0] + byte_six[1] + str(0) + byte_six[3] + str(0) + str(0) + byte_seven[6] + str(0)
                byte_keypad = byte_five[4:]
                keypad_sign = int(byte_keypad, 2)
                if keypad_sign != 8:
                    if keypad_sign == 0:
                        return Direction.Up, 1.0
                    elif keypad_sign == 1:
                        return Direction.TopRight, 1.0
                    elif keypad_sign == 2:
                        return Direction.Right, 1.0
                    elif keypad_sign == 3:
                        return Direction.DownRight, 1.0
                    elif keypad_sign == 4:
                        return Direction.Down, 1.0
                    elif keypad_sign == 5:
                        return Direction.DownLeft, 1.0
                    elif keypad_sign == 6:
                        return Direction.Left, 1.0
                    elif keypad_sign == 7:
                        return Direction.TopLef, 1.0

                A = int(self.normalize_scale_x(data[3], 0, 255, -128, 128))
                B = -int(self.normalize_scale_x(data[4], 0, 255, -128, 128))
                alpha = round(self.alpha_angle(A, B), 1)
                if alpha < 0:
                    alpha += 360.0
                angle = alpha
                distance = self.normalize_scale_x(max(abs(A), abs(B), int(sqrt(abs(A ** 2) + abs(B ** 2)))), 0, 128, 0,
                                                  1.0)
                # print('x', A, 'y', B, 'angle', alpha, 'distance', distance)
                if 67.5 <= angle < 112.5:
                    return Direction.Up, distance
                elif 112.5 <= angle < 157.5:
                    return Direction.TopLef, distance
                elif 157.5 <= angle < 202.5:
                    return Direction.Left, distance
                elif 202.5 <= angle < 247.5:
                    return Direction.DownLeft, distance
                elif 247.5 <= angle < 292.5:
                    return Direction.Down, distance
                elif 292.5 <= angle < 337.5:
                    return Direction.DownRight, distance
                elif 22.5 <= angle < 67.5:
                    return Direction.TopRight, distance
                return Direction.Right, distance
        except Exception as ex:
            traceback.print_exc()
            if 'read error' in str(ex):
                self.connected = False
                self.use_controller = False
                return {'message': f'controller {ex} now is disconnected', 'title': 'Error'}

    @staticmethod
    def normalize_scale_x(OldValue, OldMin, OldMax, NewMin, NewMax):
        """Normalizing data"""
        return (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin

    @staticmethod
    def alpha_angle(x, y):
        try:
            return math.atan2(y, x) / math.pi * 180
        except ZeroDivisionError:
            pass
        except Exception as ex:
            print(ex)
