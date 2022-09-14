from PyQt5.QtCore import QPointF, QRectF, QLineF, Qt
from PyQt5.QtGui import QPolygonF, QPen, QBrush, QFont
from PyQt5.QtWidgets import QGraphicsScene

from smooth_item import SmoothRectItem, SmoothEllipseItem, SmoothLineItem, PointItem


class DrawbleGraphicScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super(DrawbleGraphicScene, self).__init__(*args, **kwargs)

        self.x0 = int(self.width() / 2) + 1
        self.y0 = int(self.height() / 2) + 1

    def addSmoothLine(self, line: QLineF, pen: 'QPen') -> SmoothLineItem:
        smooth_line = SmoothLineItem(line, pen)
        self.addItem(smooth_line)
        return smooth_line

    def addSmoothRect(self, rect: QRectF, pen: 'QPen', brush: QBrush = Qt.transparent) -> SmoothRectItem:
        smooth_rect = SmoothRectItem(rect, pen)
        self.addItem(smooth_rect)
        return smooth_rect

    def addSmoothEllipse(self, rect: QRectF, pen: 'QPen', brush: QBrush = Qt.transparent) -> SmoothEllipseItem:
        smooth_ellipse = SmoothEllipseItem(rect, pen)
        self.addItem(smooth_ellipse)
        return smooth_ellipse

    def addLineC(self, line: QLineF, pen: 'QPen') -> 'QGraphicsLineItem':
        line = QLineF(self._transpose_point(line.p1()), self._transpose_point(line.p2()))
        return super(DrawbleGraphicScene, self).addLine(line, pen)

    def addTextC(self, text: str, pos: 'QPoint', font: 'QFont' = QFont()) -> 'QGraphicsTextItem':
        text_item = super(DrawbleGraphicScene, self).addText(text, font)
        text_item.setPos(self._transpose_point(pos))
        return text_item

    def addRectC(self, rect: QRectF, pen: 'QPen', brush: 'QBrush' = Qt.transparent) -> 'QGraphicsRectItem':
        p1 = QPointF(self._transpose_point(QPointF(rect.x(), rect.y())))
        p2 = QPointF(self._transpose_point(QPointF(rect.width(), rect.height())))
        rect = QRectF(p1, p2)
        super(DrawbleGraphicScene, self).addRect(rect, pen, brush)

    def addEllipseC(self, rect: QRectF, pen: 'QPen',
                    brush: 'QBrush' = Qt.transparent) -> 'QGraphicsEllipseItem':
        p1 = QPointF(self._transpose_point(QPointF(rect.x(), rect.y())))
        p2 = QPointF(self._transpose_point(QPointF(rect.width(), rect.height())))
        rect = QRectF(p1, p2)
        super(DrawbleGraphicScene, self).addEllipse(rect, pen, brush)

    def addPolygonC(self, polygon: QPolygonF, pen: 'QPen',
                    brush: 'QBrush' = Qt.transparent) -> 'QGraphicsPolygonItem':
        points = [self._transpose_point(point) for point in polygon]
        polygon = QPolygonF(points)
        super(DrawbleGraphicScene, self).addPolygon(polygon, pen, brush)

    def addPoint(self, point: 'QPointF', pen: 'QPen' = QPen(Qt.black),
                 brush: QBrush = QBrush(Qt.black)) -> 'QGraphicsRectItem':
        # size = 0.25
        # rect = QRectF(QPointF(point.x() - size, point.y() - size), QPointF(point.x() + size, point.y() + size))
        # return super(DrawbleGraphicScene, self).addEllipse(rect, pen, brush)
        point_item = PointItem(point, pen, brush)
        self.addItem(point_item)
        return point_item

    def addPointC(self, point: QPointF, pen: QPen = QPen(Qt.black),
                  brush: QBrush = QBrush(Qt.white)) -> 'QGraphicsRectItem':
        point = self._transpose_point(point)
        return self.addPoint(point, pen, brush)

    def _transpose_point(self, p: [QPointF, 'QPoint']):
        return QPointF(self.x0 + p.x(), self.y0 + p.y())
