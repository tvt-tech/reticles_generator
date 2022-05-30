from .layer import PixmapLayer
from PyQt5 import QtCore, QtGui
from reticle_types import HRuler, VRuler, Cross


class GridLayer(PixmapLayer):

    def erase(self):
        self.createPixmap()

    def draw(self, x0, y0, x1, y1, zoom):
        self.createPixmap()
        painter = QtGui.QPainter(self.pixmap())
        pen = QtGui.QPen(QtCore.Qt.white, 0.5, QtCore.Qt.SolidLine)

        font = QtGui.QFont("BankGothic Lt BT")
        font.setStyleStrategy(QtGui.QFont.NoAntialias)
        font.setPixelSize(11)
        painter.setFont(font)

        lx1 = x1 * zoom
        ly1 = y1 * zoom
        lxs = int(self.pm_width / 2 / lx1)
        lys = int(self.pm_height / 2 / ly1)

        st = 1
        if lx1 < 4.96 or ly1 < 4.96:
            st = 2

        defs = [painter, x0, y0, x1, y1, zoom]

        cr = [0, lxs, 0, 0, pen, 0b1111, True, True]

        Cross(*defs, *cr)

        g = [st, lxs * st, st, 0.5]
        HRuler(*defs, *g, pen=pen)
        HRuler(*defs, *g, pen=pen, flip_y=True)
        VRuler(*defs, *g, pen=pen)
        VRuler(*defs, *g, pen=pen, flip_x=True)

        g2 = [st * 5, 50, st * 5, 1]
        HRuler(*defs, *g2, pen=pen)
        HRuler(*defs, *g2, pen=pen, flip_y=True)
        VRuler(*defs, *g2, pen=pen)
        VRuler(*defs, *g2, pen=pen, flip_x=True)

        n = [st * 10, st * 10 * 5, st * 10, 0.75]
        nd = dict(mode='ruler', pen=pen)

        HRuler(*defs, *n, **nd, y_offset=3)
        HRuler(*defs, *n, **nd, y_offset=3, flip_y=True)

        VRuler(*defs, *n, **nd, x_offset=3)
        VRuler(*defs, *n, **nd, x_offset=3, flip_x=True)

        for i in range(-lys, lys):
            HRuler(*defs, *g, mode='dot', y_offset=i, pen=pen)
            HRuler(*defs, *g, mode='dot', y_offset=i, pen=pen, flip_y=True)
