from PyQt5.QtCore import QPointF, QRectF, QLineF, Qt
from PyQt5.QtGui import QPolygonF, QPen, QBrush, QFont
from PyQt5.QtWidgets import QGraphicsScene

from smooth_item import *


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

    def addPoint(self, point: 'QPointF', pen: 'QPen' = QPen(Qt.black),
                 brush: QBrush = QBrush(Qt.black)) -> 'QGraphicsRectItem':
        point_item = PointItem(point, pen, brush)
        self.addItem(point_item)
        return point_item

    def addRuler(self, rect: QRectF, step: float, pen: 'QPen', brush: 'QBrush' = Qt.transparent):
        point_item = RulerItem(rect, step, pen, brush)
        self.addItem(point_item)
        return point_item

    def addSelector(self, rect: QRectF):
        selector = SelectorItem(rect)
        self.addItem(selector)
        return selector
