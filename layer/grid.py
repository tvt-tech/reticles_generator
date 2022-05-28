from .layer import PixmapLayer
from PyQt5 import QtCore, QtGui
from reticle_types import HRuler, VRuler


class GridLayer(PixmapLayer):

    def erase(self):
        self.createPixmap()

    def draw(self, x0, y0, x1, y1, zoom):
        self.createPixmap()
        painter = QtGui.QPainter(self.pixmap())
        pen = QtGui.QPen(QtCore.Qt.white, 0.5, QtCore.Qt.SolidLine)

        lx1 = x1 * zoom
        ly1 = y1 * zoom
        lxs = int(self.pm_width / 2 / lx1)
        lys = int(self.pm_height / 2 / ly1)

        st = 1
        if lx1 < 4.96 or ly1 < 4.96:
            st = 2

        cross = {'margin': 0, 'size': 0.5, 'mask': 0b1111, 'bind': True, 'zoom': True,
                 'min_zoom': 1, 'max_zoom': 7, 'pen': pen}

        HRuler(painter, x0, y0, x1, y1, zoom, -lxs, lxs, st, 5,
               mode='cross', x_offset=0, y_offset=0, pen=pen, cross=cross)

        VRuler(painter, x0, y0, x1, y1, zoom, -lys, lys, st, 5,
               mode='cross', x_offset=0, y_offset=0, pen=pen, cross=cross)

        for i in range(-lys, lys):
            HRuler(painter, x0, y0, x1, y1, zoom, -lxs, lxs, st, 1,
                   mode='dot', x_offset=0, y_offset=i, pen=pen)
