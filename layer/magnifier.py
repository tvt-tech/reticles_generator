from PyQt5 import QtCore, QtWidgets, QtGui


class MagnifierEvent(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def pos(self):
        return QtCore.QPoint(self.x, self.y)


class Magnifier(QtWidgets.QWidget):
    def __init__(self, pm_width, pm_height):
        super(Magnifier, self).__init__()
        self.pm_width = pm_width
        self.pm_height = pm_height

        self.is_pressed = False

        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.gridLayout)

        self.magnifier_back = QtWidgets.QLabel(self)
        magnifier = QtGui.QPixmap(128, 128)
        magnifier.fill(QtCore.Qt.gray)
        self.magnifier_back.setPixmap(magnifier)
        self.gridLayout.addWidget(self.magnifier_back, 0, 0)

        self.magnifier_grid = QtWidgets.QLabel(self)
        magnifier = QtGui.QPixmap(128, 128)
        self.magnifier_grid.setPixmap(magnifier)
        self.gridLayout.addWidget(self.magnifier_grid, 0, 0)

        self.magnifier = QtWidgets.QLabel(self)
        magnifier = QtGui.QPixmap(128, 128)
        self.magnifier.setPixmap(magnifier)
        self.gridLayout.addWidget(self.magnifier, 0, 0)


    def draw(self, event, label, grid, is_map):
        if is_map:
            label_pos = label.mapFrom(label.parent(), event.pos())
        else:
            label_pos = event.pos()
        x, y = label_pos.x(), label_pos.y()

        x -= 32 if x >= 32 else 0
        y -= 32 if y >= 32 else 0
        if x >= self.pm_width - 64:
            x = self.pm_width - 64
        if y >= self.pm_height - 64:
            y = self.pm_height - 64

        rect = QtCore.QRect(x, y, 64, 64)
        pixmap = label.pixmap().copy(rect)
        pixmap = pixmap.scaled(128, 128)
        self.magnifier.setPixmap(pixmap)
        painter = QtGui.QPainter(self.magnifier.pixmap())
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
        painter.drawLine(0, 0, 0, 127)
        painter.drawLine(0, 0, 127, 0)
        painter.drawLine(127, 127, 127, 0)
        painter.drawLine(127, 127, 0, 127)

        rect = QtCore.QRect(x, y, 64, 64)
        pixmap = grid.pixmap().copy(rect)
        pixmap = pixmap.scaled(128, 128)
        self.magnifier_grid.setPixmap(pixmap)

        self.magnifier_event = MagnifierEvent(label_pos.x(), label_pos.y())

        if self.is_pressed:
            self.setMagnifierPos(label_pos)
        else:
            self.resetMagnifierPos()

    def resetMagnifierPos(self):
        self.move(self.pm_width - 128, 0)

    def setMagnifierPos(self, index):
        self.move(index.x() - 64, index.y() - 64)
