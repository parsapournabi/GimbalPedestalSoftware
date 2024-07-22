from src.main_dir.main import Main
from PyQt5.QtWidgets import QApplication
import sys

platform: str = 'WINDOWS'
version: str = '1.0add.0.0'

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main(platform=platform, version=version)
    sys.exit(app.exec_())
