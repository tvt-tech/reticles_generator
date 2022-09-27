import math

from PyQt5.QtCore import QLine
from PyQt5.QtGui import QFontMetrics

from .gv import *
import rsrc
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

            if item['t'] == ItemType.Line:

                p1 = item['p1']
                p2 = item['p2']

                if p1[0] == p2[0] != 0:
                    r = round_point_to_step(p1[0], self._min_mil_h_step)
                    if r:
                        p1 = [r, p1[1]]
                        p2 = [r, p2[1]]
                    elif r is not None:
                        continue

                elif p1[1] == p2[1] != 0:
                    r = round_point_to_step(p1[1], self._min_mil_v_step)
                    if r:
                        p1 = [p1[0], r]
                        p2 = [p2[0], r]
                    elif r is not None:
                        continue

                p1 = [self._px_at_mil_h * p1[0], self._px_at_mil_v * p1[1]]
                p2 = [self._px_at_mil_h * p2[0], self._px_at_mil_v * p2[1]]

                if p1[0] < 0:
                    p1[0] -= 1
                if p1[1] < 0:
                    p1[1] -= 1
                if p2[0] < 0:
                    p2[0] -= 1
                if p2[1] < 0:
                    p2[1] -= 1

                # if 0 < abs(p1[0]) < self._min_px_h_step:
                #     p1[0] = p1[0] / abs(p1[0]) * 1
                #
                # if 0 < abs(p2[0]) < self._min_px_h_step:
                #     p2[0] = p2[0] / abs(p2[0]) * 1
                #
                # if 0 < abs(p1[1]) < self._min_px_v_step:
                #     p1[1] = p1[1] / abs(p1[1]) * 1
                #
                # if 0 < abs(p2[1]) < self._min_px_v_step:
                #     p2[1] = p2[1] / abs(p2[1]) * 1

                p1 = QPoint(math.ceil(p1[0]), math.ceil(p1[1]))
                p2 = QPoint(math.ceil(p2[0]), math.ceil(p2[1]))

                if item['t'] == ItemType.Line:
                    line = QLine(p1, p2)
                    # pen.setWidth(item['pen'])
                    self._canvas.drawLineC(line, pen)

            elif item['t'] == ItemType.Point:
                x = item['p1'][0]
                y = item['p1'][1]

                if x != 0:
                    r = round_point_to_step(x, self._min_mil_h_step)
                    if r:
                        x = r
                    elif r is not None:
                        continue

                if y != 0:
                    r = round_point_to_step(y, self._min_mil_v_step)
                    if r:
                        y = r
                    elif r is not None:
                        continue

                p = [int(self._px_at_mil_h * x), int(self._px_at_mil_v * y)]

                if p[0] < 0:
                    p[0] -= 1
                if p[1] < 0:
                    p[1] -= 1
                if p[0] > 0:
                    p[0] += 1
                if p[1] > 0:
                    p[1] += 1

                point = QPoint(*p)

                pen = CustomPen.Line
                self._canvas.drawPointC(point, pen)

            elif item['t'] == ItemType.Text:
                x = item['p1'][0]
                y = item['p1'][1]

                if x != 0:
                    r = round_point_to_step(x, self._min_mil_h_step)
                    if r:
                        x = r
                    elif r is not None:
                        continue

                if y != 0:
                    r = round_point_to_step(y, self._min_mil_v_step)
                    if r:
                        y = r
                    elif r is not None:
                        continue

                p = [int(self._px_at_mil_h * x), int(self._px_at_mil_v * y)]

                if p[0] < 0:
                    p[0] -= 1
                if p[1] < 0:
                    p[1] -= 1
                if p[0] > 0:
                    p[0] += 1
                if p[1] > 0:
                    p[1] += 1

                point = QPoint(*p)

                font = QFont('BankGothic Lt BT')
                font.setStyleStrategy(QFont.NoAntialias)
                font.setPixelSize(11)

                fm = QFontMetrics(font)
                w = fm.width(item['text'])
                h = fm.height()

                point = point - QPoint(w / 2, - h / 3)
                if h >= self._px_at_mil_v * 0.75:
                    continue
                elif fm.width('W') >= self._px_at_mil_h * 0.75:
                    continue

                self._canvas.drawTextC(point, item['text'], font)

            elif item['t'] in [ItemType.Circle, ItemType.Ellipse]:

                x1 = item['p1'][0]
                y1 = item['p1'][1]
                x2 = item['p2'][0]
                y2 = item['p2'][1]

                if x1 != 0:
                    r = round_point_to_step(x1, self._min_mil_h_step)
                    if r:
                        x1 = r
                    elif r is not None:
                        continue

                if y1 != 0:
                    r = round_point_to_step(y1, self._min_mil_v_step)
                    if r:
                        y1 = r
                    elif r is not None:
                        continue

                if x2 != 0:
                    r = round_point_to_step(x2, self._min_mil_h_step)
                    if r:
                        x2 = r
                    elif r is not None:
                        continue

                if y2 != 0:
                    r = round_point_to_step(y2, self._min_mil_v_step)
                    if r:
                        y2 = r
                    elif r is not None:
                        continue

                x1 = x1 * self._px_at_mil_h - 1
                y1 = y1 * self._px_at_mil_v - 1
                x2 = x2 * self._px_at_mil_h + 2
                y2 = y2 * self._px_at_mil_v + 2

                # x1 += (1 if x1 > 0 else -2 if x1 < 0 else 0)
                # x2 = x2 + 1 if x2 > 0 else x2 - 2 if x2 < 0 else x2
                # y1 = y1 + 1 if y1 > 0 else y1 - 1 if y1 < 0 else y1
                # y2 = y2 + 1 if y2 > 0 else y2 - 1 if y2 < 0 else y2

                # if x1 < 0:
                #     x1 -= 1
                # if y1 < 0:
                #     y1 -= 1
                # if x2 < 0:
                #     x2 -= 1
                # if y2 < 0:
                #     y2 -= 1

                # if x2 / x1 == 0.1:
                if x2 < self._min_mil_h_step:
                    self._canvas.drawPointC(QPoint(x1, y1), pen)

                else:
                    p = QPointF(x1, y1)
                    s = QSizeF(x2, y2)
                    rect = QRectF(p, s)
                    self._canvas.drawEllipseC(rect, pen)

            elif item['t'] == ItemType.Rect:

                x1 = item['p1'][0]
                y1 = item['p1'][1]
                x2 = item['p2'][0]
                y2 = item['p2'][1]

                if abs(x1) < self._min_mil_h_step:
                    x1 = x1 / abs(x1)

                elif x1 != 0:
                    r = round_point_to_step(x1, self._min_mil_h_step)
                    if r:
                        x1 = r
                        x1 = x1 * self._px_at_mil_h
                    elif r is not None:
                        continue

                if abs(y1) < self._min_mil_v_step:
                    y1 = y1 / abs(y1)

                elif y1 != 0:
                    r = round_point_to_step(y1, self._min_mil_v_step)
                    if r:
                        y1 = r
                        y1 = y1 * self._px_at_mil_v

                    elif r is not None:
                        continue

                if abs(x2) < self._min_mil_h_step:
                    x2 = x2 / abs(x2)

                elif x2 != 0:
                    r = round_point_to_step(x2, self._min_mil_h_step)
                    if r:
                        x2 = r
                        x2 = x2 * self._px_at_mil_h
                    elif r is not None:
                        continue

                if abs(y2) < self._min_mil_v_step:
                    y2 = y2 / abs(y2)

                elif y2 != 0:
                    r = round_point_to_step(y2, self._min_mil_v_step)
                    if r:
                        y2 = r
                        y2 = y2 * self._px_at_mil_v
                    elif r is not None:
                        continue

                pen = CustomPen.Ellipse

                # x1 = x1 + 1 if x1 > 0 else x1 - 2 if x1 < 0 else x1
                x1 += (1 if x1 > 0 else -2 if x1 < 0 else 0)
                x2 = x2 + 1 if x2 > 0 else x2 - 2 if x2 < 0 else x2
                y1 = y1 + 1 if y1 > 0 else y1 - 1 if y1 < 0 else y1
                y2 = y2 + 1 if y2 > 0 else y2 - 1 if y2 < 0 else y2

                if x2 < self._min_mil_h_step:
                    self._canvas.drawPointC(QPoint(x1, y1), pen)

                else:
                    p = QPointF(x1, y1)
                    s = QSizeF(x2, y2)
                    rect = QRectF(p, s)
                    self._canvas.drawRectC(rect, pen)
