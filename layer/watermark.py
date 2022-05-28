from .layer import PixmapLayer
from PyQt5 import QtCore, QtGui


class Watermark(PixmapLayer):

    def draw(self, text):
        self.createPixmap()
        painter = QtGui.QPainter(self.pixmap())
        pen = QtGui.QPen(QtCore.Qt.darkMagenta, 1, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        font = QtGui.QFont("BankGothic Lt BT")
        font.setStyleStrategy(QtGui.QFont.NoAntialias)
        font.setPixelSize(11)

        painter.setFont(font)

        painter.drawText(QtCore.QPoint(40, 60), text)
