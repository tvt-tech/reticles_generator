import json
import math
import os.path
from pathlib import Path
from enum import IntFlag, IntEnum, auto
from functools import wraps

from PyQt5.QtCore import QLine, QPoint, QPointF, pyqtSignal, QSize, QSizeF, QRect, Qt
from PyQt5.QtGui import QBrush, QMouseEvent, QFont, QCursor, QImage, QIcon
from PyQt5.QtWidgets import QApplication, QGraphicsPixmapItem, \
    QToolButton, QGraphicsView, QVBoxLayout, QHBoxLayout, QFrame, \
    QLineEdit, QComboBox

from canvas import GraphicsCanvas
from drawable_scene import DrawbleGraphicScene
from example_grid import example_grid
from grid_step import *
from custom_graphics_item import *


def hide_grid(func: callable):
    @wraps(func)
    def _impl(self, *method_args, **method_kwargs):
        children = self._scene.items()
        for ch in children:
            if isinstance(ch, GridItem):
                ch.setVisible(False)
            # if hasattr(ch, 'pen'):
            #     if ch.pen().color() == Qt.darkMagenta or ch.pen().color() == Qt.magenta:
            #         ch.setVisible(False)
            #
            # if hasattr(ch, 'defaultTextColor'):
            #     if ch.defaultTextColor() == Qt.darkMagenta or ch.defaultTextColor() == Qt.magenta:
            #         ch.setVisible(False)
        self._pen_size_ellipse.setVisible(False)
        ret = func(self, *method_args, **method_kwargs)
        for ch in children:
            ch.setVisible(True)
        self._pen_size_ellipse.setVisible(True)
        return ret

    return _impl


def hide_canvas(func: callable):
    @wraps(func)
    def _impl(self, *method_args, **method_kwargs):
        self._canvas.setVisible(False)

        ret = func(self, *method_args, **method_kwargs)
        self._canvas.setVisible(True)

        return ret

    return _impl


class DrawModeBtn(QToolButton):
    def __init__(self, *args, **kwargs):
        super(DrawModeBtn, self).__init__(*args, **kwargs)
        self.setFixedSize(50, 40)
        self.setText('Draw')
        self.is_enabled = False
        self.clicked.connect(self.change_mode)

    def change_mode(self):
        self.is_enabled = not self.is_enabled
        self.setDown(self.is_enabled)

    def reset(self):
        self.is_enabled = False
        self.setDown(self.is_enabled)


class DrawMode(IntFlag):
    Notool = auto()
    Pencil = auto()
    Eraser = auto()
    Line = auto()
    Rect = auto()
    Ellipse = auto()
    Text = auto()
    Ruler = auto()


