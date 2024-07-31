import traceback

import serial
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo
from serial.serialutil import SerialException
from typing import List

from src.communication.common import Communication


class Serial(Communication):
    baud_rate: int = 115200
    data_bits: int = 8
    stop_bits: int = 1
    parity: str = 'N' or 'E' or 'O'
    port: str = ''
    serial = None

    @staticmethod
    def get_available_ports() -> list[ListPortInfo]:
        try:
            ports: list = []
            for port in comports():
                ports.append(port)

            return ports
        except Exception as ex:
            traceback.print_exc()
            print(f'Exception at get_available_ports {ex}')

    def connect(self):
        self.connected = False
        self.timeout = False
        try:
            self.serial = serial.Serial(port=self.port,
                                        baudrate=self.baud_rate,
                                        bytesize=self.data_bits,
                                        stopbits=self.stop_bits,
                                        parity=self.parity)
            self.connected = True
            return f'Connecting to {self.port} successful', 'info'
        except SerialException as ex:
            return str(ex), 'Error'
        except Exception as err:
            return str(err), 'Error'

    def disconnect(self):
        try:
            self.serial.close()
            self.connected = False
            return f'Port {self.port} has been disconnected', 'info'
        except SerialException as ex:
            return str(ex), 'Error'
        except Exception as err:
            return str(err), 'Error'


if __name__ == '__main__':
    print(Serial.get_available_ports())
    ser = Serial()
    ser.port = 'COM4'
    print(ser.connect())
