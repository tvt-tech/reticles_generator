from PyQt5.QtCore import QRectF, Qt, QLineF, QPointF
from PyQt5.QtGui import QPainter, QPixmap, QPen
from PyQt5.QtWidgets import QGraphicsEllipseItem, QStyleOptionGraphicsItem, QWidget, QGraphicsLineItem, \
    QGraphicsRectItem, QGraphicsItem, QGraphicsItemGroup


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


class PointItem(QGraphicsItem):
    def __init__(self, point: 'QPointF', pen: QPen, brush: 'QBrush' = Qt.black, parent=None):
        super(PointItem, self).__init__(parent)
        self._pen = pen
        self._brush = brush
        self._p = point
        self._x = point.x()
        self._y = point.y()

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

    def pen(self):
        return self._pen

    def brush(self):
        return self._brush

    def setPen(self, p: QPen):
        self._pen = p


class RulerItem(QGraphicsRectItem):
    def __init__(self, r: QRectF, step: float, pen: QPen, brush: 'QBrush' = Qt.black, parent=None):
        super(RulerItem, self).__init__(r, parent)
        self.setPen(pen)
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


class SelectorItem(QGraphicsRectItem):
    def __init__(self, r: QRectF, parent=None):
        super(SelectorItem, self).__init__(r, parent)
        self.setPen(QPen(Qt.blue, 0.2, Qt.SolidLine, Qt.RoundCap))

    def paint(self, painter: 'QPainter', option: 'QStyleOptionGraphicsItem', widget: 'QWidget') -> None:
        super(SelectorItem, self).paint(painter, option, widget)
        painter.drawLine(self.rect().topLeft(), self.rect().bottomRight())
        painter.setBrush(Qt.blue)
        painter.drawEllipse(self.rect().center(), 0.3, 0.3)