class MyCanvasItem(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        super(MyCanvasItem, self).__init__(parent)

    def paint(self, painter, option, widget=None):
        super(MyCanvasItem, self).paint(painter, option, widget)

    # def drawLine(self):


class VectoRaster(QGraphicsView):
    photoClicked = pyqtSignal(QPoint)

    def __init__(self, parent=None,
                 size: QSize = QSize(640, 480),
                 clicks: QSizeF = QSizeF(2.01, 2.01),
                 vector_mode: bool = False):
        super(VectoRaster, self).__init__(parent)

        self.setRenderHint(QPainter.Antialiasing)
        self.setCursor(Qt.CrossCursor)

        # cur_pix = QPixmap('pencil20.svg')
        # pen_cur = QCursor(cur_pix, 2, -24)
        # self.setCursor(pen_cur)

        # self.setFixedSize(size)

        # drawing flags
        self._vector_mode = vector_mode
        self.draw_mode = DrawMode.Notool
        self.drawing = False
        self.temp_item = None
        self.lastPoint = None
        self._selector = None
        self.ruler_step = 1

        self.mil_grids = []

        self.w = size.width()
        self.h = size.height()

        self._zoom = 0

        self._click_x = clicks.width()
        self._click_y = clicks.height()

        # for 1px = 0.1mil
        # self._click_x = 0.25
        # self._click_y = 0.25

        # init canvas center coords
        self._x0 = int(self.w / 2)
        self._y0 = int(self.h / 2)

        # init reticle scale
        self._multiplier = 10  # cm/mil
        self._px_at_mil_h = 1
        self._px_at_mil_v = 1
        self.set_reticle_scale()

        # count minimal step
        # if self._vector_mode:
        #     mgs_h = 1
        #     mgs_v = 1
        # else:
        #     mgs_h = mingridstep_h
        #     mgs_v = mingridstep_v

        _min_mil_h_step = minmilstep(self._click_x, mingridstep_h)  # min horizontal step in mil
        _min_mil_v_step = minmilstep(self._click_y, mingridstep_v)  # min vertical step in mil
        self._min_mil_h_step = roundmilstep(_min_mil_h_step)
        self._min_mil_v_step = roundmilstep(_min_mil_v_step)
        self._min_px_h_step = self._min_mil_h_step * self._px_at_mil_h  # min horizontal step in pix at mil
        self._min_px_v_step = self._min_mil_v_step * self._px_at_mil_v  # min vertical step in pix at mil

        # set view flags
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.setMouseTracking(True)

        # create scene
        self._scene = DrawbleGraphicScene()

        rect = QRectF(-self.w / 2, -self.h / 2, self.w, self.h)

        self._scene.setSceneRect(rect)

        if self._vector_mode:
            # self.setBackgroundBrush(background_brush)
            self.draw_vector_mode_grid()
            self.setBackgroundBrush(Qt.lightGray)
        else:
            background_brush = QBrush(Qt.lightGray, Qt.Dense4Pattern)
            background_brush.setTransform(background_brush.transform().translate(0.5, 0.5))
            self.setBackgroundBrush(background_brush)
            self.draw_raster_mode_grid()

        # self._scene = DrawbleGraphicScene(-self.w, -self.h, self.w, self.h)
        self._canvas = GraphicsCanvas(self._scene.sceneRect().size())
        self._canvas.setPos(-1.5, -1.5)
        self._scene.addItem(self._canvas)

        self._pen_size_ellipse = QGraphicsEllipseItem(0, 0, 1, 1)
        self._pen_size_ellipse.setPen(QPen(Qt.darkBlue, 0.1, Qt.SolidLine))
        # self._pen_size_ellipse.setBrush(Qt.darkBlue)
        self._scene.addItem(self._pen_size_ellipse)

        self.setScene(self._scene)

        self.toggleDragMode()

    def draw_raster_mode_grid(self):
        # self.draw_mil_grid(10, 10, True, True, CustomPen.GridH2)
        # self.draw_mil_grid(1, 1, True, False, CustomPen.GridH3, font_size=5)
        self.draw_mil_grid(self._min_mil_h_step, self._min_mil_v_step, True, False, CustomPen.GridH3)
        # self.draw_mil_grid(100, 100, True, False, CustomPen.GridH1)

    def draw_vector_mode_grid(self):
        # self.draw_mil_grid(0.05, 0.05, True, False, CustomPen.GridH5)
        self.draw_mil_grid(0.1, 0.1, True, False, CustomPen.GridH4)
        self.draw_mil_grid(1, 1, True, True, CustomPen.GridH3, font_size=5)
        self.draw_mil_grid(5, 5, False, False, CustomPen.GridH3, font_size=8)
        self.draw_mil_grid(10, 10, True, False, CustomPen.GridH2)
        self.draw_mil_grid(100, 100, True, False, CustomPen.GridH1)

    def rasterize(self, sketch=example_grid):

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
                # pen.setWidth(item['pen'])
                self._canvas.drawPointC(point, pen)
            #
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

                x1 = x1 * self._px_at_mil_h
                y1 = y1 * self._px_at_mil_v
                x2 = x2 * self._px_at_mil_h
                y2 = y2 * self._px_at_mil_v

                if x1 < 0:
                    x1 -= 1
                if y1 < 0:
                    y1 -= 1
                if x2 < 0:
                    x2 -= 1
                if y2 < 0:
                    y2 -= 1

                if x2 / x1 == 0.1:
                    pen = CustomPen.Pencil
                    p = QPoint(x2 - x1, y2 - y1)
                    self._canvas.drawPointC(p, pen)

            elif item['t'] == ItemType.Rect:

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

                pen = CustomPen.Ellipse

                x1 = x1 * self._px_at_mil_h
                y1 = y1 * self._px_at_mil_v
                x2 = x2 * self._px_at_mil_h
                y2 = y2 * self._px_at_mil_v

                if x1 < 0:
                    x1 -= 1
                if y1 < 0:
                    y1 -= 1
                if x2 < 0:
                    x2 -= 1
                if y2 < 0:
                    y2 -= 1

                if x2 < self._min_mil_h_step:
                    self._canvas.drawPointC(QPoint(x1, y1), pen)

                else:
                    p = (x1, y1)
                    s = (x1 + x2, y1 + y2)
                    rect = QRect(*p, *s)
                    self._canvas.drawRectC(rect, pen)

    def load_reticle_sketch(self, sketch=example_grid):

        for layer in sketch:
            if layer['t'] == ItemType.Ruler:
                graphics_item_type = RulerGroup
            elif layer['t'] == ItemType.Point:
                graphics_item_type = PointItem
            elif layer['t'] == ItemType.Line:
                graphics_item_type = LineItem
            elif layer['t'] == ItemType.Rect:
                graphics_item_type = RectItem
            elif layer['t'] in [ItemType.Ellipse, ItemType.Circle]:
                graphics_item_type = EllipseItem
            else:
                continue
            graphics_item = graphics_item_type.fromJson(self._px_at_mil_h, self._px_at_mil_v, **layer)
            self._scene.addItem(graphics_item)

    def set_reticle_scale(self):
        self._px_at_mil_h = self._multiplier / self._click_x
        self._px_at_mil_v = self._multiplier / self._click_y

    def draw_mil_grid(self, step_h=10.0, step_v=10.0, grid=False, mark=False, pen: QPen = QPen(), font_size=10):

        grid_layer = GridItem(self._px_at_mil_h, self._px_at_mil_v, step_h, step_v, grid, mark, pen, font_size,
                              self._scene.sceneRect())
        self._scene.addItem(grid_layer)

    def fitInView(self, scale=True):
        rect = self.sceneRect()
        unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
        self.scale(1 / unity.width(), 1 / unity.height())
        viewrect = self.viewport().rect()
        scenerect = self.transform().mapRect(rect)
        factor = min(viewrect.width() / scenerect.width(),
                     viewrect.height() / scenerect.height())
        self.scale(factor, factor)
        self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._canvas.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._canvas.setPixmap(QPixmap())
        self.fitInView()

    def wheelEvent(self, event):

        if self._vector_mode:
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1

            if 20 >= self._zoom > 0:
                self.scale(factor, factor)

            elif self._zoom > 20:
                self._zoom = 20

            elif self._zoom <= 0:
                self.fitInView()
            else:
                self._zoom = 0

        else:

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

    def toggleDragMode(self):
        if self.draw_mode != DrawMode.Notool:
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    @hide_grid
    def clear_view(self):
        if self._vector_mode:
            for item in self._scene.items():
                if item.isVisible():
                    self._scene.removeItem(item)
        else:
            self._canvas.clear_pixmap()

    def pencil_tool_draw(self, point, modifiers):
        p1 = QPoint(self.lastPoint.x(), self.lastPoint.y())
        p2 = QPoint(point.x(), point.y())

        if modifiers == Qt.ShiftModifier:
            if abs(p1.x() - p2.x()) <= abs(p1.y() - p2.y()):
                p2.setY(self.lastPoint.y())
            else:
                p2.setX(self.lastPoint.x())

        return p1, p2

    def pencil_raster(self, point, modifiers, pen=CustomPen.Pencil):
        p1, p2 = self.pencil_tool_draw(point, modifiers)
        self._canvas.drawLine(QLine(p1, p2), pen)
        self.lastPoint = p2

    def pencil_vector(self, point, modifiers, pen=CustomPen.PencilVect):
        p1, p2 = self.pencil_tool_draw(point, modifiers)

        if p1 != p2:
            line = QLineF(p1, p2)
            self.temp_item = self._scene.addLine(line, CustomPen.LineVect)
            # self._scene.addPoint(p2, CustomPen.PointVect)
            # if not self.temp_item:
            #     self.temp_item = self._scene.add(line, CustomPen.Line)
            # else:
            #     self.temp_item.setLine(line)

            # if p1 != p2:
            #
            #     self._scene.addLine(QLineF(p1, p2), pen)
            self.lastPoint = p2

    def eraser_raster(self, point, modifiers):
        p1, p2 = self.pencil_tool_draw(point, modifiers)
        self._canvas.drawLine(QLine(p1, p2), CustomPen.Eraser)
        self.lastPoint = p2

    def eraser_vector(self, point, modifiers):
        grab_item = self._scene.itemAt(point, self.transform())
        if grab_item is not self._pen_size_ellipse:
            if isinstance(grab_item, RulerGroup):
                pass
            elif grab_item.parentItem() is None:
                self._scene.removeItem(grab_item)
            else:
                self._scene.removeItem(grab_item.parentItem())

    def line_tool_draw(self, point, modifiers):
        p1 = QPointF(self.lastPoint)
        p2 = QPointF(point)
        if modifiers == Qt.ShiftModifier:
            if abs(p1.x() - p2.x()) < abs(p1.y() - p2.y()):
                p2.setX(p1.x())
            else:
                p2.setY(p1.y())

        return p1, p2

    def line_raster(self, point, modifiers):
        p1, p2 = self.line_tool_draw(point, modifiers)
        line = QLineF(p1, p2)
        if not self.temp_item:
            self.temp_item = self._scene.addSmoothLine(line, CustomPen.Line)
        else:
            self.temp_item.setLine(line)

    def line_vector(self, point, modifiers):
        p1, p2 = self.line_tool_draw(point, modifiers)
        line = QLineF(p1, p2)
        if not self.temp_item:
            self.temp_item = self._scene.addLine(line, CustomPen.LineVect)
        else:
            self.temp_item.setLine(line)

    def rect_tool_draw(self, point, modifiers):

        p1 = QPointF(self.lastPoint)
        p2 = QPointF(point)

        if p2.x() >= p1.x() and p2.y() >= p1.y():
            return p1, p2
        elif p1.x() > p2.x() and p1.y() > p2.y():
            return p2, p1
        elif p2.x() >= p1.x() and p2.y() < p1.y():
            y1, y2 = p2.y(), p1.y()
            p1.setY(y1)
            p2.setY(y2)
        else:
            x1, x2 = p2.x(), p1.x()
            p1.setX(x1)
            p2.setX(x2)
        return p1, p2

    def rect_raster(self, point, modifiers):
        p1, p2 = self.rect_tool_draw(point, modifiers)
        rect = QRectF(p1, p2)

        if not self.temp_item:
            self.temp_item = self._scene.addSmoothRect(rect, CustomPen.Line)
        else:
            self.temp_item.setRect(rect)

    def rect_vector(self, point, modifiers):
        p1, p2 = self.rect_tool_draw(point, modifiers)
        rect = QRectF(p1, p2)

        if not self.temp_item:
            self._selector = self._scene.addSelector(rect, (self._click_x, self._click_y, self._multiplier))
            self.temp_item = self._scene.addRect(rect, CustomPen.LineVect)
        else:
            self._selector.setRect(rect)
            self.temp_item.setRect(rect)

    def ellipse_tool_mode(self, point, modifiers):

        delta = self.lastPoint - point

        if modifiers == Qt.ShiftModifier:

            if delta.x() > delta.y():
                p1 = self.lastPoint - QPointF(delta.x(), delta.x())
                p2 = self.lastPoint + QPointF(delta.x(), delta.x())
            else:
                p1 = self.lastPoint - QPointF(delta.y(), delta.y())
                p2 = self.lastPoint + QPointF(delta.y(), delta.y())

        else:
            p1 = self.lastPoint - delta
            p2 = self.lastPoint + delta

        return p1, p2

    def ellipse_raster(self, point, modifiers, pen=CustomPen.Ellipse):
        p1, p2 = self.ellipse_tool_mode(point, modifiers)
        rect = QRectF(p1, p2)

        if not self.temp_item:
            self.temp_item = self._scene.addSmoothEllipse(rect, pen)
        else:
            self.temp_item.setRect(rect)

    def ellipse_vector(self, point, modifiers, pen=CustomPen.Ellipse):
        p1, p2 = self.ellipse_tool_mode(point, modifiers)
        rect = QRectF(p1, p2)

        if not self.temp_item:
            self._selector = self._scene.addSelector(rect, (self._click_x, self._click_y, self._multiplier))
            self.temp_item = self._scene.addEllipse(rect, pen)
        else:
            self._selector.setRect(rect)
            self.temp_item.setRect(rect)

    def ruler_vector(self, point, modifiers, pen=CustomPen.LineVect):
        p1, p2 = self.rect_tool_draw(point, modifiers)
        rect = QRectF(p1, p2)

        if not self.temp_item:
            self._selector = self._scene.addSelector(rect, (self._click_x, self._click_y, self._multiplier))
            self.temp_item = self._scene.addRuler(rect, self.ruler_step * self._px_at_mil_h, pen)
        else:
            self._selector.setRect(rect)
            self.temp_item.setRect(rect)

    def mousePressEvent(self, event):
        # if True:
        #     self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())

        if (event.button() & (Qt.LeftButton | Qt.RightButton)) and self.draw_mode != DrawMode.Notool:
            # make drawing flag true
            self.drawing = True
            # make last point to the point of cursor
            self.lastPoint = self.mapToScene(event.pos()).toPoint()

        elif (event.button() & (Qt.LeftButton | Qt.RightButton)) and self.draw_mode == DrawMode.Notool:
            point = self.mapToScene(event.pos()).toPoint()
            grab_item = self._scene.itemAt(point, self.transform())
            if grab_item is not self._pen_size_ellipse:
                print(grab_item)

        super(VectoRaster, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        point = self.mapToScene(event.pos()).toPoint()
        modifiers = QApplication.keyboardModifiers()

        # if self.draw_mode != DrawMode.Notool:
        self._pen_size_ellipse.setPos(point.x() - 0.5, point.y() - 0.5)

        if (event.buttons() == Qt.RightButton) & self.drawing:
            if self._vector_mode:
                self.eraser_vector(point, modifiers)
            else:
                self.eraser_raster(point, modifiers)

        elif (event.buttons() & Qt.LeftButton) & self.drawing:

            if self.draw_mode == DrawMode.Pencil:

                if self._vector_mode:
                    self.pencil_vector(point, modifiers)
                else:
                    self.pencil_raster(point, modifiers)

            elif self.draw_mode == DrawMode.Eraser:
                if self._vector_mode:
                    self.eraser_vector(point, modifiers)
                else:
                    self.eraser_raster(point, modifiers)

            elif self.draw_mode == DrawMode.Line:
                if self._vector_mode:
                    self.line_vector(point, modifiers)
                else:
                    self.line_raster(point, modifiers)

            elif self.draw_mode == DrawMode.Rect:
                if self._vector_mode:
                    self.rect_vector(point, modifiers)
                else:
                    self.rect_raster(point, modifiers)

            elif self.draw_mode == DrawMode.Ellipse:
                if self._vector_mode:
                    self.ellipse_vector(point, modifiers)
                else:
                    self.ellipse_raster(point, modifiers)

            elif self.draw_mode == DrawMode.Ruler:
                if self._vector_mode:
                    self.ruler_vector(point, modifiers)

        super(VectoRaster, self).mouseMoveEvent(event)

    # method for mouse left button release
    def mouseReleaseEvent(self, event):
        point = self.mapToScene(event.pos()).toPoint()

        if event.buttons() == Qt.RightButton:
            grab_item = self._scene.itemAt(point, self.transform())
            if grab_item is not self._pen_size_ellipse:
                if isinstance(grab_item, RulerGroup):
                    pass
                elif grab_item.parentItem() is None:
                    self._scene.removeItem(grab_item)
                else:
                    self._scene.removeItem(grab_item.parentItem())

        elif event.button() == Qt.LeftButton:

            if not self._vector_mode:
                if self.draw_mode == DrawMode.Pencil:
                    self._canvas.drawPoint(self.lastPoint, CustomPen.Pencil)

                elif self.draw_mode == DrawMode.Eraser:
                    self._canvas.drawPoint(self.lastPoint, CustomPen.Eraser)

                elif self.draw_mode == DrawMode.Line and self.temp_item:
                    self._canvas.drawLine(self.temp_item.line(), CustomPen.Line)

                elif self.draw_mode == DrawMode.Rect and self.temp_item:
                    self._canvas.drawRect(self.temp_item.item(), CustomPen.Line)

                elif self.draw_mode == DrawMode.Ellipse and self.temp_item:
                    self._canvas.drawEllipse(self.temp_item.item(), CustomPen.Ellipse)

                if self.temp_item:
                    self._scene.removeItem(self.temp_item)

            else:
                if not self.temp_item:

                    if self.draw_mode == DrawMode.Eraser:
                        grab_item = self._scene.itemAt(point, self.transform())
                        if grab_item is not self._pen_size_ellipse:
                            if isinstance(grab_item, RulerGroup):
                                pass
                            elif grab_item.parentItem() is None:
                                self._scene.removeItem(grab_item)
                            else:
                                self._scene.removeItem(grab_item.parentItem())

                    elif self.draw_mode == DrawMode.Pencil:
                        self._scene.addPoint(point, CustomPen.PencilVect, CustomBrush.Black)

                    # elif self.draw_mode == DrawMode.Notool:
                    #     grab_item = self._scene.itemAt(point, self.transform())
                    #     if grab_item is not self._pen_size_ellipse:
                    #         print(grab_item.line())

            if self.temp_item:
                self.temp_item = None

        self.lastPoint = point

        # make drawing flag false
        self.drawing = False
        if self._selector:
            self._scene.removeItem(self._selector)
            self._selector = None

        super(VectoRaster, self).mouseReleaseEvent(event)

    @hide_grid
    @hide_canvas
    def get_vectors(self, grouping=True, *args, **kwargs):

        template = []
        count = 0
        for i in self._scene.items():
            rule = (i.parentItem() is None) if grouping else (not isinstance(i, RulerGroup))

            if i.isVisible() and rule:

                count += 1
                if isinstance(i, RulerGroup):
                    template.append(i.toJson(self._click_x, self._click_y, self._multiplier))
                elif isinstance(i, PointItem):
                    template.append(i.toJson(self._click_x, self._click_y, self._multiplier))
                elif isinstance(i, LineItem):
                    template.append(i.toJson(self._click_x, self._click_y, self._multiplier))
                elif isinstance(i, RectItem) and not isinstance(i, RulerGroup):
                    template.append(i.toJson(self._click_x, self._click_y, self._multiplier))
                elif isinstance(i, EllipseItem):
                    template.append(i.toJson(self._click_x, self._click_y, self._multiplier))

        return template

    @hide_grid
    def save_raster(self, *args, **kwargs):
        out_pix = QPixmap(self._scene.width(), self._scene.height())
        painter = QPainter(out_pix)
        out_pix.fill(Qt.white)

        self._scene.render(painter, QRectF(out_pix.rect()), QRectF(self._scene.sceneRect()),
                           Qt.KeepAspectRatio)

        painter.end()
        out_pix.save(f'test_scene_{round(self._click_x, 2)}_{round(self._click_y, 2)}.bmp', 'BMP')

    def resizeEvent(self, event: 'QResizeEvent') -> None:
        self.fitInView()
        return super(VectoRaster, self).resizeEvent(event)


class Window(QWidget):
    def __init__(self, filename=None):
        super(Window, self).__init__()
        self.setObjectName('RetEdit')

        self.setStyleSheet("#RetEdit {background-color: rgb(72, 72, 72);}")

        self.filename = filename if filename is not None else 'reticle.abcv'

        self.filename = Path(self.filename)
        if self.filename.exists():
            if self.filename.suffix == '.abcv':
                self.viewer = VectoRaster(self, QSize(640, 480), clicks=QSizeF(0.5, 0.5), vector_mode=True)
                with open(self.filename, 'r') as fp:
                    self.template = json.load(fp)
                self.viewer.load_reticle_sketch(self.template)
            elif self.filename.suffix == '.bmp':
                self.viewer = VectoRaster(self, QSize(640, 480), clicks=QSizeF(2.01, 2.01))
                self.viewer.setPhoto(QPixmap(self.filename))
            else:
                sys.exit()
        else:
            sys.exit()

        # 'Load image' button
        self.btnLoad = QToolButton(self)
        self.btnLoad.setText('Load image')
        self.btnLoad.clicked.connect(self.loadImage)
        # Button to change from drag/pan to getting pixel info
        self.btnPixInfo = QToolButton(self)
        self.btnPixInfo.setText('Enter pixel info mode')
        self.btnPixInfo.clicked.connect(self.pixInfo)

        self.editPixInfo = QLineEdit(self)
        self.editPixInfo.setReadOnly(True)
        self.viewer.photoClicked.connect(self.photoClicked)

        self.btnLoad.setHidden(True)
        self.btnPixInfo.setHidden(True)
        self.editPixInfo.setHidden(True)

        self.no_tool_btn = DrawModeBtn(self)
        # self.no_tool_btn.setText('NoTool')
        self.no_tool_btn.setIcon(QIcon('rsrc/hand-index.svg'))
        self.no_tool_btn.setDown(True)
        self.no_tool_btn.clicked.connect(self.on_notool_btn_press)

        self.pencil_btn = DrawModeBtn(self)
        # self.pencil_btn.setText('Pencil')
        self.pencil_btn.setIcon(QIcon('rsrc/pencil.svg'))
        self.pencil_btn.clicked.connect(self.on_draw_btn_press)

        self.eraser_btn = DrawModeBtn(self)
        # self.eraser_btn.setText('Eraser')
        self.eraser_btn.setIcon(QIcon('rsrc/eraser.svg'))
        self.eraser_btn.clicked.connect(self.on_eraser_btn_press)

        self.line_btn = DrawModeBtn(self)
        # self.line_btn.setText('Line')
        self.line_btn.setIcon(QIcon('rsrc/slash-lg.svg'))
        self.line_btn.clicked.connect(self.on_line_btn_press)

        self.clear_btn = QToolButton(self)
        self.clear_btn.setFixedSize(50, 40)
        self.clear_btn.setText('Clear')
        self.clear_btn.clicked.connect(self.on_clear_btn_press)

        self.to_svg_btn = QToolButton(self)
        # self.to_svg_btn.setText('To SVG')
        self.to_svg_btn.setIcon(QIcon('rsrc/filetype-json.svg'))
        self.to_svg_btn.setFixedSize(50, 40)
        self.to_svg_btn.clicked.connect(self.on_to_svg_btn_press)

        self.raster_btn = QToolButton(self)
        # self.raster_btn.setText('To BMP')
        self.raster_btn.setIcon(QIcon('rsrc/filetype-bmp.svg'))
        self.raster_btn.setFixedSize(50, 40)
        self.raster_btn.clicked.connect(self.on_raster_btn_press)

        self.rect_btn = DrawModeBtn()
        # self.rect_btn.setText('Rect')
        self.rect_btn.setIcon(QIcon('rsrc/square.svg'))
        self.rect_btn.clicked.connect(self.on_rect_btn_press)

        self.ellipse_btn = DrawModeBtn()
        # self.ellipse_btn.setText('Ellipse')
        self.ellipse_btn.setIcon(QIcon('rsrc/circle.svg'))
        self.ellipse_btn.clicked.connect(self.on_ellipse_btn_press)

        self.ruler_btn = DrawModeBtn()
        # self.ruler_btn.setText('Ruler')
        self.ruler_btn.setIcon(QIcon('rsrc/rulers.svg'))
        self.ruler_btn.clicked.connect(self.on_ruler_btn_press)

        self.ruler_combo = QComboBox()
        self.ruler_combo.setFixedSize(70, 40)
        for i in [0.05, 0.1, 0.2, 0.25, 0.3, 0.5, 1, 2, 5, 10]:
            self.ruler_combo.addItem(f'{i} mil', i)
        self.ruler_combo.currentIndexChanged.connect(self.ruler_step_change)

        if not self.viewer._vector_mode:
            self.to_svg_btn.setHidden(True)
            self.ruler_btn.setHidden(True)

        # self.drawing = False
        # make last point to the point of cursor
        self.lastPoint = QPoint()

        # hotkey binds
        self.no_tool_btn.setShortcut(Qt.Key_1)
        self.pencil_btn.setShortcut(Qt.Key_2)
        self.eraser_btn.setShortcut(Qt.Key_3)
        self.line_btn.setShortcut(Qt.Key_4)
        self.rect_btn.setShortcut(Qt.Key_5)
        self.ellipse_btn.setShortcut(Qt.Key_6)
        self.ruler_btn.setShortcut(Qt.Key_7)
        self.raster_btn.setShortcut(Qt.CTRL + Qt.Key_S)

        # Arrange layout
        VBlayout = QVBoxLayout(self)
        VBlayout.setContentsMargins(0, 0, 0, 0)
        VBlayout.addWidget(self.viewer)

        HBlayout = QHBoxLayout()
        HBlayout.setAlignment(Qt.AlignLeft)
        HBlayout.addWidget(self.btnLoad)
        HBlayout.addWidget(self.btnPixInfo)
        HBlayout.addWidget(self.editPixInfo)
        HBlayout.addWidget(self.no_tool_btn)
        HBlayout.addWidget(self.pencil_btn)
        HBlayout.addWidget(self.eraser_btn)
        HBlayout.addWidget(self.line_btn)
        HBlayout.addWidget(self.rect_btn)
        HBlayout.addWidget(self.ellipse_btn)
        HBlayout.addWidget(self.ruler_btn)
        HBlayout.addWidget(self.ruler_combo)
        HBlayout.addWidget(self.clear_btn)
        HBlayout.addWidget(self.to_svg_btn)
        HBlayout.addWidget(self.raster_btn)
        VBlayout.addLayout(HBlayout)

        self.installEventFilter(self.viewer._scene)

    def on_draw_btn_press(self):
        self.on_notool_btn_press()
        self.viewer.draw_mode = DrawMode.Pencil
        self.viewer.toggleDragMode()

    def on_eraser_btn_press(self):
        self.on_notool_btn_press()
        self.viewer.draw_mode = DrawMode.Eraser
        self.viewer.toggleDragMode()

    def on_line_btn_press(self):
        self.on_notool_btn_press()
        self.viewer.draw_mode = DrawMode.Line
        self.viewer.toggleDragMode()

    def on_notool_btn_press(self):
        self.viewer.draw_mode = DrawMode.Notool
        self.viewer.toggleDragMode()

        buttons = self.findChildren(DrawModeBtn)
        for b in buttons:
            b.reset()
        self.sender().setDown(True)

    def on_rect_btn_press(self):
        self.on_notool_btn_press()
        self.viewer.draw_mode = DrawMode.Rect
        self.viewer.toggleDragMode()

    def on_ellipse_btn_press(self):
        self.on_notool_btn_press()
        self.viewer.draw_mode = DrawMode.Ellipse
        self.viewer.toggleDragMode()

    def on_ruler_btn_press(self):
        self.on_notool_btn_press()
        self.viewer.draw_mode = DrawMode.Ruler
        self.viewer.toggleDragMode()

    def on_raster_btn_press(self, *args, **kwargs):
        for i in [1, 2, 3, 4, 6]:
            # viewer = VectoRaster(self, clicks=QSizeF(2.01, 2.01) / i)
            viewer = VectoRaster(self, clicks=QSizeF(1.42, 1.42) / i)
            viewer.rasterize(self.viewer.get_vectors(False))
            viewer.save_raster()

    def on_to_svg_btn_press(self, *args, **kwargs):
        self.save_vectors()

    def on_clear_btn_press(self):
        self.viewer.clear_view()

    def ruler_step_change(self, idx):
        self.viewer.ruler_step = self.ruler_combo.currentData()

    def save_vectors(self):
        template = self.viewer.get_vectors()
        with open(self.filename, 'w') as fp:
            json.dump(template, fp)

    def loadImage(self):
        self.viewer.setPhoto(QPixmap('1_3 MIL-R.bmp'))

    def pixInfo(self):
        self.viewer.toggleDragMode()

    def photoClicked(self, pos):
        if self.viewer.dragMode() == QGraphicsView.NoDrag:
            self.editPixInfo.setText('%d, %d' % (pos.x(), pos.y()))


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    filename = app.arguments()[1] if len(app.arguments()) > 1 else None
    window = Window(filename)
    window.setGeometry(500, 300, 800, 600)
    window.show()
    sys.exit(app.exec_())
