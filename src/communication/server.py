import socket
from src.communication.common import Communication


class ServerSocket(Communication):
    host: str
    port: int
    server: socket.socket
    accept: bool = False
    client_connected: socket.socket = None
    client_address = None

    def connect(self):
        self.connected = False
        self.timeout = False
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(3)
            self.connected = True
            return f'Server bound on {self.host}:{self.port} successfully', 'info'
        except OSError as os_err:
            return str(os_err), 'Error'
        except socket.gaierror as s_err:
            return str(s_err), 'Error'
        except Exception as err:
            return str(err), 'Error'

    def disconnect(self):
        try:
            self.server.close()
            self.connected = False
            self.timeout = False
            self.accept = False
            self.client_connected = None
            self.client_address = None
            return f'Server unbound!', 'info'
        except OSError as os_err:
            return str(os_err), 'Error'
        except socket.gaierror as s_err:
            return str(s_err), 'Error'
        except Exception as err:
            return str(err), 'Error'

    def accepting(self):
        self.client_connected, self.client_address = self.server.accept()
        if self.client_connected is not None and self.client_address is not None:
            self.accept = True
            return 0
        self.accept = False
