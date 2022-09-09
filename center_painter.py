from PyQt5.QtCore import QPointF, QPoint, QLine, QRect, QRectF, Qt
from PyQt5.QtGui import QPainter, QPixmap, QPolygon


class CenterPainter(QPainter):
    def __init__(self, pixmap: QPixmap = None):
        super(CenterPainter, self).__init__(pixmap)

        self.pixmap = pixmap
        self.x0 = int(pixmap.width() / 2) + 1
        self.y0 = int(pixmap.height() / 2) + 1

    def drawPointC(self, point: [QPointF, QPoint]) -> None:
        point = self._transpose_point(point)
        return super(CenterPainter, self).drawPoint(point)

    def drawLineC(self, line: QLine) -> None:
        line = QLine(self._transpose_line_point(line.p1()), self._transpose_line_point(line.p2()))
        return super(CenterPainter, self).drawLine(line)

    def drawLinesC(self, lines: list) -> None:
        lines = list(map(lambda line: QLine(self._transpose_line_point(line.p1()), self._transpose_line_point(line.p2())), lines))
        return super(CenterPainter, self).drawLines(lines)

    def drawRectC(self, r: QRect) -> None:
        p1 = QPoint(self._transpose_point(QPoint(r.x(), r.y())))
        p2 = QPoint(self._transpose_point(QPoint(r.width(), r.height())))
        r = QRect(p1, p2)
        return super(CenterPainter, self).drawRect(r)

    def drawEllipseC(self, r: QRectF) -> None:
        p1 = QPoint(self._transpose_point(QPoint(r.x(), r.y())))
        p2 = QPoint(self._transpose_point(QPoint(r.width(), r.height())))
        r = QRect(p1, p2)
        return super(CenterPainter, self).drawEllipse(r)

    def drawPolygonC(self, polygon: QPolygon, fillRule: Qt.FillRule = Qt.OddEvenFill) -> None:
        points = [self._transpose_line_point(point) for point in polygon]
        polygon = QPolygon(points)
        return super(CenterPainter, self).drawPolygon(polygon, fillRule)

    def _transpose_line_point(self, p: [QPointF, QPoint]):
        return QPoint(self.x0 + p.x(), self.y0 + p.y())

    def _transpose_point(self, p: [QPointF, QPoint]):
        if p.x() > 0:
            p.setX(p.x() - 1)
        if p.y() > 0:
            p.setY(p.y() - 1)
        return QPoint(self.x0 + p.x(), self.y0 + p.y())
