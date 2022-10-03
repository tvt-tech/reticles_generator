import typing

from PyQt5.QtCore import QSize, Qt, QRectF, QPoint, QLine, QPointF, QSizeF, QLineF
from PyQt5.QtGui import QPixmap, QFontMetrics, QFont
from PyQt5.QtWidgets import QGraphicsItem

from .center_painter import CenterPainter
from .custom_graphics_item import ItemType

import math
from .grid_step import rlist


class GraphicsCanvas(QGraphicsItem):
    def __init__(self, size: QSize, parent=None):
        super(GraphicsCanvas, self).__init__(parent)

        self.pixmap = None
        self.pixmap = QPixmap(size.width(), size.height())
        self.pixmap.fill(Qt.transparent)

    def setPixmap(self, pixmap):
        self.pixmap = pixmap
        self.scene().update()

    def boundingRect(self) -> QRectF:
        return self.scene().sceneRect()

    def paint(self, painter: 'QPainter',
              option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional['QWidget'] = ...) -> None:
        pixmap_rect = QRectF(self.pixmap.rect())
        painter.drawPixmap(self.boundingRect(), self.pixmap, pixmap_rect)

    def clear_pixmap(self):
        self.pixmap = QPixmap(self.scene().width(), self.scene().height())
        self.pixmap.fill(Qt.transparent)
        self.scene().update()

    def drawPoint(self, p: 'QPoint', pen: 'QPen'):
        painter = CenterPainter(self.pixmap)
        painter.setCompositionMode(CenterPainter.CompositionMode_Source)
        painter.setPen(pen)
        painter.drawPoint(p)
        self.scene().update()

    def drawLine(self, l: 'QLine', pen: 'QPen'):
        painter = CenterPainter(self.pixmap)
        painter.setCompositionMode(CenterPainter.CompositionMode_Source)
        painter.setPen(pen)
        painter.drawLine(l)
        self.scene().update()

    def drawRect(self, r: 'QRect', pen: 'QPen'):
        painter = CenterPainter(self.pixmap)
        painter.setCompositionMode(CenterPainter.CompositionMode_Source)
        painter.setPen(pen)
        painter.drawRect(r)
        self.scene().update()

    def drawEllipse(self, r: 'QRect', pen: 'QPen'):
        painter = CenterPainter(self.pixmap)
        painter.setCompositionMode(CenterPainter.CompositionMode_Source)
        painter.setPen(pen)
        painter.drawEllipse(r)
        self.scene().update()

    def drawPolygon(self, p: 'QPolygon', pen: 'QPen'):
        painter = CenterPainter(self.pixmap)
        painter.setCompositionMode(CenterPainter.CompositionMode_Source)
        painter.setPen(pen)
        painter.drawPolygon(p)
        self.scene().update()

    def drawPointC(self, p: 'QPoint', pen: 'QPen'):
        painter = CenterPainter(self.pixmap)
        painter.setCompositionMode(CenterPainter.CompositionMode_Source)
        painter.setPen(pen)
        painter.drawPointC(p)
        self.scene().update()

    def drawLineC(self, l: 'QLine', pen: 'QPen'):
        painter = CenterPainter(self.pixmap)
        painter.setCompositionMode(CenterPainter.CompositionMode_Source)
        painter.setPen(pen)
        painter.drawLineC(l)
        self.scene().update()

    def drawRectC(self, r: 'QRectF', pen: 'QPen'):
        painter = CenterPainter(self.pixmap)
        painter.setCompositionMode(CenterPainter.CompositionMode_Source)
        painter.setPen(pen)
        painter.drawRectC(r)
        self.scene().update()

    def drawEllipseC(self, r: 'QRect'=None, pen: 'QPen'=None, p: 'QPointF'=None, rx: float = None, ry: float = None):
        painter = CenterPainter(self.pixmap)
        painter.setCompositionMode(CenterPainter.CompositionMode_Source)
        painter.setPen(pen)
        painter.drawEllipseC(r, p, rx, ry)
        self.scene().update()

    def drawPolygonC(self, p: 'QPolygon', pen: 'QPen'):
        painter = CenterPainter(self.pixmap)
        painter.setCompositionMode(CenterPainter.CompositionMode_Source)
        painter.setPen(pen)
        painter.drawPolygonC(p)
        self.scene().update()

    def drawTextC(self, p: 'QPoint', s: str, font: 'QFont'):
        painter = CenterPainter(self.pixmap)
        painter.setCompositionMode(CenterPainter.CompositionMode_Source)
        painter.setFont(font)
        painter.drawTextC(p, s)
        self.scene().update()


