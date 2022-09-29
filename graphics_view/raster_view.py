from PyQt5.QtCore import QLine

import rsrc
from .canvas import Rasterizer
from .gv import *

assert rsrc


class RasterViewer(VectoRaster):

    def __init__(self, parent=None,
                 size: QSize = QSize(640, 480),
                 clicks: QSizeF = QSizeF(2.01, 2.01)):
        super(RasterViewer, self).__init__(parent, size, clicks)

    def draw_grid(self):
        self.draw_mil_grid(10, 10, True, True, CustomPen.GridH2)
        self.draw_mil_grid(1, 1, True, False, CustomPen.GridH3, font_size=5)
        self.draw_mil_grid(self._min_mil_h_step, self._min_mil_v_step, True, False, CustomPen.GridH3)
        self.draw_mil_grid(100, 100, True, False, CustomPen.GridH1)

    def draw_background(self):
        background_brush = QBrush(Qt.lightGray, Qt.Dense4Pattern)
        background_brush.setTransform(background_brush.transform().translate(0.5, 0.5))
        self.setBackgroundBrush(background_brush)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 2  # may be (1.6, 0.625) or (1.25, 0.8)
            self._zoom += 1
        else:
            factor = 0.5  # may be (1.6, 0.625) or (1.25, 0.8)
            self._zoom -= 1
        if 6 >= self._zoom > 0:
            self.scale(factor, factor)
        elif self._zoom > 6:
            self._zoom = 6
        elif self._zoom == 0:
            self.fitInView()
        else:
            self._zoom = 0

    def _release_mouse_button(self, point):
        if self.draw_mode == DrawMode.Pencil:
            self._canvas.drawPoint(self.lastPoint, CustomPen.Pencil)
        elif self.draw_mode == DrawMode.Eraser:
            self._canvas.drawPoint(self.lastPoint, CustomPen.Eraser)
        elif self.draw_mode == DrawMode.Line and self.temp_item:
            self._canvas.drawLineC(self.temp_item.line(), CustomPen.Line)
        elif self.draw_mode == DrawMode.Rect and self.temp_item:
            self._canvas.drawRectC(self.temp_item.rect(), CustomPen.Line)
        elif self.draw_mode == DrawMode.Ellipse and self.temp_item:
            self._canvas.drawEllipseC(self.temp_item.rect(), CustomPen.Ellipse)
        if self.temp_item:
            self._scene.removeItem(self.temp_item)

    def _erase(self, point, modifiers):
        p1, p2 = self._get_pencil_tool_points(point, modifiers)
        self._canvas.drawLineC(QLine(p1, p2), CustomPen.Eraser)
        self.lastPoint = p2

    def _pencil(self, point, modifiers, pen=CustomPen.PencilVect):
        p1, p2 = self._get_pencil_tool_points(point, modifiers)
        self._canvas.drawLineC(QLine(p1, p2), pen)
        self.lastPoint = p2

    def _line(self, point, modifiers):
        p1, p2 = self._get_line_tool_points(point, modifiers)
        line = QLineF(p1, p2)
        if not self.temp_item:
            self.temp_item = self._scene.addLine(line, CustomPen.Line)
        else:
            self.temp_item.setLine(line)

    def _rect(self, point, modifiers):
        p1, p2 = self._get_rect_tool_point(point, modifiers)
        rect = QRectF(p1, p2)
        if not self.temp_item:
            self.temp_item = self._scene.addSmoothRect(rect, CustomPen.Line)
        else:
            self.temp_item.setRect(rect)

    def _ellipse(self, point, modifiers):
        p1, p2 = self._get_ellipse_tool_point(point, modifiers)
        rect = QRectF(p1, p2)
        if not self.temp_item:
            self.temp_item = self._scene.addSmoothEllipse(rect, CustomPen.Ellipse)
        else:
            self.temp_item.setRect(rect)

    @hide_grid
    def clear_view(self):
        self._canvas.clear_pixmap()

    def draw_sketch(self, sketch=example_grid):
        def round_point_to_step(v, step):
            if abs(v) < step:
                return False
            mod = abs(v % step)
            if mod > 0:
                if step == 0.2 and mod / 0.2 > mod / 0.25:
                    step = 0.25
                if step == 0.25 and mod / 0.25 > mod / 0.3:
                    step = 0.3
                if step == 0.3 and mod / 0.3 > mod / 0.5:
                    step = 0.5
                return round(v / step) * step
            return None

        for item in sketch:
            pen = CustomPen.Line

            layer = Rasterizer(self._min_mil_h_step,
                               self._min_mil_v_step,
                               self._px_at_mil_h,
                               self._px_at_mil_v,
                               **item)

            if layer.t == ItemType.Line:

                line = layer.as_line()
                if line:
                    self._canvas.drawLineC(line, pen)

            elif layer.t == ItemType.Point:
                point = layer.as_point()
                if point:
                    self._canvas.drawPointC(point, pen)

            elif layer.t == ItemType.Text:
                point = layer.as_text()
                if point:
                    self._canvas.drawTextC(point, layer.text, layer.font)

            elif layer.t in [ItemType.Circle, ItemType.Ellipse]:

                ellipse = layer.as_ellipse()
                if ellipse:
                    cx, cy, rx, ry = ellipse
                    if abs(rx) < self._min_px_h_step and abs(ry) < self._min_px_v_step:
                        cp = QPointF(cx, cy) - QPointF(1, 1)
                        rect = QRectF(cp, QSizeF(2, 2))
                        self._canvas.drawEllipseC(rect, pen=pen)
                    else:
                        rect = QRectF(QPointF(cx - rx, cy - ry), QSizeF(2 * rx, 2 * ry))
                        self._canvas.drawEllipseC(rect, pen=pen)

            elif layer.t == ItemType.Rect:

                rect = layer.as_rect()
                if rect:
                    cx, cy, rx, ry = rect

                    if abs(rx) < self._min_px_h_step and abs(ry) < self._min_px_v_step:
                        cp = QPointF(cx, cy) - QPointF(1, 1)
                        self._canvas.drawRectC(QRectF(cp, QSizeF(2, 2)), pen)
                    else:
                        rect = QRectF(QPointF(cx - rx, cy - ry), QPointF(cx + rx, cy + ry))
                        self._canvas.drawRectC(rect, pen)
