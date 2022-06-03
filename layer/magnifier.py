from PyQt5 import QtCore, QtWidgets, QtGui


class MagnifierEvent(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def pos(self):
        return QtCore.QPoint(self.x, self.y)


class Ui_Magnifier(object):
    def setupUi(self, parent):
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.gridLayout)

        self.magnifier_back = QtWidgets.QLabel(parent)
        magnifier = QtGui.QPixmap(self.w * 2, self.h * 2)
        magnifier.fill(QtCore.Qt.gray)
        self.magnifier_back.setPixmap(magnifier)
        self.gridLayout.addWidget(self.magnifier_back, 0, 0)

        self.magnifier_grid = QtWidgets.QLabel(parent)
        magnifier = QtGui.QPixmap(self.w * 2, self.h * 2)
        self.magnifier_grid.setPixmap(magnifier)
        self.gridLayout.addWidget(self.magnifier_grid, 0, 0)

        self.magnifier = QtWidgets.QLabel(parent)
        magnifier = QtGui.QPixmap(self.w * 2, self.h * 2)
        self.magnifier.setPixmap(magnifier)
        self.gridLayout.addWidget(self.magnifier, 0, 0)


class Magnifier(QtWidgets.QWidget, Ui_Magnifier):
    def __init__(self, pm_width, pm_height):
        super(Magnifier, self).__init__()
        self.pm_width = pm_width
        self.pm_height = pm_height
        self.is_pressed = False
        self.magnifier_event = None

        self.w = 80
        self.h = 60

        self.setupUi(self)


    def draw(self, event, label, grid, is_map):
        if is_map:
            label_pos = label.mapFrom(label.parent(), event.pos())
        else:
            label_pos = event.pos()
        x, y = label_pos.x(), label_pos.y()

        if x < self.w:
            x = self.w
        if x > self.pm_width - self.w:
            x = self.pm_width - self.w
        if y < self.h:
            y = self.h
        if y > self.pm_height - self.h:
            y = self.pm_height - self.h

        rect = QtCore.QRect(x - self.w/2, y - self.h/2, self.w, self.h)
        pixmap = label.pixmap().copy(rect)
        pixmap = pixmap.scaled(self.w * 2, self.h * 2)
        self.magnifier.setPixmap(pixmap)
        
        painter = QtGui.QPainter(self.magnifier.pixmap())
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
        painter.drawRect(0, 0, self.w * 2 - 1, self.h * 2 - 1)

        rect = QtCore.QRect(x - self.w/2, y - self.h/2, self.w, self.h)
        pixmap = grid.pixmap().copy(rect)
        pixmap = pixmap.scaled(self.w * 2, self.h * 2)
        self.magnifier_grid.setPixmap(pixmap)

        self.magnifier_event = MagnifierEvent(x, y)

        if self.is_pressed:
            self.setMagnifierPos(label_pos)
        else:
            self.resetMagnifierPos()

    def resetMagnifierPos(self):
        self.move(self.pm_width - self.w * 2, 0)

    def setMagnifierPos(self, index):

        if index.x() < self.w:
            x = self.w
        elif self.pm_width - self.w < index.x():
            x = self.pm_width - self.w
        else:
            x = index.x()

        if index.y() < self.h:
            y = self.h
        elif self.pm_height - self.h < index.y():
            y = self.pm_height - self.h
        else:
            y = index.y()


        self.move(x - self.w, y - self.h)
