from enum import IntEnum

from PyQt5.QtCore import QRectF, Qt, QLineF, QPointF
from PyQt5.QtGui import QPainter, QPixmap, QPen, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsEllipseItem, QStyleOptionGraphicsItem, QWidget, QGraphicsLineItem, \
    QGraphicsRectItem, QGraphicsItem, QGraphicsItemGroup


class ItemType(IntEnum):
    Point = 1
    Line = 2
    Rect = 3
    Ellipse = 4
    Circle = 5
    Polygon = 6
    Text = 7
    Ruler = 8


class CustomPen:
    GridH1 = QPen(Qt.darkMagenta, 0.2, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    GridH2 = QPen(Qt.darkMagenta, 0.15, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    GridH3 = QPen(Qt.darkMagenta, 0.05, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    GridH4 = QPen(Qt.darkMagenta, 0.02, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    GridH5 = QPen(Qt.darkMagenta, 0.01, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    Pencil = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)
    PencilVect = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)
    PointVect = QPen(Qt.transparent, 0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    Eraser = QPen(Qt.transparent, 1, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)
    Line = QPen(Qt.black, 1, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
    LineVect = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    Ellipse = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)


class HoveredGraphicsItem:

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        pen = self.pen()
        pen.setColor(Qt.blue)
        self.setPen(pen)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        pen = self.pen()
        pen.setColor(self._default_pen_color)
        self.setPen(pen)

    def toJson(self, click_x, click_y, multiplier) -> dict:
        return {}

    @staticmethod
    def fromJson(px_at_mil_h: float,
                 px_at_mil_v: float,
                 p1: tuple[float, float],
                 p2: tuple[float, float],
                 step: float = 1, *args, **kwargs):
        return


class SmoothLineItem(QGraphicsLineItem):
    def __init__(self, line: QLineF, pen: QPen, parent=None):
        super(SmoothLineItem, self).__init__(parent)
        self.setLine(line)
        self.setPen(pen)
        self.setPos(-0.5, -0.5)

    def boundingRect(self) -> QRectF:
        return self.scene().sceneRect()

    def redraw_pix(self):
        pixmap = QPixmap(self.scene().width(), self.scene().height())
        pixmap.fill(Qt.transparent)
        pix_painter = QPainter(pixmap)
        pix_painter.drawLine(self.line())
        return pixmap

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.setPen(self.pen())
        pixmap = self.redraw_pix()
        painter.drawPixmap(self.boundingRect(), pixmap, self.boundingRect())


class SmoothRectItem(QGraphicsRectItem):
    def __init__(self, rect: QRectF, pen: QPen, parent=None):
        super(SmoothRectItem, self).__init__(parent)
        self.setRect(rect)
        self.setPen(pen)
        self.setPos(-0.5, -0.5)

    def boundingRect(self) -> QRectF:
        return self.scene().sceneRect()

    def redraw_pix(self):
        pixmap = QPixmap(self.scene().width(), self.scene().height())
        pixmap.fill(Qt.transparent)
        pix_painter = QPainter(pixmap)
        pix_painter.drawRect(self.rect())
        return pixmap

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.setPen(self.pen())
        pixmap = self.redraw_pix()
        pixmap_rect = QRectF(pixmap.rect())
        painter.drawPixmap(self.boundingRect(), pixmap, pixmap_rect)


class SmoothEllipseItem(QGraphicsEllipseItem):
    def __init__(self, rect: QRectF, pen: QPen, parent=None):
        super(SmoothEllipseItem, self).__init__(parent)
        self.setRect(rect)
        self.setPen(pen)
        self.setPos(-0.5, -0.5)

    def boundingRect(self) -> QRectF:
        return self.scene().sceneRect()

    def redraw_pix(self):
        pixmap = QPixmap(self.scene().width(), self.scene().height())
        pixmap.fill(Qt.transparent)
        pix_painter = QPainter(pixmap)
        pix_painter.drawEllipse(self.rect())
        return pixmap

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.setPen(self.pen())
        pixmap = self.redraw_pix()
        pixmap_rect = QRectF(pixmap.rect())
        painter.drawPixmap(self.boundingRect(), pixmap, pixmap_rect)


class PointItem(QGraphicsItem, HoveredGraphicsItem):
    def __init__(self, point: 'QPointF', pen: QPen, brush: 'QBrush' = Qt.black, parent=None):
        super(PointItem, self).__init__(parent)
        self.setAcceptHoverEvents(True)
        self._default_pen_color = pen.color()
        self._pen = pen
        self._brush = brush
        self._p = point
        self._x = point.x()
        self._y = point.y()

    def setPen(self, p: QPen):
        self._pen = p

    def pen(self):
        return self._pen

    def boundingRect(self) -> QRectF:
        return QRectF(-0.5, -0.5, 1, 1)

    def paint(self, painter: 'QPainter', option: 'QStyleOptionGraphicsItem', widget: 'QWidget') -> None:
        painter.setPen(self._pen)
        painter.drawPoint(self._p.x(), self._p.y())

    def x(self):
        return self._p.x()

    def y(self):
        return self._p.y()

    def p(self):
        return self._p

    def brush(self):
        return self._brush

    def toJson(self, click_x, click_y, multiplier):
        return {
            't': ItemType.Point,
            'step': 0.0,
            'p1': (
                self.x() * click_x / multiplier,
                self.y() * click_y / multiplier
            ),
            'p2': (0.0, 0.0),
            'pen': 1,
        }

    @staticmethod
    def fromJson(px_at_mil_h: float,
                 px_at_mil_v: float,
                 p1: tuple[float, float],
                 p2: tuple[float, float],
                 step: float = 1, *args, **kwargs):
        point = QPointF(px_at_mil_h * p1[0], px_at_mil_v * p1[1])
        pen = CustomPen.PencilVect
        return PointItem(point, pen)


# class RulerItem(QGraphicsRectItem, HoveredGraphicsItem):
#     def __init__(self, r: QRectF, step: float, pen: QPen, brush: 'QBrush' = Qt.black, parent=None):
#         super(RulerItem, self).__init__(r, parent)
#         # self.setAcceptHoverEvents(True)
#         self.setFiltersChildEvents(False)
#         self.setPen(pen)
#         self._default_pen_color = pen.color()
#         self.setBrush(brush)
#         self._step = step
#         self.items_group = None
#
#     def step(self):
#         return self._step
#
#     def paint(self, painter: 'QPainter', option: 'QStyleOptionGraphicsItem', widget: 'QWidget') -> None:
#         # super(RulerItem, self).paint(painter, option, widget)
#         rect = self.rect()
#
#         for item in self.scene().items():
#             if item.parentItem() == self:
#                 self.scene().removeItem(item)
#
#         if rect.width() > rect.height():
#             line_count = abs(int(rect.width() / self._step)) + 1
#             for i in range(line_count):
#                 x = i * self._step + rect.x()
#                 if rect.height() > 0:
#                     line = QLineF(x, rect.center().y() - rect.height() / 2, x, rect.center().y() + rect.height() / 2)
#                     line_item = self.scene().addLine(line, self.pen())
#                     line_item.setParentItem(self)
#                 else:
#                     point = QPointF(x, rect.center().y())
#                     point_item = self.scene().addPoint(point, self.pen())
#                     point_item.setParentItem(self)
#
#         elif rect.width() < rect.height():
#             line_count = abs(int(rect.height() / self._step)) + 1
#             for i in range(line_count):
#                 y = i * self._step + rect.y()
#                 if rect.width() > 0:
#                     line = QLineF(rect.center().x() - rect.width() / 2, y, rect.center().x() + rect.width() / 2, y)
#                     line_item = self.scene().addLine(line, self.pen())
#                     line_item.setParentItem(self)
#                 else:
#                     point = QPointF(rect.center().x(), y)
#                     point_item = self.scene().addPoint(point, self.pen())
#                     point_item.setParentItem(self)
#
#     def toJson(self, click_x, click_y, multiplier):
#         return {
#             't': ItemType.Ruler,
#             'step': self.step() * click_x / multiplier,
#             'p1': (
#                 self.rect().x() * click_x / multiplier,
#                 self.rect().y() * click_y / multiplier
#             ),
#             'p2': (
#                 self.rect().width() * click_x / multiplier,
#                 self.rect().height() * click_y / multiplier
#             ),
#             'mode': 'pt',
#             'pen': 1,
#         }


class RulerGroup(QGraphicsItemGroup):
    def __init__(self, r: QRectF, step: float, pen: QPen, brush: 'QBrush' = Qt.transparent, parent=None):
        super(RulerGroup, self).__init__(parent)
        self.setAcceptHoverEvents(True)
        self._default_pen_color = pen.color()
        self._step = step
        self._pen = pen
        self._brush = brush
        self._rect = None
        self.setRect(r)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self._pen.setColor(Qt.blue)
        for item in self.childItems():
            item.setPen(self._pen)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self._pen.setColor(self._default_pen_color)
        for item in self.childItems():
            item.setPen(self._pen)

    def boundingRect(self) -> QRectF:
        if self.rect().width() > self.rect().height():
            return QRectF(self.rect().x(), self.rect().y(), self.rect().width(), 0)
        elif self.rect().width() < self.rect().height():
            return QRectF(self.rect().x(), self.rect().y(), 0, self.rect().height())
        return QRectF()

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem', widget: QWidget = None) -> None:
        pass

    def setRect(self, r: QRectF):
        self._rect = r
        rect = self.rect()
        for item in self.childItems():
            self.scene().removeItem(item)

        if rect.width() > rect.height():
            line_count = abs(int(rect.width() / self._step)) + 1
            for i in range(line_count):
                x = i * self._step + rect.x()
                if rect.height() > 0:
                    line = QLineF(x, rect.center().y() - rect.height() / 2, x, rect.center().y() + rect.height() / 2)
                    line_item = LineItem(line, self._pen)
                    self.addToGroup(line_item)
                else:
                    point = QPointF(x, rect.center().y())
                    point_item = PointItem(point, self._pen)
                    self.addToGroup(point_item)

        elif rect.width() < rect.height():
            line_count = abs(int(rect.height() / self._step)) + 1
            for i in range(line_count):
                y = i * self._step + rect.y()
                if rect.width() > 0:
                    line = QLineF(rect.center().x() - rect.width() / 2, y, rect.center().x() + rect.width() / 2, y)
                    line_item = LineItem(line, self._pen)
                    self.addToGroup(line_item)
                else:
                    point = QPointF(rect.center().x(), y)
                    point_item = PointItem(point, self._pen)
                    self.addToGroup(point_item)

    def rect(self):
        return self._rect

    def setPen(self, p: QPen):
        self._pen = p

    def pen(self):
        return self._pen

    def setBrush(self, b: 'QBrush'):
        self._brush = b

    def brush(self):
        return self._brush

    def setStep(self, step: float):
        self._step = step

    def step(self):
        return self._step

    def toJson(self, click_x, click_y, multiplier):
        return {
            't': ItemType.Ruler,
            'step': self.step() * click_x / multiplier,
            'p1': (
                self.rect().x() * click_x / multiplier,
                self.rect().y() * click_y / multiplier
            ),
            'p2': (
                self.rect().width() * click_x / multiplier,
                self.rect().height() * click_y / multiplier
            ),
            'pen': 1,
        }

    @staticmethod
    def fromJson(px_at_mil_h: float,
                 px_at_mil_v: float,
                 p1: tuple[float, float],
                 p2: tuple[float, float],
                 step: float, *args, **kwargs):
        s = step * px_at_mil_h if p2[0] > p2[1] else step * px_at_mil_v
        rect = QRectF(px_at_mil_h * p1[0], px_at_mil_v * p1[1], px_at_mil_h * p2[0], px_at_mil_v * p2[1])
        pen = CustomPen.LineVect
        return RulerGroup(rect, s, pen)


class LineItem(QGraphicsLineItem, HoveredGraphicsItem):
    def __init__(self, line: QLineF, pen: QPen, parent=None):
        super(LineItem, self).__init__(line)
        self.setParentItem(parent)
        self.setPen(pen)
        self._default_pen_color = pen.color()
        self.setAcceptHoverEvents(True)

    def toJson(self, click_x, click_y, multiplier):
        return {
            't': ItemType.Line,
            'step': 0.0,
            'p1': (
                self.line().x1() * click_x / multiplier,
                self.line().y1() * click_y / multiplier
            ),
            'p2': (
                self.line().x2() * click_x / multiplier,
                self.line().y2() * click_y / multiplier
            ),
            'pen': 1,
        }

    @staticmethod
    def fromJson(px_at_mil_h: float,
                 px_at_mil_v: float,
                 p1: tuple[float, float],
                 p2: tuple[float, float],
                 step: float = 1, *args, **kwarg):
        line = QLineF(px_at_mil_h * p1[0], px_at_mil_v * p1[1], px_at_mil_h * p2[0], px_at_mil_v * p2[1])
        pen = CustomPen.LineVect
        return LineItem(line, pen)


class RectItem(QGraphicsRectItem, HoveredGraphicsItem):
    def __init__(self, rect: QRectF, pen: QPen, brush: 'QBrush' = Qt.transparent):
        super(RectItem, self).__init__(rect)
        self.setPen(pen)
        self._default_pen_color = pen.color()
        self.setBrush(brush)
        self.setAcceptHoverEvents(True)

    def toJson(self, click_x, click_y, multiplier):
        return {
            't': ItemType.Rect,
            'step': 0.0,
            'p1': (
                self.rect().x() * click_x / multiplier,
                self.rect().y() * click_y / multiplier
            ),
            'p2': (
                self.rect().width() * click_x / multiplier,
                self.rect().height() * click_y / multiplier
            ),
            'pen': 1,
        }

    @staticmethod
    def fromJson(px_at_mil_h: float,
                 px_at_mil_v: float,
                 p1: tuple[float, float],
                 p2: tuple[float, float],
                 step: float = 1, *args, **kwargs):
        rect = QRectF(px_at_mil_h * p1[0], px_at_mil_v * p1[1], px_at_mil_h * p2[0], px_at_mil_v * p2[1])
        pen = CustomPen.LineVect
        return RectItem(rect, pen)


class EllipseItem(QGraphicsEllipseItem, HoveredGraphicsItem):
    def __init__(self, rect: QRectF, pen: QPen, brush: 'QBrush' = Qt.transparent):
        super(EllipseItem, self).__init__(rect)
        self.setPen(pen)
        self._default_pen_color = pen.color()
        self.setBrush(brush)
        self.setAcceptHoverEvents(True)

    def toJson(self, click_x, click_y, multiplier):
        return {
            't': ItemType.Ellipse if self.rect().width() != self.rect().height() else ItemType.Circle,
            'step': 0.0,
            'p1': (
                self.rect().x() * click_x / multiplier,
                self.rect().y() * click_y / multiplier
            ),
            'p2': (
                self.rect().width() * click_x / multiplier,
                self.rect().height() * click_y / multiplier
            ),
            'pen': 1,
        }

    @staticmethod
    def fromJson(px_at_mil_h: float,
                 px_at_mil_v: float,
                 p1: tuple[float, float],
                 p2: tuple[float, float],
                 step: float = 1, *args, **kwargs):
        rect = QRectF(px_at_mil_h * p1[0], px_at_mil_v * p1[1], px_at_mil_h * p2[0], px_at_mil_v * p2[1])
        pen = CustomPen.PencilVect
        return EllipseItem(rect, pen)


class SelectorItem(QGraphicsRectItem):
    def __init__(self, r: QRectF, view_scale: tuple[float, float, float] = None, parent=None):
        super(SelectorItem, self).__init__(r, parent)
        self.setPen(QPen(Qt.blue, 0.2, Qt.SolidLine, Qt.RoundCap))
        self.setBrush(QColor(0, 0, 255, 32))
        self._view_scale = view_scale

    def paint(self, painter: 'QPainter', option: 'QStyleOptionGraphicsItem', widget: 'QWidget') -> None:
        super(SelectorItem, self).paint(painter, option, widget)
        painter.drawLine(self.rect().topLeft(), self.rect().bottomRight())
        painter.drawEllipse(self.rect().center(), 0.3, 0.3)
        if self._view_scale:
            w = round(self.rect().width() * self._view_scale[0] / self._view_scale[2], 2)
            h = round(self.rect().height() * self._view_scale[1] / self._view_scale[2], 2)
            painter.drawText(self.rect(), f'({w}, {h})')
