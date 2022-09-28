import typing

from PyQt5.QtCore import QSize, Qt, QRectF
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsItem

from .center_painter import CenterPainter


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
