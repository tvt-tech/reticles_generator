from enum import IntEnum, IntFlag, auto

from PyQt5.QtCore import QRectF, Qt, QLineF, QPointF, QSizeF
from PyQt5.QtGui import QPainter, QPixmap, QPen, QBrush, QColor, QFont, QPainterPath, QPainterPathStroker
from PyQt5.QtWidgets import QGraphicsEllipseItem, QStyleOptionGraphicsItem, QWidget, QGraphicsLineItem, \
    QGraphicsRectItem, QGraphicsItemGroup, QGraphicsSimpleTextItem

from .center_painter import CenterPainter


class ItemFlag(IntFlag):
    Point = auto()
    Line = auto()
    Rect = auto()
    Ellipse = auto()
    Circle = auto()
    Polygon = auto()
    Text = auto()
    Ruler = auto()
    Filled = auto()


class ItemType(IntEnum):
    Point = 1
    Line = 2
    Rect = 3
    Ellipse = 4
    Circle = 5
    Polygon = 6
    Text = 7
    Ruler = 8
    RLine = 9


class CustomPen:
    # GridH1 = QPen(Qt.darkMagenta, 0.2, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    # GridH2 = QPen(Qt.darkMagenta, 0.15, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    # GridH3 = QPen(Qt.darkMagenta, 0.05, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    # GridH4 = QPen(Qt.darkMagenta, 0.02, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    # GridH5 = QPen(Qt.darkMagenta, 0.01, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    GridH1 = QPen(QColor(78, 83, 87), 0.2, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    GridH2 = QPen(QColor(78, 83, 87), 0.15, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    GridH3 = QPen(QColor(78, 83, 87), 0.05, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    GridH4 = QPen(QColor(78, 83, 87), 0.02, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    GridH5 = QPen(QColor(78, 83, 87), 0.01, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    Pencil = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)
    PencilVect = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)
    PointVect = QPen(Qt.transparent, 0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    Eraser = QPen(Qt.transparent, 1, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)
    Line = QPen(Qt.black, 1, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
    LineVect = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    Ellipse = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)
    NoPen = QPen(Qt.transparent, 0)


class CustomBrush:
    Transparent = QBrush(Qt.transparent)
    Black = QBrush(Qt.black)
    Blue = QBrush(Qt.blue)


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
        print(pixmap.rect())
        pixmap.fill(Qt.transparent)
        pix_painter = CenterPainter(pixmap)
        pix_painter.drawRect(pixmap.rect())
        pix_painter.drawLineC(self.line())
        return pixmap

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.setPen(self.pen())
        pixmap = self.redraw_pix()
        painter.drawPixmap(self.boundingRect(), pixmap, QRectF(0, 0, pixmap.width(), pixmap.height()))


class SmoothRectItem(QGraphicsRectItem):
    def __init__(self, rect: QRectF, pen: QPen, parent=None):
        super(SmoothRectItem, self).__init__(parent)
        self.setRect(rect)
        self.setPen(pen)
        # self.setPos(-0.5, -0.5)

    def boundingRect(self) -> QRectF:
        return self.scene().sceneRect()

    def redraw_pix(self):
        pixmap = QPixmap(self.scene().width(), self.scene().height())
        pixmap.fill(Qt.transparent)
        pix_painter = CenterPainter(pixmap)
        print(self.rect())
        pix_painter.drawRectC(self.rect())
        return pixmap

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.setPen(self.pen())
        pixmap = self.redraw_pix()
        painter.drawPixmap(self.boundingRect(), pixmap, QRectF(1, 1, pixmap.width()-1, pixmap.height()-1))


class SmoothEllipseItem(QGraphicsEllipseItem):
    def __init__(self, rect: QRectF, pen: QPen, parent=None):
        super(SmoothEllipseItem, self).__init__(parent)
        self.setRect(rect)
        self.setPen(pen)
        # self.setPos(-0.5, -0.5)

    def boundingRect(self) -> QRectF:
        return self.scene().sceneRect()

    def redraw_pix(self):
        pixmap = QPixmap(self.scene().width(), self.scene().height())
        pixmap.fill(Qt.transparent)
        pix_painter = CenterPainter(pixmap)
        pix_painter.drawEllipseC(self.rect())
        return pixmap

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.setPen(self.pen())
        pixmap = self.redraw_pix()
        painter.drawPixmap(self.boundingRect(), pixmap, QRectF(1, 1, pixmap.width()-1, pixmap.height()-1))


class PointItem(QGraphicsEllipseItem, HoveredGraphicsItem):
    def __init__(self, point: 'QPointF', pen: QPen = CustomPen.PointVect, brush: 'QBrush' = CustomBrush.Black, parent=None):
        super(PointItem, self).__init__(parent)
        self.setAcceptHoverEvents(True)
        self._default_brush_color = brush.color()
        self._r = 0.5
        self.setPen(CustomPen.NoPen)
        self.setBrush(brush)
        self._cp = point
        self.setRect(QRectF(self._cp.x() - self._r, self._cp.y() - self._r, 2 * self._r, 2 * self._r))

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.setBrush(CustomBrush.Blue)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.setBrush(QBrush(self._default_brush_color))

    def cx(self):
        return self._cp.x()

    def cy(self):
        return self._cp.y()

    def cp(self):
        return self._cp

    def toJson(self, click_x, click_y, multiplier):
        return {
            't': ItemType.Point,
            'text': "",
            'step': 0.0,
            'p1': (
                self._cp.x() * click_x / multiplier,
                self._cp.y() * click_y / multiplier
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


class RulerGroup(QGraphicsItemGroup):
    def __init__(self, r: QRectF, step: float, pen: QPen = CustomPen.LineVect, brush: 'QBrush' = CustomBrush.Black,
                 parent=None):
        super(RulerGroup, self).__init__(parent)
        self.setAcceptHoverEvents(True)
        self._default_pen_color = pen.color()
        self._default_brush_color = brush.color()
        self._step = step
        self._pen = pen
        self._brush = brush
        self._rect = None
        self.setRect(r)
        self._removing = False

    def removeSelf(self):
        self._removing = True
        self.scene().removeItem(self)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self._pen.setColor(Qt.blue)
        self._brush.setColor(Qt.blue)
        for item in self.childItems():
            if isinstance(item, LineItem):
                item.setPen(self._pen)
            if isinstance(item, PointItem):
                item.setBrush(self._brush)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self._pen.setColor(self._default_pen_color)
        self._brush.setColor(self._default_brush_color)
        for item in self.childItems():
            if isinstance(item, LineItem):
                item.setPen(self._pen)
            if isinstance(item, PointItem):
                item.setBrush(self._brush)

    def boundingRect(self) -> QRectF:
        if self._removing:
            return self.rect()
        elif self.rect().width() > self.rect().height():
            return QRectF(self.rect().x(), self.rect().y(), self.rect().width(), 0)
        elif self.rect().width() < self.rect().height():
            return QRectF(self.rect().x(), self.rect().y(), 0, self.rect().height())
        return QRectF()

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
                    line_item = RLineItem(line)
                    self.addToGroup(line_item)
                else:
                    point = QPointF(x, rect.center().y())
                    point_item = PointItem(point)
                    self.addToGroup(point_item)

        elif rect.width() < rect.height():
            line_count = abs(int(rect.height() / self._step)) + 1
            for i in range(line_count):
                y = i * self._step + rect.y()
                if rect.width() > 0:
                    line = QLineF(rect.center().x() - rect.width() / 2, y, rect.center().x() + rect.width() / 2, y)
                    line_item = RLineItem(line)
                    self.addToGroup(line_item)
                else:
                    point = QPointF(rect.center().x(), y)
                    point_item = PointItem(point)
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
            "text": "",
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
        point = QPointF(px_at_mil_h * p1[0], px_at_mil_v * p1[1])
        size = QSizeF(px_at_mil_h * p2[0], px_at_mil_v * p2[1])
        rect = QRectF(point, size)
        pen = CustomPen.LineVect
        return RulerGroup(rect, s, pen)


# class RulerTextGroup(RulerGroup):
#
#     def setRect(self, r: QRectF):
#         self._rect = r
#         rect = self.rect()
#         font = QFont('BankGothic Lt BT')
#         font.setPointSize(8)
#         for item in self.childItems():
#             self.scene().removeItem(item)
#
#         if rect.width() > rect.height():
#             line_count = abs(int(rect.width() / self._step)) + 1
#             for i in range(line_count):
#                 x = i * self._step + rect.x()
#                 text_item = SimpleTextItem(f'{abs(int(x * 0.05))}', font, QPointF(x, rect.center().y()))
#                 self.addToGroup(text_item)
#
#         elif rect.width() < rect.height():
#             line_count = abs(int(rect.height() / self._step)) + 1
#             for i in range(line_count):
#                 y = i * self._step + rect.y()
#                 text_item = SimpleTextItem(f'{abs(int(y * 0.05))}', font, QPointF(rect.center().x(), y))
#                 self.addToGroup(text_item)


class LineItem(QGraphicsLineItem, HoveredGraphicsItem):
    def __init__(self, line: QLineF, pen: QPen=CustomPen.LineVect, parent=None):
        super(LineItem, self).__init__(line)
        self.setParentItem(parent)
        self.setPen(pen)
        self._default_pen_color = pen.color()
        self.setAcceptHoverEvents(True)
        self._brush = QBrush()

    def setBrush(self, b: QBrush):
        self._brush = b

    def brush(self):
        return self._brush

    def toJson(self, click_x, click_y, multiplier):
        return {
            't': ItemType.Line,
            "text": "",
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


class RLineItem(LineItem):
    def toJson(self, click_x, click_y, multiplier):
        return {
            't': ItemType.RLine,
            "text": "",
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
        return RLineItem(line, pen)


class RectItem(QGraphicsRectItem, HoveredGraphicsItem):
    def __init__(self, rect: QRectF, pen: QPen, brush: 'QBrush' = CustomBrush.Transparent):
        super(RectItem, self).__init__(rect)
        self.setPen(pen)
        self._default_pen_color = pen.color()
        self.setBrush(brush)
        self.setAcceptHoverEvents(True)

    def shape(self) -> 'QPainterPath':
        path = super(RectItem, self).shape()
        stroker = QPainterPathStroker()
        return stroker.createStroke(path)

    def toJson(self, click_x, click_y, multiplier):
        return {
            't': ItemType.Rect,
            'text': "",
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
        p = QPointF(px_at_mil_h * p1[0], px_at_mil_v * p1[1])
        s = QSizeF(px_at_mil_h * p2[0], px_at_mil_v * p2[1])
        rect = QRectF(p, s)
        pen = CustomPen.LineVect
        return RectItem(rect, pen)


class EllipseItem(QGraphicsEllipseItem, HoveredGraphicsItem):
    def __init__(self, rect: QRectF, pen: QPen, brush: 'QBrush' = CustomBrush.Transparent):
        super(EllipseItem, self).__init__(rect)
        self.setPen(pen)
        self._default_pen_color = pen.color()
        self.setBrush(brush)
        self.setAcceptHoverEvents(True)

    def shape(self) -> 'QPainterPath':
        path = super(EllipseItem, self).shape()
        stroker = QPainterPathStroker()
        return stroker.createStroke(path)

    def toJson(self, click_x, click_y, multiplier):
        return {
            't': ItemType.Ellipse if self.rect().width() != self.rect().height() else ItemType.Circle,
            'text': "",
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
        p = QPointF(px_at_mil_h * p1[0], px_at_mil_v * p1[1])
        s = QSizeF(px_at_mil_h * p2[0], px_at_mil_v * p2[1])
        rect = QRectF(p, s)
        pen = CustomPen.PencilVect
        return EllipseItem(rect, pen)


class SimpleTextItem(QGraphicsSimpleTextItem, HoveredGraphicsItem):
    def __init__(self, text: str, font: QFont, pos: QPointF, parent=None):
        super(SimpleTextItem, self).__init__(text, parent)
        self.setAcceptHoverEvents(True)
        self.setFont(font)
        self._default_pen_color = Qt.black
        self._default_text_color = Qt.black
        self.def_pos = pos
        self.setPos(pos - QPointF(self.boundingRect().width() / 2, self.boundingRect().height() / 2))

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        brush = self.brush()
        brush.setColor(Qt.blue)
        self.setBrush(brush)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        brush = self.brush()
        brush.setColor(self._default_pen_color)
        self.setBrush(brush)

    def toJson(self, click_x, click_y, multiplier) -> dict:
        return {
            't': ItemType.Text,
            'text': self.text(),
            'step': 0.0,
            'p1': (
                self.def_pos.x() * click_x / multiplier,
                self.def_pos.y() * click_y / multiplier
            ),
            'p2': (0.0, 0.0),
            'pen': self.font().pointSize(),
        }

    @staticmethod
    def fromJson(px_at_mil_h: float,
                 px_at_mil_v: float,
                 p1: tuple[float, float],
                 p2: tuple[float, float],
                 step: float = 1, *args, **kwargs):
        font = QFont('BankGothic Lt BT')
        font.setPointSize(kwargs['pen'])
        pos = QPointF(px_at_mil_h * p1[0], px_at_mil_v * p1[1])
        text = kwargs['text'] if 'text' in kwargs else 'X'
        return SimpleTextItem(text, font, pos)


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


class GridItem(QGraphicsItemGroup):
    def __init__(self, px_at_mil_h, px_at_mil_v,
                 step_h=10.0, step_v=10.0, grid=False, mark=False, pen: QPen = QPen(), font_size=8, rect: QRectF=QRectF(), parent=None):
        super(GridItem, self).__init__(parent)
        self._rect = rect
        self._px_at_mil_h = px_at_mil_h
        self._px_at_mil_v = px_at_mil_v
        self._step_h = step_h
        self._step_v = step_v
        self._grid = grid
        self._mark = mark
        self._pen = pen
        self._font_size = font_size
        self._draw()

    def boundingRect(self) -> QRectF:
        return QRectF()

    def _draw(self):
        grid_scale_h_f = self._px_at_mil_h * self._step_h
        grid_scale_v_f = self._px_at_mil_v * self._step_v
        grid_scale_h = int(grid_scale_h_f)
        grid_scale_v = int(grid_scale_v_f)

        if (grid_scale_h and grid_scale_v) == 0:
            return

        scene_rect = self._rect
        max_x = int(scene_rect.width() / 2)
        max_y = int(scene_rect.height() / 2)

        font = QFont('BankGothic Lt BT')
        font.setPointSize(self._font_size)

        half_dark_magenta = QColor(78, 83, 87, 128)
        # half_dark_magenta = QColor(128, 0, 128, 128)
        font_brush = QBrush(half_dark_magenta)
        self._pen.setColor(half_dark_magenta)

        for i, x in enumerate(range(0, max_x, grid_scale_h)):
            xF = i * grid_scale_h_f
            if self._grid:
                line_item = LineItem(QLineF(xF, max_y, xF, -max_y), pen=self._pen)
                self.addToGroup(line_item)
                line_item = LineItem(QLineF(-xF, max_y, -xF, -max_y), pen=self._pen)
                self.addToGroup(line_item)
            if self._mark and i > 0:
                text_item = SimpleTextItem(str(round(i * self._step_h, 1)), font, QPointF(xF, 10))
                text_item.setBrush(font_brush)
                self.addToGroup(text_item)

                text_item = SimpleTextItem(str(round(i * self._step_h, 1)), font, QPointF(-xF, 10))
                text_item.setBrush(font_brush)
                self.addToGroup(text_item)

        for i, x in enumerate(range(0, max_x, grid_scale_v)):
            yF = i * grid_scale_v_f
            if self._grid:
                line_item = LineItem(QLineF(max_x, yF, -max_x, yF), pen=self._pen)
                self.addToGroup(line_item)
                line_item = LineItem(QLineF(max_x, -yF, -max_x, -yF), pen=self._pen)
                self.addToGroup(line_item)
            if self._mark and i > 0:
                text_item = SimpleTextItem(str(round(i * self._step_h, 1)), font, QPointF(10, yF))
                text_item.setBrush(font_brush)
                self.addToGroup(text_item)

                text_item = SimpleTextItem(str(round(i * self._step_h, 1)), font, QPointF(10, -yF))
                text_item.setBrush(font_brush)
                self.addToGroup(text_item)


class PenCircle(QGraphicsEllipseItem):
    def __init__(self, parent=None):
        super(PenCircle, self).__init__(parent)
        self.setRect(0, 0, 1, 1)
        self.setPen(QPen(Qt.darkBlue, 0.1, Qt.SolidLine))

    def shape(self) -> 'QPainterPath':
        path = super(PenCircle, self).shape()
        stroker = QPainterPathStroker()
        return stroker.createStroke(path)
