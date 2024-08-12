from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter, QBrush, QColor, QConicalGradient
from PyQt5.QtWidgets import QApplication, QWidget


class PipelineGauge(QWidget):

    def __init__(self):
        super().__init__()

        self.value = 50  # initial value (0-100)
        self.min_value = -40
        self.max_value = 85
        self.gauge_width = 25
        self.gauge_height = 90
        self.gauge_height = 90

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the gauge background
        gauge_rect = QRectF(10, 10, self.gauge_width, self.gauge_height)
        painter.setBrush(QBrush(QColor.fromRgb(22, 25, 29)))
        painter.drawRoundedRect(gauge_rect, 10, 10)

        # Draw the pipeline
        pipeline_rect = QRectF(15, 15, self.gauge_width - 10, self.gauge_height - 30)
        grad = QConicalGradient(QPointF(0, 0), -100.0)
        grad.setColorAt(.00, Qt.green)
        grad.setColorAt(.15, Qt.yellow)
        grad.setColorAt(.2, Qt.red)
        painter.setBrush(grad)
        painter.drawRoundedRect(pipeline_rect, 10, 10)

        # Draw the value indicator
        value_rect = QRectF(15, 15 + (self.gauge_height - 30) * (1 - self.value / 100), self.gauge_width - 10, 10)
        painter.setBrush(QColor.fromRgb(52, 59, 71))
        painter.drawRoundedRect(value_rect, 10, 10)

    def setValue(self, value):
        value = self.normalize_scale_x(value, self.min_value, self.max_value, 0, 100)
        if value in range(0, 101):
            self.value = value
            self.update()

    @staticmethod
    def normalize_scale_x(OldValue, OldMin, OldMax, NewMin, NewMax):
        """Normalizing data"""
        return (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin


if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets

    app = QApplication(sys.argv)
    frame = QtWidgets.QFrame()
    frame.setObjectName('frame')
    frame.setStyleSheet('''#frame {background-color: black;}''')
    # frame.setMinimumSize(2000, 1600)
    layout = QtWidgets.QHBoxLayout(frame)

    gauge = PipelineGauge()
    gauge.setValue(100)
    # gauge.resize(50, 250)
    layout.addWidget(gauge)
    frame.show()

    # gauge.setValue(100)

    sys.exit(app.exec_())
