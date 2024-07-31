from PyQt5.QtCore import QThread, pyqtSignal
import threading


class WorkerThread(QThread):
    signal_do_func = pyqtSignal(object)
    signal_set_icon = pyqtSignal(tuple)
    signal_set_pixmap = pyqtSignal(tuple)
    signal_message_box = pyqtSignal(tuple)
    signal_set_text = pyqtSignal(tuple)
    signal_set_plain_text = pyqtSignal(tuple)
    signal_set_value = pyqtSignal(tuple)
    signal_add_saved = pyqtSignal(object)
    signal_change_action_page = pyqtSignal(object)
    signal_question_box = pyqtSignal(str)
    signal_get_cookies = pyqtSignal(list)
    signal_get_cookies_tiktok = pyqtSignal(list)
    signal_instagram_database = pyqtSignal(list)
    signal_set_style = pyqtSignal(tuple)
    signal_set_gauge_value = pyqtSignal(tuple)

    def __init__(self, function, ret_response: bool = False):
        super(WorkerThread, self).__init__()
        self.func = function
        self.ret_response = ret_response

    def run(self):
        ret = self.func()
        if self.ret_response and isinstance(ret, dict):
            self.message_box(message=ret.get('message'), title=ret.get('title'))

    def do_func(self, method):
        emit = method
        self.signal_do_func.emit(emit)

    def set_icon(self, widget, ico_path):
        emit = (widget, ico_path)
        self.signal_set_icon.emit(emit)

    def set_pixmap(self, widget, pixmap):
        emit = (widget, pixmap)
        self.signal_set_pixmap.emit(emit)

    def message_box(self, message, title: str = 'info'):
        emit = (message, title)
        self.signal_message_box.emit(emit)

    def set_text(self, widget, text: str):
        emit = (widget, text)
        self.signal_set_text.emit(emit)

    def set_plain_text(self, widget, text: str):
        emit = (widget, text)
        self.signal_set_plain_text.emit(emit)

    def set_value(self, widget, value: int):
        emit = (widget, value)
        self.signal_set_value.emit(emit)

    def add_saved(self, obj):
        emit = obj
        self.signal_add_saved.emit(emit)

    def change_action_page(self, value):
        emit = value
        self.signal_change_action_page.emit(emit)

    def question_box(self, message: str):
        emit = message
        self.signal_question_box.emit(emit)

    def get_cookies(self, ret, username, password, func):
        emit = [ret, username, password, func]
        self.signal_get_cookies.emit(emit)

    def get_cookies_tiktok(self, ret, username, password, func):
        emit = [ret, username, password, func]
        self.signal_get_cookies_tiktok.emit(emit)

    def get_instagram_database_result(self, func, args):
        emit = [func] + args
        self.signal_instagram_database.emit(emit)

    def set_style_sheet(self, widget, style):
        emit = (widget, style)
        self.signal_set_style.emit(emit)

    def set_gauge_value(self, widget, value):
        emit = (widget, value)
        self.signal_set_gauge_value.emit(emit)

class Threading(threading.Thread):
    pass
