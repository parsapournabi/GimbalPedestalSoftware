from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
from enum import Enum


class Direction(Enum):
    Left = 0
    Right = 1
    Up = 2
    Down = 3
    TopLef = 4
    TopRight = 5
    DownLeft = 6
    DownRight = 7


class Joystick(QWidget):
    def __init__(self, parent=None):
        super(Joystick, self).__init__(parent)
        self.setMinimumSize(120, 120)
        self.movingOffset = QPointF(0, 0)
        self.grabCenter = False
        self.__maxDistance = 50

    def paintEvent(self, event):
        painter = QPainter(self)
        bounds = QRectF(-self.__maxDistance, -self.__maxDistance, self.__maxDistance * 2,
                        self.__maxDistance * 2).translated(self._center())
        painter.drawEllipse(bounds)
        painter.setBrush(QColor.fromRgb(44, 49, 60))
        painter.drawEllipse(self._centerEllipse())

    def _centerEllipse(self):
        if self.grabCenter:
            return QRectF(-20, -20, 40, 40).translated(self.movingOffset)
        return QRectF(-20, -20, 40, 40).translated(self._center())

    def _center(self):
        return QPointF(self.width() / 2, self.height() / 2)

    def _boundJoystick(self, point):
        limitLine = QLineF(self._center(), point)
        if (limitLine.length() > self.__maxDistance):
            limitLine.setLength(self.__maxDistance)
        return limitLine.p2()

    def joystickDirection(self):
        if not self.grabCenter:
            return 0
        normVector = QLineF(self._center(), self.movingOffset)
        currentDistance = normVector.length()
        angle = normVector.angle()

        distance = min(currentDistance / self.__maxDistance, 1.0)
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
        # raise ValueError(f'Joystick movement angle is not correct!! {angle}')

    def mousePressEvent(self, ev):
        self.grabCenter = self._centerEllipse().contains(ev.pos())
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        return super().mousePressEvent(ev)

    def mouseReleaseEvent(self, event):
        self.grabCenter = False
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.movingOffset = QPointF(0, 0)
        self.update()

    def mouseMoveEvent(self, event):
        if self.grabCenter:
            self.movingOffset = self._boundJoystick(event.pos())
            self.update()
        self.joystickDirection()


if __name__ == '__main__':
    # Create main application window
    app = QApplication([])
    app.setStyle(QStyleFactory.create("Cleanlooks"))
    mw = QMainWindow()
    mw.setWindowTitle('Joystick example')

    # Create and set widget layout
    # Main widget container
    cw = QWidget()
    ml = QGridLayout()
    cw.setLayout(ml)
    mw.setCentralWidget(cw)

    # Create joystick
    joystick = Joystick()

    # ml.addLayout(joystick.get_joystick_layout(),0,0)
    ml.addWidget(joystick, 0, 0)

    mw.show()
    from PyQt5 import QtCore

    # Start Qt event loop unless running in interactive mode or using pyside.
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QApplication.instance().exec_()
