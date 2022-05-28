from PyQt5 import QtGui, QtWidgets


class PixmapLayer(QtWidgets.QLabel):
    def __init__(self, pm_width, pm_height, fill):
        super(PixmapLayer, self).__init__()
        self.pm_width = pm_width
        self.pm_height = pm_height
        self.fill = fill
        self.createPixmap()

    def createPixmap(self):
        canvas = QtGui.QPixmap(self.pm_width, self.pm_height)
        canvas.fill(self.fill)
        self.setPixmap(canvas)
