from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QGraphicsScene

from custom_graphics_item import *


class DrawbleGraphicScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super(DrawbleGraphicScene, self).__init__(*args, **kwargs)
        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)

        self.x0 = int(self.width() / 2) + 1
        self.y0 = int(self.height() / 2) + 1
        self.origin = QPoint(self.x0, self.y0)

    def addItem(self, item: QGraphicsItem) -> QGraphicsItem:
        super(DrawbleGraphicScene, self).addItem(item)
        return item

    def addSmoothLine(self, line: QLineF, pen: 'QPen') -> SmoothLineItem:
        smooth_line = SmoothLineItem(line, pen)
        return self.addItem(smooth_line)

    def addSmoothRect(self, rect: QRectF, pen: 'QPen', brush: QBrush = Qt.transparent) -> SmoothRectItem:
        smooth_rect = SmoothRectItem(rect, pen)
        return self.addItem(smooth_rect)

    def addSmoothEllipse(self, rect: QRectF, pen: 'QPen', brush: QBrush = Qt.transparent) -> SmoothEllipseItem:
        smooth_ellipse = SmoothEllipseItem(rect, pen)
        return self.addItem(smooth_ellipse)

    def addPoint(self, point: 'QPointF', pen: 'QPen' = CustomPen.PointVect,
                 brush: QBrush = QBrush(Qt.black)) -> 'QGraphicsRectItem':
        point_item = PointItem(point, pen, brush)
        return self.addItem(point_item)

    def addRuler(self, rect: QRectF, step: float, pen: 'QPen', brush: 'QBrush' = CustomBrush.Transparent) -> RulerGroup:
        ruler_group = RulerGroup(rect, step, pen, brush)
        return self.addItem(ruler_group)

    def addSelector(self, rect: QRectF, view_scale: tuple[float, float, float] = None) -> SelectorItem:
        selector = SelectorItem(rect, view_scale)
        return self.addItem(selector)

    def addLine(self, line: QLineF, pen: 'QPen') -> LineItem:
        line_item = LineItem(line, pen)
        return self.addItem(line_item)

    def addRect(self, rect: 'QRectF', pen: 'QPen', brush: QBrush = CustomBrush.Transparent) -> RectItem:
        rect_item = RectItem(rect, pen, brush)
        return self.addItem(rect_item)

    def addEllipse(self, rect: 'QRectF', pen: 'QPen', brush: QBrush = CustomBrush.Transparent) -> QGraphicsEllipseItem:
        ellipse_item = EllipseItem(rect, pen, brush)
        return self.addItem(ellipse_item)

    # def removeItem(self, item: 'QGraphicsItem') -> None:
    #     for child_item in item.childItems():
    #         super().removeItem(child_item)
    #     super().removeItem(item)
