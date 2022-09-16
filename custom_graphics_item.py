from enum import IntEnum

from PyQt5.QtCore import QRectF, Qt, QLineF, QPointF
from PyQt5.QtGui import QPainter, QPixmap, QPen
from PyQt5.QtWidgets import QGraphicsEllipseItem, QStyleOptionGraphicsItem, QWidget, QGraphicsLineItem, \
    QGraphicsRectItem, QGraphicsItem


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
        self.setPen(self.default_pen)

    def toJson(self) -> dict:
        return {}

    @staticmethod
    def fromJson(px_at_1_mil_h: float, px_at_1_mil_v: float, data: dict):
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
        self.default_pen = pen
        self._pen = pen
        self._brush = brush
        self._p = point
        self._x = point.x()
        self._y = point.y()

    def setPen(self, p: QPen):
        self._pen = p
        self.scene().update()

    def pen(self):
        return self._pen

    def boundingRect(self) -> QRectF:
        size = self._pen.width()
        return QRectF(self._p.x() - size, self._p.y() - size, 0.5, 0.5)

    def paint(self, painter: 'QPainter', option: 'QStyleOptionGraphicsItem', widget: 'QWidget') -> None:
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
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
            'p': (
                self.x() * click_x / multiplier,
                self.y() * click_y / multiplier
            ),
            'mode': 'pt',
            'pen': 1,
        }

    @staticmethod
    def fromJson(px_at_1_mil_h: float, px_at_1_mil_v: float, data: dict):
        if data['mode'] == 'pt':
            p = [px_at_1_mil_h * data['p'][0], px_at_1_mil_v * data['p'][1]]

        else:
            p = [data['p'][0], data['p'][1]]

        point = QPointF(*p)

        pen = CustomPen.PencilVect
        return PointItem(point, pen)


class RulerItem(QGraphicsRectItem, HoveredGraphicsItem):
    def __init__(self, r: QRectF, step: float, pen: QPen, brush: 'QBrush' = Qt.black, parent=None):
        super(RulerItem, self).__init__(r, parent)
        self.setAcceptHoverEvents(True)
        self.setPen(pen)
        self.default_pen = pen
        self.setBrush(brush)
        self._step = step
        self.items_group = None

    def step(self):
        return self._step

    def paint(self, painter: 'QPainter', option: 'QStyleOptionGraphicsItem', widget: 'QWidget') -> None:
        # super(RulerItem, self).paint(painter, option, widget)
        rect = self.rect()

        for item in self.scene().items():
            if item.parentItem() == self:
                self.scene().removeItem(item)

        if rect.width() > rect.height():
            line_count = abs(int(rect.width() / self._step)) + 1
            for i in range(line_count):
                x = i * self._step + rect.x()
                if rect.height() > 0:
                    line = QLineF(x, rect.center().y() - rect.height() / 2, x, rect.center().y() + rect.height() / 2)
                    line_item = self.scene().addLine(line, self.pen())
                    line_item.setParentItem(self)
                else:
                    point = QPointF(x, rect.center().y())
                    point_item = self.scene().addPoint(point, self.pen())
                    point_item.setParentItem(self)

        elif rect.width() < rect.height():
            line_count = abs(int(rect.height() / self._step)) + 1
            for i in range(line_count):
                y = i * self._step + rect.y()
                if rect.width() > 0:
                    line = QLineF(rect.center().x() - rect.width() / 2, y, rect.center().x() + rect.width() / 2, y)
                    line_item = self.scene().addLine(line, self.pen())
                    line_item.setParentItem(self)
                else:
                    point = QPointF(rect.center().x(), y)
                    point_item = self.scene().addPoint(point, self.pen())
                    point_item.setParentItem(self)

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
            'mode': 'pt',
            'pen': 1,
        }


class LineItem(QGraphicsLineItem, HoveredGraphicsItem):
    def __init__(self, line: QLineF, pen: QPen):
        super(LineItem, self).__init__(line)
        self.setPen(pen)
        self.default_pen = pen
        self.setAcceptHoverEvents(True)

    def toJson(self, click_x, click_y, multiplier):
        return {
            't': ItemType.Line,
            'p1': (
                self.line().x1() * click_x / multiplier,
                self.line().y1() * click_y / multiplier
            ),
            'p2': (
                self.line().x2() * click_x / multiplier,
                self.line().y2() * click_y / multiplier
            ),
            'mode': 'pt',
            'pen': 1,
        }

    @staticmethod
    def fromJson(px_at_1_mil_h: float, px_at_1_mil_v: float, data: dict):
        # if data['mode'] == 'pt':
        p1 = [px_at_1_mil_h * data['p1'][0], px_at_1_mil_v * data['p1'][1]]
        p2 = [px_at_1_mil_h * data['p2'][0], px_at_1_mil_v * data['p2'][1]]
        line = QLineF(*p1, *p2)
        pen = CustomPen.PencilVect
        return LineItem(line, pen)


class RectItem(QGraphicsRectItem, HoveredGraphicsItem):
    def __init__(self, rect: QRectF, pen: QPen, brush: 'QBrush' = Qt.transparent):
        super(RectItem, self).__init__(rect)
        self.setPen(pen)
        self.default_pen = pen
        self.setBrush(brush)
        self.setAcceptHoverEvents(True)

    def toJson(self, click_x, click_y, multiplier):
        return {
            't': ItemType.Rect,
            'p1': (
                self.rect().x() * click_x / multiplier,
                self.rect().y() * click_y / multiplier
            ),
            'p2': (
                self.rect().width() * click_x / multiplier,
                self.rect().height() * click_y / multiplier
            ),
            'mode': 'pt',
            'pen': 1,
        }


class EllipseItem(QGraphicsEllipseItem, HoveredGraphicsItem):
    def __init__(self, rect: QRectF, pen: QPen, brush: 'QBrush' = Qt.transparent):
        super(EllipseItem, self).__init__(rect)
        self.setPen(pen)
        self.default_pen = pen
        self.setBrush(brush)
        self.setAcceptHoverEvents(True)

    def toJson(self, click_x, click_y, multiplier):
        return {
            't': ItemType.Ellipse if self.rect().width() != self.rect().height() else ItemType.Circle,
            'p1': (
                self.rect().x() * click_x / multiplier,
                self.rect().y() * click_y / multiplier
            ),
            'p2': (
                self.rect().width() * click_x / multiplier,
                self.rect().height() * click_y / multiplier
            ),
            'mode': 'pt',
            'pen': 1,
        }


class SelectorItem(QGraphicsRectItem):
    def __init__(self, r: QRectF, parent=None):
        super(SelectorItem, self).__init__(r, parent)
        self.setPen(QPen(Qt.blue, 0.2, Qt.SolidLine, Qt.RoundCap))

    def paint(self, painter: 'QPainter', option: 'QStyleOptionGraphicsItem', widget: 'QWidget') -> None:
        super(SelectorItem, self).paint(painter, option, widget)
        painter.drawLine(self.rect().topLeft(), self.rect().bottomRight())
        painter.setBrush(Qt.blue)
        painter.drawEllipse(self.rect().center(), 0.3, 0.3)