class Rasterizer:
    def __init__(self,min_mil_h_step, min_mil_v_step, px_at_mil_h, px_at_mil_v, t, p1, p2, text, **kwargs):
        self.t = t
        self.p1 = p1
        self.p2 = p2
        self.text = text
        self._min_mil_h_step = min_mil_h_step
        self._min_mil_v_step = min_mil_v_step
        self._px_at_mil_h = px_at_mil_h
        self._px_at_mil_v = px_at_mil_v
        self.font = None

    @staticmethod
    def round_point_to_step(v, step):
        if abs(v) < step:
            return False
        mod = abs(v % step)
        if mod > 0:

            # if step == 0.1 and mod / 0.1 > mod / 0.2:
            #     step = 0.2

            # if step == 0.2 and mod / 0.2 > mod / 0.25:
            #     step = 0.25

            # if step == 0.25 and mod / 0.25 > mod / 0.3:
            #     step = 0.3
            # if step == 0.3 and mod / 0.3 > mod / 0.5:
            #     step = 0.5

            if step == 0.25 and mod / 0.25 > mod / 0.5:
                step = 0.5
            elif step == 0.2 and mod / 0.2 > mod / 0.25:
                step = 0.25

            return round(v / step) * step
        return None

    def as_rline(self):
        p1 = list(self.p1)
        p2 = list(self.p2)

        if p1[0] == p2[0] != 0:
            r = self.round_point_to_step(p1[0], self._min_mil_h_step)
            if r:
                p1 = [r, p1[1]]
                p2 = [r, p2[1]]
            elif r is not None:
                return

        if p1[1] == p2[1] != 0:
            r = self.round_point_to_step(p1[1], self._min_mil_v_step)
            if r:
                p1 = [p1[0], r]
                p2 = [p2[0], r]
            elif r is not None:
                return

        p1 = [self._px_at_mil_h * p1[0], self._px_at_mil_v * p1[1]]
        p2 = [self._px_at_mil_h * p2[0], self._px_at_mil_v * p2[1]]

        p1[0] += (1 if p1[0] > 0 else 0 if p1[0] < 0 else 0)
        p1[1] += (1 if p1[1] > 0 else 0 if p1[1] < 0 else 0)
        p2[0] += (1 if p2[0] > 0 else 0 if p2[0] < 0 else 0)
        p2[1] += (1 if p2[1] > 0 else 0 if p2[1] < 0 else 0)

        p1 = QPointF(*p1)
        p2 = QPointF(*p2)

        return QLineF(p1, p2)

    def as_line(self):
        p1 = list(self.p1)
        p2 = list(self.p2)
        p1 = [self._px_at_mil_h * p1[0], self._px_at_mil_v * p1[1]]
        p2 = [self._px_at_mil_h * p2[0], self._px_at_mil_v * p2[1]]

        p1[0] += (1 if p1[0] > 0 else 0 if p1[0] < 0 else 0)
        p1[1] += (1 if p1[1] > 0 else 0 if p1[1] < 0 else 0)
        p2[0] += (1 if p2[0] > 0 else 0 if p2[0] < 0 else 0)
        p2[1] += (1 if p2[1] > 0 else 0 if p2[1] < 0 else 0)

        p1 = QPointF(*p1)
        p2 = QPointF(*p2)

        return QLineF(p1, p2)

    def as_point(self):
        x, y = self.p1

        rx = self.round_point_to_step(x, self._min_mil_h_step) if x != 0 else None
        if rx:
            x = rx

        ry = self.round_point_to_step(y, self._min_mil_h_step) if y != 0 else None
        if ry:
            y = ry

        p = [int(self._px_at_mil_h * x), int(self._px_at_mil_v * y)]
        p[0] += (1 if p[0] > 0 else -1 if p[0] < 0 else 0)
        p[1] += (1 if p[1] > 0 else -1 if p[1] < 0 else 0)
        return QPointF(*p)

    def as_text(self):
        x, y = self.p1

        p = [int(self._px_at_mil_h * x), int(self._px_at_mil_v * y)]
        p[0] += (1 if p[0] > 0 else -1 if p[0] < 0 else 0)
        p[1] += (1 if p[1] > 0 else -1 if p[1] < 0 else 0)
        point = QPoint(*p)

        self.font = QFont('BankGothic Lt BT')
        self.font.setStyleStrategy(QFont.NoAntialias)
        self.font.setPixelSize(11)

        fm = QFontMetrics(self.font)
        w = fm.width(self.text)
        h = fm.height()

        point = point - QPoint(w / 2, - h / 3)
        if h >= self._px_at_mil_v * 0.75:
            return
        elif fm.width('W') >= self._px_at_mil_h * 0.75:
            return
        return point

    def as_ellipse(self):
        x1, y1 = self.p1
        x2, y2 = self.p2

        milrect = QRectF(QPointF(x1, y1), QSizeF(x2, y2))

        cx = milrect.center().x()
        rcpx = self.round_point_to_step(cx, self._min_mil_h_step) if cx != 0 else None
        if rcpx:
            cx = rcpx

        cy = milrect.center().y()
        rcpy = self.round_point_to_step(cy, self._min_mil_v_step) if cy != 0 else None
        if rcpy:
            cy = rcpy

        rx = milrect.width() / 2
        # rradx = round_point_to_step(rx, self._min_mil_h_step) if rx != 0 else None
        # if rradx:
        #     rx = rradx

        ry = milrect.height() / 2
        # rrady = round_point_to_step(ry, self._min_mil_v_step) if ry != 0 else None
        # if rrady:
        #     ry = rrady

        cx *= self._px_at_mil_h
        cy *= self._px_at_mil_v
        rx *= self._px_at_mil_h
        ry *= self._px_at_mil_v

        cx += 0.5
        cy += 0.5
        rx = abs(rx) + 0.5
        ry = abs(ry) + 0.5

        return cx, cy, rx, ry

    def as_rect(self):
        x1, y1 = self.p1
        x2, y2 = self.p2

        milrect = QRectF(QPointF(x1, y1), QSizeF(x2, y2))

        cx = milrect.center().x()
        rcpx = self.round_point_to_step(cx, self._min_mil_h_step) if cx != 0 else None
        if rcpx:
            cx = rcpx

        cy = milrect.center().y()
        rcpy = self.round_point_to_step(cy, self._min_mil_v_step) if cy != 0 else None
        if rcpy:
            cy = rcpy

        rx = milrect.width() / 2
        rradx = self.round_point_to_step(rx, self._min_mil_h_step) if rx != 0 else None
        if rradx:
            rx = rradx

        ry = milrect.height() / 2
        rrady = self.round_point_to_step(ry, self._min_mil_v_step) if ry != 0 else None
        if rrady:
            ry = rrady

        cx *= self._px_at_mil_h
        cy *= self._px_at_mil_v
        rx *= self._px_at_mil_h
        ry *= self._px_at_mil_v
        # rx -= 0.5
        # ry -= 0.5

        cx += (1 if cx > 0 else -1 if cx < 0 else 0)
        cy += (1 if cy > 0 else -1 if cy < 0 else 0)

        return cx, cy, rx, ry

