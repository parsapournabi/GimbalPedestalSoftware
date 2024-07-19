from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from time import sleep

from scripts.database.database import DataBase
from scripts.threads.worker import WorkerThread
# from scripts.gui.mainGUI import Ui_MainWindow


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
    db: DataBase

    # Icons PATHS...
    dict_icons_path = {'btnPageHome': [':/icons/icons/home.png', ':/icons/icons/home-clicked.png'],
                       'btnPageSaved': [':/icons/icons/Saved.png', ':/icons/icons/Saved-clicked.png'],
                       'btnPageActions': [':/icons/icons/Actions.png', ':/icons/icons/Actions-clicked.png'],
                       'btnPageSetting': [':/icons/icons/Setting.png', ':/icons/icons/Setting-clicked.png'],
                       'btnPageStatus': [':/icons/icons/Status.png', ':/icons/icons/Status-clicked.png'],
                       'btnPageHelp': [':/icons/icons/help.png', ':/icons/icons/help-clicked.png']}
    icon_side_menu_path = ':/icons/icons/Side-Menu.png'
    icon_side_menu_clicked_path = ':/icons/icons/Side-Menu-clicked.png'

    # Special Variables
    dict_actions_page_config: dict = {'socials': [], 'state': ''}

    def __init__(self, ui, platform: str, is_main_window: bool = False, args=None):
        self.platform = platform
        self.window = QtWidgets.QWidget()
        self.ui = ui()
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
            self.progress_bar_worker = WorkerThread(self.progress_bar)

            # Normal Variables
            self.animation = QtCore.QPropertyAnimation(self.ui.frameleftMenu, b"minimumWidth")
            self.animation_spacing = QtCore.QPropertyAnimation(self.ui.horizontalLayout_4, b"spacing")
            self._dict_sender_actions: dict = {self.ui.btnActionsSocialPageInstagram: False,
                                               self.ui.btnActionsSocialPageLinkedin: False,
                                               self.ui.btnActionsSocialPageTiktok: False,
                                               self.ui.btnActionsSocialPageEmail: False,
                                               self.ui.btnActionsAll: 'ALL',
                                               self.ui.btnActionsPending: 'PENDING',
                                               self.ui.btnActionsInprogress: 'INPROGRESS',
                                               self.ui.btnActionsPaused: 'PAUSE',
                                               self.ui.btnActionsDone: 'DONE'}

            # Special Variables
            self.ui.actions_config_value_changed = ValueChangedEvent()
            self.db = DataBase(platform)

            self.screen_events()

            # Threads Connections
            self.progress_bar_worker.signal_set_icon.connect(func_set_icon)

    def setup_font_point_size(self, parent):
        for child in parent:
            font = child.font()
            font.setPointSize(int(font.pointSize() * self.p_size))
            child.setFont(font)

    def remove_focus_policy(self, parent):
        for child in parent:
            child.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def remove_pages_style_sheet(self, btn: QtWidgets.QPushButton):
        btn.setStyleSheet('')
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(self.dict_icons_path.get(btn.objectName())[0]), QtGui.QIcon.Mode.Normal,
                       QtGui.QIcon.State.Off)
        btn.setIcon(icon)

    def setup_pages_style_sheet(self, btn: QtWidgets.QPushButton):
        ss = f'#{btn.objectName()}' + '{border-left: 3px solid rgb(71, 60, 56); \n' \
                                      'background-color: rgb(230, 230, 230); \n}'
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(self.dict_icons_path.get(btn.objectName())[1]), QtGui.QIcon.Mode.Normal,
                       QtGui.QIcon.State.Off)
        btn.setStyleSheet(ss)
        btn.setIconSize(btn.iconSize())
        btn.setIcon(icon)
        if 'Home' in btn.objectName():
            self.ui.swMain.setStyleSheet(self.ui.swMain.styleSheet().strip('}') + '\tborder-top-left-radius: 0px;\n}')
        else:
            if 'border-top-left-radius: 0px;' in self.ui.swMain.styleSheet():
                self.ui.swMain.setStyleSheet('\n'.join(self.ui.swMain.styleSheet().split('\n')[:-2] + ['}']))

    def side_menu_coll_exp(self):
        try:
            icon = QtGui.QIcon()
            if self.side_menu:
                icon.addPixmap(QtGui.QPixmap(self.icon_side_menu_path), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
                self.side_menu = False
            else:
                icon.addPixmap(QtGui.QPixmap(self.icon_side_menu_clicked_path), QtGui.QIcon.Mode.Normal,
                               QtGui.QIcon.State.Off)
                self.side_menu = True
            self.ui.btnSideMenu.setIcon(icon)

            width = self.ui.frameleftMenu.width()
            width_spacer = self.ui.horizontalLayout_4.spacing()
            width_extended = 65
            width_extended_spacer = 0

            # SET MAX WIDTH
            if width == 65:
                width_extended = 150
            if width_spacer == 0:
                width_extended_spacer = 80

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
        dict_sender: dict = {self.ui.btnPageHome: 1,
                             self.ui.btnPageSaved: 2,
                             self.ui.btnPageActions: 3,
                             self.ui.btnPageStatus: 4,
                             self.ui.btnPageSetting: 5,
                             self.ui.btnPageHelp: 6}

        self.page = dict_sender.get(sender, self.page)

    def screen_saved_social_buttons_clicked(self):
        sender: QtWidgets.QPushButton = self.window.sender()
        dict_sender: dict = {self.ui.btnSavedSocialPageInstagram: 0,
                             self.ui.btnSavedSocialPageLinkedin: 1,
                             self.ui.btnSavedSocialPageTiktok: 2}
        self.page_saved = dict_sender.get(sender, self.page)

    def screen_actions_socials_buttons_clicked(self, value=None):
        sender: QtWidgets.QPushButton = self.window.sender() if value is None else value
        _dict_social_name: dict = {self.ui.btnActionsSocialPageInstagram: 'INSTAGRAM',
                                   self.ui.btnActionsSocialPageLinkedin: 'LINKEDIN',
                                   self.ui.btnActionsSocialPageTiktok: 'TIKTOK',
                                   self.ui.btnActionsSocialPageEmail: 'EMAIL'}
        if isinstance(self._dict_sender_actions.get(sender), bool):
            self.dict_actions_page_config['socials'] = []
            for k, v in self._dict_sender_actions.items():
                if not isinstance(v, bool):
                    continue
                if k == sender:
                    if not v:
                        k.setIconSize(k.iconSize() * 1.2)
                        self._dict_sender_actions[k] = True
                    else:
                        k.setIconSize(k.iconSize() / 1.2)
                        self._dict_sender_actions[k] = False
                if self._dict_sender_actions[k]:
                    self.dict_actions_page_config['socials'].append(_dict_social_name.get(k))

        elif isinstance(self._dict_sender_actions.get(sender), str):
            for k, v in self._dict_sender_actions.items():
                if not isinstance(v, str):
                    continue
                if k == sender:
                    k.setStyleSheet('#%s {background-color: rgb(212, 200, 190); \n '
                                    'border-left-color: rgb(212, 200, 190);}' % k.objectName())
                    self.dict_actions_page_config['state'] = v
                else:
                    k.setStyleSheet('')

        self.ui.actions_config_value_changed.value = self.dict_actions_page_config.copy()

    def screen_setting_buttons_clicked(self):
        sender: QtWidgets.QPushButton = self.window.sender()
        dict_sender: dict = {self.ui.btnSettingPageInstagram: 0,
                             self.ui.btnSettingPageLinkedin: 1,
                             self.ui.btnSettingPageTiktok: 2,
                             self.ui.btnSettingPageEmail: 3}
        self.page_setting = dict_sender.get(sender, self.page_setting)

    def screen_events(self):
        # Events
        self.ui.btnSideMenu.clicked.connect(self.side_menu_coll_exp)
        # Main Stacked Widget Pages Changing...
        self.ui.btnPageHome.clicked.connect(lambda: self.screen_change_buttons_clicked())
        self.ui.btnPageSaved.clicked.connect(lambda: self.screen_change_buttons_clicked())
        self.ui.btnPageActions.clicked.connect(lambda: self.screen_change_buttons_clicked())
        self.ui.btnPageStatus.clicked.connect(lambda: self.screen_change_buttons_clicked())
        self.ui.btnPageSetting.clicked.connect(lambda: self.screen_change_buttons_clicked())
        self.ui.btnPageHelp.clicked.connect(lambda: self.screen_change_buttons_clicked())
        # Saved Social Stacked Widget Pages Changing
        self.ui.btnSavedSocialPageInstagram.clicked.connect(lambda: self.screen_saved_social_buttons_clicked())
        self.ui.btnSavedSocialPageLinkedin.clicked.connect(lambda: self.screen_saved_social_buttons_clicked())
        self.ui.btnSavedSocialPageTiktok.clicked.connect(lambda: self.screen_saved_social_buttons_clicked())
        # Actions Socials Buttons
        self.ui.btnActionsSocialPageInstagram.clicked.connect(lambda: self.screen_actions_socials_buttons_clicked())
        self.ui.btnActionsSocialPageLinkedin.clicked.connect(lambda: self.screen_actions_socials_buttons_clicked())
        self.ui.btnActionsSocialPageTiktok.clicked.connect(lambda: self.screen_actions_socials_buttons_clicked())
        self.ui.btnActionsSocialPageEmail.clicked.connect(lambda: self.screen_actions_socials_buttons_clicked())
        self.ui.btnActionsAll.clicked.connect(lambda: self.screen_actions_socials_buttons_clicked())
        self.ui.btnActionsPending.clicked.connect(lambda: self.screen_actions_socials_buttons_clicked())
        self.ui.btnActionsInprogress.clicked.connect(lambda: self.screen_actions_socials_buttons_clicked())
        self.ui.btnActionsPaused.clicked.connect(lambda: self.screen_actions_socials_buttons_clicked())
        self.ui.btnActionsDone.clicked.connect(lambda: self.screen_actions_socials_buttons_clicked())
        # Setting Stacked Widget Pages Changing
        self.ui.btnSettingPageInstagram.clicked.connect(lambda: self.screen_setting_buttons_clicked())
        self.ui.btnSettingPageLinkedin.clicked.connect(lambda: self.screen_setting_buttons_clicked())
        self.ui.btnSettingPageTiktok.clicked.connect(lambda: self.screen_setting_buttons_clicked())
        # self.ui.btnSettingPageEmail.clicked.connect(lambda: self.screen_setting_buttons_clicked())

        self.ui.btnInstagramExportLog.clicked.connect(self.export_log)
        self.ui.btnLinkedinExportLog.clicked.connect(self.export_log)
        self.ui.btnTiktokExportLog.clicked.connect(self.export_log)

        # Gui
        # Main Pages Animation
        self.ui.swMain.setTransitionDirection(Qt.Horizontal)
        self.ui.swMain.setTransitionSpeed(450)
        self.ui.swMain.setTransitionEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.ui.swMain.setSlideTransition(True)
        self.ui.swMain.setFadeSpeed(450)
        self.ui.swMain.setFadeCurve(QtCore.QEasingCurve.InOutQuart)
        self.ui.swMain.setFadeTransition(True)
        # SavedSocial Pages Animation
        self.ui.swSavedSocial.setTransitionDirection(Qt.Horizontal)
        self.ui.swSavedSocial.setTransitionSpeed(500)
        self.ui.swSavedSocial.setTransitionEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.ui.swSavedSocial.setSlideTransition(False)
        self.ui.swSavedSocial.setFadeSpeed(1000)
        self.ui.swSavedSocial.setFadeCurve(QtCore.QEasingCurve.InOutQuart)
        self.ui.swSavedSocial.setFadeTransition(True)
        # Setting Pages Animation
        self.ui.swSetting.setTransitionDirection(Qt.Vertical)
        self.ui.swSetting.setTransitionSpeed(450)
        self.ui.swSetting.setTransitionEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.ui.swSetting.setSlideTransition(True)
        self.ui.swSetting.setFadeSpeed(450)
        self.ui.swSetting.setFadeCurve(QtCore.QEasingCurve.InOutQuart)
        self.ui.swSetting.setFadeTransition(False)

        # First View
        self.page_saved = 0
        self.page_setting = 0
        self.ui.txtInstagramTwoFactor.hide()
        flatlay_username, _ = self.db.get_user_pass('flatlay')
        if '-at-' in flatlay_username:
            flatlay_username = flatlay_username.replace('-at-', '@')
        else:
            flatlay_username = ''
        self.ui.txtFlatlayUsername.setText(flatlay_username)

        self.ui.btnSettingPageEmail.setIconSize(self.ui.btnSettingPageEmail.iconSize() * 1.1)
        self.ui.btnSavedPageNext.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
        self.ui.btnSavedPagePrevious.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
        self.screen_actions_socials_buttons_clicked(self.ui.btnActionsSocialPageInstagram)
        self.screen_actions_socials_buttons_clicked(self.ui.btnActionsSocialPageLinkedin)
        self.screen_actions_socials_buttons_clicked(self.ui.btnActionsSocialPageTiktok)
        self.screen_actions_socials_buttons_clicked(self.ui.btnActionsAll)


    def export_log(self):
        sender: QtWidgets.QPushButton = self.window.sender()
        dict_plain_txt: dict = {self.ui.btnInstagramExportLog: self.ui.plaintxtInstagramLog,
                                self.ui.btnLinkedinExportLog: self.ui.plaintxtLinkedinLog,
                                self.ui.btnTiktokExportLog: self.ui.plaintxtTiktokLog}
        dict_social_name: dict = {self.ui.btnInstagramExportLog: 'instagram',
                                  self.ui.btnLinkedinExportLog: 'linkedin',
                                  self.ui.btnTiktokExportLog: 'tiktok'}

        plain_txt: QtWidgets.QPlainTextEdit = dict_plain_txt.get(sender)
        social_name = dict_social_name.get(sender)
        file_path, _ = QtWidgets.QFileDialog().getSaveFileName(caption=f'{social_name} export log',
                                                               filter='Text files (*.txt)')
        if not file_path:
            return 0
        with open(file_path, 'w') as file:
            file.write(plain_txt.toPlainText())
            file.close()

    def progress_bar(self):
        icons_progress = [':/icons/icons/progress_1.png',
                          ':/icons/icons/progress_2.png',
                          ':/icons/icons/progress_3.png',
                          ':/icons/icons/progress_4.png',
                          ':/icons/icons/progress_5.png',
                          ':/icons/icons/progress_6.png',
                          ':/icons/icons/progress_7.png',
                          ':/icons/icons/progress_8.png',
                          ':/icons/icons/progress_9.png',
                          ':/icons/icons/progress_10.png',
                          ':/icons/icons/progress_11.png',
                          ':/icons/icons/progress_12.png',
                          ':/icons/icons/Refresh.png']
        while self.loading and self.progress_bar_worker.started:
            self.ui.btnRefresh.setEnabled(False)
            for ico in icons_progress[:-1]:
                self.progress_bar_worker.set_icon(self.ui.btnRefresh, ico)
                sleep(0.04)
        self.ui.btnRefresh.setEnabled(True)
        self.progress_bar_worker.set_icon(self.ui.btnRefresh, icons_progress[-1])

    @property
    def page(self):
        return self.ui.swMain.currentIndex()

    @page.setter
    def page(self, value: int):
        dict_sender: dict = {self.ui.btnPageHome: 1,
                             self.ui.btnPageSaved: 2,
                             self.ui.btnPageActions: 3,
                             self.ui.btnPageStatus: 4,
                             self.ui.btnPageSetting: 5,
                             self.ui.btnPageHelp: 6}
        dict_sender_reverse = {v: k for k, v in dict_sender.items()}
        sender: QtWidgets.QPushButton = dict_sender_reverse.get(value)
        try:
            if self.page != 0:
                btn: QtWidgets.QPushButton = dict_sender_reverse.get(self.page)
                self.remove_pages_style_sheet(btn)
            self.ui.swMain.slideToWidgetIndex(value)
            for keys in dict_sender.keys():
                if keys == sender:
                    self.setup_pages_style_sheet(sender)
                    break

        except Exception as ex:
            print(ex)

    @property
    def page_saved(self):
        return self.ui.swSavedSocial.currentIndex()

    @page_saved.setter
    def page_saved(self, value: int):
        dict_sender: dict = {self.ui.btnSavedSocialPageInstagram: 0,
                             self.ui.btnSavedSocialPageLinkedin: 1,
                             self.ui.btnSavedSocialPageTiktok: 2}
        dict_sender_icon: dict = {self.ui.btnSavedSocialPageInstagram: [':/icons/icons/Instagram-Connected.png',
                                                                        ':/icons/icons/Instagram-Disconnected.png'],
                                  self.ui.btnSavedSocialPageLinkedin: [':/icons/icons/Linkedin-Connected.png',
                                                                       ':/icons/icons/Linkedin-Disconnected.png'],
                                  self.ui.btnSavedSocialPageTiktok: [':/icons/icons/Tiktok-Connected.png',
                                                                     ':/icons/icons/Tiktok-Disconnected.png']}
        dict_sender_reverse = {v: k for k, v in dict_sender.items()}
        cur_sender = dict_sender_reverse.get(self.page_saved)

        sender: QtWidgets.QPushButton = dict_sender_reverse.get(value)
        try:
            self.ui.swSavedSocial.slideToWidgetIndex(value)
            for key in dict_sender.keys():
                if sender == cur_sender:
                    break
                if key == sender:
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap(dict_sender_icon.get(key)[0]), QtGui.QIcon.Mode.Normal,
                                   QtGui.QIcon.State.Off)
                    key.setIcon(icon)
                    key.setIconSize(key.iconSize() * 1.01)
                elif key == cur_sender:
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap(dict_sender_icon.get(key)[1]), QtGui.QIcon.Mode.Normal,
                                   QtGui.QIcon.State.Off)
                    key.setIcon(icon)
                    key.setIconSize(key.iconSize() * 0.99)

        except Exception as ex:
            print(ex)

    @property
    def page_setting(self):
        return self.ui.swSetting.currentIndex()

    @page_setting.setter
    def page_setting(self, value: int):
        dict_sender: dict = {self.ui.btnSettingPageInstagram: 0,
                             self.ui.btnSettingPageLinkedin: 1,
                             self.ui.btnSettingPageTiktok: 2,
                             self.ui.btnSettingPageEmail: 3}
        dict_sender_reverse = {v: k for k, v in dict_sender.items()}
        cur_sender = dict_sender_reverse.get(self.page_setting)

        sender: QtWidgets.QPushButton = dict_sender_reverse.get(value)
        try:
            self.ui.swSetting.slideToWidgetIndex(value)
            for key in dict_sender.keys():
                if sender == cur_sender:
                    break
                if key == sender:
                    key.setIconSize(key.iconSize() * 1.2)
                elif key == cur_sender:
                    key.setIconSize(key.iconSize() / 1.2)

        except Exception as ex:
            print(ex)

    @property
    def loading(self):
        return self._loading

    @loading.setter
    def loading(self, value):
        if value:
            self.progress_bar_worker.start()
            self._loading = True
        else:
            self._loading = False
            self.progress_bar_worker.quit()
