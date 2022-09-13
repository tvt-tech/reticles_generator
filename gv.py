import json
import math
from enum import IntFlag, IntEnum, auto
from functools import wraps

from PyQt5.QtCore import QLine, QPoint, QPointF, pyqtSignal, QSize, QSizeF
from PyQt5.QtGui import QBrush, QPolygonF, QTransform, QMouseEvent, QFont, QKeySequence
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtWidgets import QApplication, QGraphicsPixmapItem, \
    QToolButton, QGraphicsView, QVBoxLayout, QHBoxLayout, QFrame, \
    QLineEdit, QShortcut

from canvas import GraphicsCanvas
from drawable_scene import DrawbleGraphicScene
from example_grid import example_grid
from grid_step import *
from smooth_item import *


def hide_grid(func: callable):
    @wraps(func)
    def _impl(self, *method_args, **method_kwargs):
        children = self._scene.items()
        for ch in children:
            if hasattr(ch, 'pen'):
                if ch.pen().color() == Qt.darkMagenta or ch.pen().color() == Qt.magenta:
                    ch.setVisible(False)

            if hasattr(ch, 'defaultTextColor'):
                if ch.defaultTextColor() == Qt.darkMagenta or ch.defaultTextColor() == Qt.magenta:
                    ch.setVisible(False)
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


class ItemType(IntEnum):
    Point = 1
    Line = 2
    Rect = 3
    Ellipse = 4
    Circle = 5
    Polygon = 6
    Text = 7


class CustomPen:
    GridH1 = QPen(Qt.darkMagenta, 0.2, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    GridH2 = QPen(Qt.darkMagenta, 0.15, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    GridH3 = QPen(Qt.darkMagenta, 0.05, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    GridH4 = QPen(Qt.darkMagenta, 0.02, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    GridH5 = QPen(Qt.darkMagenta, 0.01, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    Pencil = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)
    PencilVect = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)
    PointVect = QPen(Qt.transparent, 0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    Eraser = QPen(Qt.transparent, 1, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)
    Line = QPen(Qt.black, 1, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
    LineVect = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    Ellipse = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)


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
        # self.setFixedSize(size)

        # drawing flags
        self._vector_mode = vector_mode
        self.draw_mode = DrawMode.Notool
        self.drawing = False
        self.temp_item = None
        self.lastPoint = None

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
        self._px_at_1_mil_h = 1
        self._px_at_1_mil_v = 1
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
        # self._min_mil_h_step = _min_mil_h_step
        # self._min_mil_v_step = _min_mil_v_step
        print(self._min_mil_h_step, self._min_mil_v_step)
        self._min_px_h_step = self._min_mil_h_step * self._px_at_1_mil_h  # min horizontal step in pix at mil
        self._min_px_v_step = self._min_mil_v_step * self._px_at_1_mil_v  # min vertical step in pix at mil

        # set view flags
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
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
        self.draw_mil_grid(10, 10, True, True, CustomPen.GridH2)
        self.draw_mil_grid(1, 1, True, False, CustomPen.GridH3, font_size=5)
        self.draw_mil_grid(self._min_px_h_step, self._min_px_v_step, True, False, CustomPen.GridH4)
        self.draw_mil_grid(100, 100, True, False, CustomPen.GridH1)

    def draw_vector_mode_grid(self):
        # self.draw_mil_grid(0.05, 0.05, True, False, CustomPen.GridH5)
        self.draw_mil_grid(0.1, 0.1, True, False, CustomPen.GridH4)
        self.draw_mil_grid(1, 1, True, True, CustomPen.GridH3, font_size=5)
        self.draw_mil_grid(5, 5, True, False, CustomPen.GridH3, font_size=8)
        self.draw_mil_grid(10, 10, True, False, CustomPen.GridH2)
        self.draw_mil_grid(100, 100, True, False, CustomPen.GridH1)

    def rasterize(self, sketch=example_grid):


        found_trashhold = [100]

        for item in sketch:

            if item['t'] == ItemType.Line:
                if item['mode'] == 'pt':

                    if item['p1'][0] == item['p2'][0] != 0 and item['p1'][0] % self._min_mil_h_step > 0:
                        print(item['p1'][0] % self._min_mil_h_step, item['p1'])
                        found_trashhold.append(item['p1'][0] % self._min_mil_h_step)
                        pen = QPen(Qt.darkRed, 1, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
                        # continue

                    elif item['p1'][1] == item['p2'][1] != 0 and item['p1'][1] % self._min_mil_v_step > 0:
                        print(item['p1'][1] % self._min_mil_v_step, item['p1'])
                        pen = QPen(Qt.darkRed, 1, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
                        # continue

                    else:
                        pen = CustomPen.Line

                    p1 = [self._px_at_1_mil_h * item['p1'][0], self._px_at_1_mil_v * item['p1'][1]]
                    p2 = [self._px_at_1_mil_h * item['p2'][0], self._px_at_1_mil_v * item['p2'][1]]

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

                else:
                    p1 = QPoint(item['p1'])
                    p2 = QPoint(item['p2'])

                if item['t'] == ItemType.Line:
                    line = QLine(p1, p2)

                    # pen.setWidth(item['pen'])
                    self._canvas.drawLineC(line, pen)
        print(min(found_trashhold))
            # if item['t'] == (ItemType.Rect or ItemType.Ellipse):
            #
            #     if int((item['p1'][0] or item['p2'][0]) % self._min_mil_h_step) > 0:
            #         continue
            #
            #     if int((item['p1'][1] or item['p2'][1]) % self._min_mil_v_step) > 0:
            #         continue
            #
            #     p1 = (int(self._px_at_1_mil_h * item['p1'][0]), int(self._px_at_1_mil_v * item['p1'][1]))
            #     p2 = (int(self._px_at_1_mil_h * item['p2'][0]), int(self._px_at_1_mil_v * item['p2'][1]))
            #
            #     if item['t'] == ItemType.Rect:
            #         rect = QRect(*p1, *p2)
            #         pen = CustomPen.Line
            #         pen.setWidth(item['pen'])
            #         self._canvas.drawRectC(rect, pen)
            #
            #     if item['t'] == ItemType.Ellipse:
            #         rect = QRect(*p1, *p2)
            #         pen = CustomPen.Ellipse
            #         pen.setWidth(item['pen'])
            #         self._canvas.drawEllipseC(rect, pen)
            #
            # if item['t'] == ItemType.Point:
            #     if item['mode'] == 'pt':
            #         if int(item['p'][0] % self._min_mil_h_step) > 0:
            #             continue
            #
            #         elif int(item['p'][1] % self._min_mil_v_step) > 0:
            #             continue
            #
            #         point = QPoint(
            #             int(self._px_at_1_mil_h * item['p'][0]),
            #             int(self._px_at_1_mil_v * item['p'][1])
            #         )
            #     else:
            #         point = QPoint(*item['p'])
            #
            #     pen = CustomPen.Line
            #     pen.setWidth(item['pen'])
            #     self._canvas.drawPointC(point, pen)
            #
            # if item['t'] == ItemType.Circle:
            #     if item['mode'] == 'pt':
            #         if int(item['p'][0] % self._min_mil_h_step) > 0:
            #             continue
            #
            #         elif int(item['p'][1] % self._min_mil_v_step) > 0:
            #             continue
            #
            #         elif int(item['r'] % (self._min_mil_h_step or self._min_mil_v_step)) > 0:
            #             continue
            #
            #         p1 = (
            #             int(self._px_at_1_mil_h * (item['p'][0] - item['r'])),
            #             int(self._px_at_1_mil_v * (item['p'][1] - item['r']))
            #         )
            #         p2 = (
            #             int(self._px_at_1_mil_h * (item['p'][0] + item['r'])),
            #             int(self._px_at_1_mil_v * (item['p'][1] + item['r']))
            #         )
            #
            #     else:
            #         p1 = (int(item['p'][0] - item['r']), int(item['p'][1] - item['r']))
            #         p2 = (int(item['p'][0] + item['r']), int(item['p'][1] + item['r']))
            #
            #     rect = QRect(*p1, *p2)
            #     pen = CustomPen.Ellipse
            #     pen.setWidth(item['pen'])
            #     self._canvas.drawEllipseC(rect, pen)
            #
            # if item['t'] == ItemType.Polygon:
            #     if item['mode'] == 'pt':
            #         points = [QPoint(int(self._px_at_1_mil_h * x), int(self._px_at_1_mil_v * y)) for x, y in
            #                   item['points']]
            #     else:
            #         points = [QPoint(x, y) for x, y in item['points']]
            #     polygon = QPolygonF(points)
            #
            #     pen = CustomPen.Line
            #     pen.setWidth(item['pen'])
            #     self._canvas.drawPolygonC(polygon, pen)

    def load_reticle_sketch(self, sketch=example_grid):

        for item in sketch:
            if item['t'] == ItemType.Line:

                if not self._vector_mode:

                    # if item['p1'][0] == item['p2'][0] != 0 and round(abs(item['p1'][0]), 2) % self._min_mil_h_step > 0:
                    if item['p1'][0] == item['p2'][0] != 0 and abs(item['p1'][0]) % self._min_mil_h_step > 1e-2:
                        continue
                    #
                    if item['p1'][1] == item['p2'][1] != 0 and abs(item['p1'][1]) % self._min_mil_v_step > 1e-2:
                        # if item['p1'][1] == item['p2'][1] != 0 and round(abs(item['p1'][1]), 2) % self._min_mil_v_step > 0:
                        continue

                if item['mode'] == 'pt':
                    p1 = [self._px_at_1_mil_h * item['p1'][0], self._px_at_1_mil_v * item['p1'][1]]
                    p2 = [self._px_at_1_mil_h * item['p2'][0], self._px_at_1_mil_v * item['p2'][1]]

                    if not self._vector_mode:
                        if 0 < abs(p1[0]) < self._min_px_h_step:
                            p1[0] = p1[0] / abs(p1[0])

                        if 0 < abs(p2[0]) < self._min_px_h_step:
                            p2[0] = p2[0] / abs(p2[0])

                        if 0 < abs(p1[1]) < self._min_px_v_step:
                            p1[1] = p1[1] / abs(p1[1])

                        if 0 < abs(p2[1]) < self._min_px_v_step:
                            p2[1] = p2[1] / abs(p2[1])

                else:
                    p1 = item['p1']
                    p2 = item['p2']

                # if 0 < abs(p1[0]) < self._min_px_h_step:
                #     p1[0] = p1[0] / abs(p1[0]) * self._min_px_h_step
                #
                # if 0 < abs(p2[0]) < self._min_px_h_step:
                #     p2[0] = p2[0] / abs(p2[0]) * self._min_px_h_step
                #
                # if 0 < abs(p1[1]) < self._min_px_v_step:
                #     p1[1] = p1[1] / abs(p1[1]) * self._min_px_v_step
                #
                # if 0 < abs(p2[1]) < self._min_px_v_step:
                #     p2[1] = p2[1] / abs(p2[1]) * self._min_px_v_step

                line = QLineF(*p1, *p2)
                # pen = CustomPen.Line
                pen = CustomPen.PencilVect
                # pen.setWidth(item['pen'])
                # self._scene.addLineC(line, pen)
                self._scene.addLine(line, pen)

            if item['t'] == ItemType.Rect:
                if item['mode'] == 'pt':
                    p1 = (self._px_at_1_mil_h * item['p1'][0], self._px_at_1_mil_v * item['p1'][1])
                    p2 = (self._px_at_1_mil_h * item['p2'][0], self._px_at_1_mil_v * item['p2'][1])

                else:
                    p1 = item['p1']
                    p2 = item['p2']

                print(p1, p2)

                rect = QRectF(*p1, *p2)
                # pen = CustomPen.Line
                pen = CustomPen.LineVect
                # pen.setWidth(item['pen'])
                # self._scene.addRectC(rect, pen)
                self._scene.addRect(rect, pen)

            if item['t'] == ItemType.Point:
                if item['mode'] == 'pt':
                    p = (
                        self._px_at_1_mil_h * item['p'][0],
                        self._px_at_1_mil_v * item['p'][1]
                    )
                else:
                    p = item['p']

                point = QPointF(*p)
                # pen = CustomPen.Line
                pen = CustomPen.PointVect
                # pen.setWidth(item['pen'])
                self._scene.addPoint(point, pen)
                # self._scene.addPointC(point, pen)

            if item['t'] in [ItemType.Ellipse, ItemType.Circle]:
                if item['mode'] == 'pt':
                    p1 = (self._px_at_1_mil_h * item['p1'][0], self._px_at_1_mil_v * item['p1'][1])
                    p2 = (self._px_at_1_mil_h * item['p2'][0], self._px_at_1_mil_v * item['p2'][1])

                else:
                    p1 = item['p1']
                    p2 = item['p2']

                rect = QRectF(*p1, *p2)
                # pen = CustomPen.Ellipse
                pen = CustomPen.PencilVect
                # pen.setWidth(item['pen'])
                # self._scene.addEllipseC(rect, pen)
                self._scene.addEllipse(rect, pen)

            # if item['t'] == ItemType.Polygon:
            #     if item['mode'] == 'pt':
            #         points = [QPointF(self._px_at_1_mil_h * x, self._px_at_1_mil_v * y) for x, y in
            #                   item['points']]
            #     else:
            #         points = [QPointF(x, y) for x, y in item['points']]
            #     polygon = QPolygonF(points)
            #
            #     # pen = CustomPen.Line
            #     pen = CustomPen.Line
            #     # pen.setWidth(item['pen'])
            #     # self._scene.addPolygonC(polygon, pen)
            #     self._scene.addPolygon(polygon, pen)

    def set_reticle_scale(self):
        self._px_at_1_mil_h = self._multiplier / self._click_x
        self._px_at_1_mil_v = self._multiplier / self._click_y

    def draw_mil_grid(self, step_h=10.0, step_v=10.0, grid=False, mark=False, pen: QPen = QPen(), font_size=10):

        grid_scale_h_f = self._px_at_1_mil_h * step_h
        grid_scale_v_f = self._px_at_1_mil_v * step_v
        grid_scale_h = int(grid_scale_h_f)
        grid_scale_v = int(grid_scale_v_f)

        if (grid_scale_h and grid_scale_v) == 0:
            return

        scene_rect = self._scene.sceneRect()
        max_x = int(scene_rect.width() / 2)
        max_y = int(scene_rect.height() / 2)

        font = QFont()
        font.setPixelSize(font_size)

        for i, x in enumerate(range(0, max_x, grid_scale_h)):
            xF = i * grid_scale_h_f
            if grid:
                line1 = QLineF(xF, max_y, xF, -max_y)
                line2 = QLineF(-xF, max_y, -xF, -max_y)
                self._scene.addLine(line1, pen)
                self._scene.addLine(line2, pen)
            if mark:
                text1 = self._scene.addText(str(round(i * step_h, 1)), font)
                text1.setPos(QPointF(xF, 0))
                text1.setDefaultTextColor(pen.color())
                text2 = self._scene.addText(str(round(i * step_h, 1)), font)
                text2.setPos(QPointF(-xF, 0))
                text2.setDefaultTextColor(pen.color())

        for i, x in enumerate(range(0, max_x, grid_scale_v)):
            yF = i * grid_scale_v_f
            if grid:
                line1 = QLineF(max_x, yF, -max_x, yF)
                line2 = QLineF(max_x, -yF, -max_x, -yF)
                self._scene.addLine(line1, pen)
                self._scene.addLine(line2, pen)
            if mark:
                text1 = self._scene.addText(str(round(i * step_v, 1)), font)
                text1.setPos(QPointF(0, yF))
                text1.setDefaultTextColor(pen.color())
                text2 = self._scene.addText(str(round(i * step_v, 1)), font)
                text2.setPos(QPointF(0, -yF))
                text2.setDefaultTextColor(pen.color())

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
            self.temp_item = self._scene.addLine(line, CustomPen.PencilVect)
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
            self._scene.removeItem(grab_item)

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
            self.temp_item = self._scene.addLine(line, CustomPen.PencilVect)
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
            self.temp_item = self._scene.addRect(rect, CustomPen.LineVect)
        else:
            self.temp_item.setRect(rect)

    def ellipse_tool_mode(self, point, modifiers):
        delta_x = abs(self.lastPoint.x() - point.x())
        delta_y = abs(self.lastPoint.y() - point.y())

        if modifiers == Qt.ShiftModifier:

            if delta_x > delta_y:
                p1 = QPointF(self.lastPoint.x() - delta_x, self.lastPoint.y() - delta_x)
                p2 = QPointF(self.lastPoint.x() + delta_x, self.lastPoint.y() + delta_x)
            else:
                p1 = QPointF(self.lastPoint.x() - delta_y, self.lastPoint.y() - delta_y)
                p2 = QPointF(self.lastPoint.x() + delta_y, self.lastPoint.y() + delta_y)

        else:
            p1 = QPointF(self.lastPoint.x() - delta_x, self.lastPoint.y() - delta_y)
            p2 = QPointF(self.lastPoint.x() + delta_x, self.lastPoint.y() + delta_y)

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
            self.temp_item = self._scene.addEllipse(rect, pen)
        else:
            self.temp_item.setRect(rect)

    def mousePressEvent(self, event):
        # if True:
        #     self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())

        if event.button() == Qt.LeftButton and self.draw_mode != DrawMode.Notool:
            # make drawing flag true
            self.drawing = True
            # make last point to the point of cursor
            self.lastPoint = self.mapToScene(event.pos()).toPoint()

        super(VectoRaster, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        point = self.mapToScene(event.pos()).toPoint()
        modifiers = QApplication.keyboardModifiers()

        # if self.draw_mode != DrawMode.Notool:
        self._pen_size_ellipse.setPos(point.x() - 0.5, point.y() - 0.5)

        if (event.buttons() & Qt.LeftButton) & self.drawing:

            # if modifiers == Qt.ControlModifier and self.draw_mode != DrawMode.Notool:
            #     # self.draw_mode = DrawMode.Eraser
            #     if self._vector_mode:
            #         self.eraser_vector(point, modifiers)
            #     else:
            #         self.eraser_raster(point, modifiers)

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

        self._scene.update()
        super(VectoRaster, self).mouseMoveEvent(event)

    # method for mouse left button release
    def mouseReleaseEvent(self, event):
        point = self.mapToScene(event.pos()).toPoint()
        if event.button() == Qt.LeftButton:

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
                    if self.draw_mode == DrawMode.Pencil:
                        self._scene.addPoint(self.lastPoint, CustomPen.PencilVect, brush=Qt.transparent)

                    elif self.draw_mode == DrawMode.Eraser:
                        grab_item = self._scene.itemAt(point, self.transform())
                        if grab_item is not self._pen_size_ellipse:
                            self._scene.removeItem(grab_item)

                    elif self.draw_mode == DrawMode.Notool:
                        grab_item = self._scene.itemAt(point, self.transform())
                        if grab_item is not self._pen_size_ellipse:
                            print(grab_item.line())

            if self.temp_item:
                self.temp_item = None

        self.lastPoint = point

        # make drawing flag false
        self.drawing = False

        super(VectoRaster, self).mouseReleaseEvent(event)

    @hide_grid
    @hide_canvas
    def save_svg(self, *args, **kwargs):

        # self._canvas.setVisible(False)

        template = []
        count = 0
        for i in self._scene.items():
            # print(i)
            if i.isVisible():
                count += 1
                if isinstance(i, QGraphicsLineItem):
                    line = i.line()
                    template.append({
                        't': ItemType.Line,
                        'p1': (
                            line.x1() * self._click_x / self._multiplier,
                            line.y1() * self._click_y / self._multiplier
                        ),
                        'p2': (
                            line.x2() * self._click_x / self._multiplier,
                            line.y2() * self._click_y / self._multiplier
                        ),
                        'mode': 'pt',
                        'pen': 1,
                    })
                if isinstance(i, QGraphicsRectItem):
                    rect = i.rect()
                    template.append({
                        't': ItemType.Rect,
                        'p1': (
                            rect.x() * self._click_x / self._multiplier,
                            rect.y() * self._click_y / self._multiplier
                        ),
                        'p2': (
                            rect.width() * self._click_x / self._multiplier,
                            rect.height() * self._click_y / self._multiplier
                        ),
                        'mode': 'pt',
                        'pen': 1,
                    })

                if isinstance(i, QGraphicsEllipseItem):
                    rect = i.rect()
                    print(rect)
                    template.append({
                        't': ItemType.Ellipse if rect.width() != rect.height() else ItemType.Circle,
                        'p1': (
                            rect.x() * self._click_x / self._multiplier,
                            rect.y() * self._click_y / self._multiplier
                        ),
                        'p2': (
                            rect.width() * self._click_x / self._multiplier,
                            rect.height() * self._click_y / self._multiplier
                        ),
                        'mode': 'pt',
                        'pen': 1,
                    })

        with open('reticle.abcv', 'w') as fp:
            json.dump(template, fp)

        # svg_gen = QSvgGenerator()
        # svg_gen.setFileName('test_scene.svg')
        # svg_gen.setSize(QSize(int(self.sceneRect().width()), int(self.sceneRect().height())))
        # svg_gen.setViewBox(self.sceneRect())
        # svg_gen.setTitle("SVG Generator Example Drawing")
        # svg_gen.setDescription("An SVG drawing created by the SVG Generator "
        #                        "Example provided with Qt.")
        #
        # painter = QPainter(svg_gen)
        # self._scene.render(painter)
        # painter.end()

        # self._canvas.setVisible(True)

    @hide_grid
    def save_raster(self, *args, **kwargs):
        out_pix = QPixmap(self._scene.width(), self._scene.height())
        painter = QPainter(out_pix)
        out_pix.fill(Qt.white)

        self._scene.render(painter, QRectF(out_pix.rect()), QRectF(self._scene.sceneRect()),
                           Qt.KeepAspectRatio)

        painter.end()
        out_pix.save('test_scene.bmp', 'BMP')

    def resizeEvent(self, event: 'QResizeEvent') -> None:
        self.fitInView()
        return super(VectoRaster, self).resizeEvent(event)


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        # self.setFixedSize(640, 500)

        self.viewer = VectoRaster(self, clicks=QSizeF(0.7525, 0.7525))
        # self.viewer = VectoRaster(self, clicks=QSizeF(0.336, 0.336))
        # self.viewer = VectoRaster(self, clicks=QSizeF(0.5025, 0.5025))
        # self.viewer = VectoRaster(self, clicks=QSizeF(2.01, 2.01))
        # self.viewer = VectoRaster(self, clicks=QSizeF(1.005, 1.005))
        # self.viewer = VectoRaster(self, QSize(640, 480), clicks=QSizeF(0.5, 0.5), vector_mode=True)
        # self.viewer = VectoRaster(self, QSize(640, 480), clicks=QSizeF(2.01, 2.01))
        # self.viewer = VectoRaster(self, QSize(640, 480), clicks=QSizeF(2.01, 2.01))


        with open('reticle.abcv', 'r') as fp:
            template = json.load(fp)
        # self.viewer.load_reticle_sketch(template)
        self.viewer.rasterize(template)

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
        self.no_tool_btn.setText('NoTool')
        self.no_tool_btn.setDown(True)
        self.no_tool_btn.clicked.connect(self.on_notool_btn_press)

        self.pencil_btn = DrawModeBtn(self)
        self.pencil_btn.setText('Pencil')
        self.pencil_btn.clicked.connect(self.on_draw_btn_press)

        self.eraser_btn = DrawModeBtn(self)
        self.eraser_btn.setText('Eraser')
        self.eraser_btn.clicked.connect(self.on_eraser_btn_press)

        self.line_btn = DrawModeBtn(self)
        self.line_btn.setText('Line')
        self.line_btn.clicked.connect(self.on_line_btn_press)

        self.clear_btn = QToolButton(self)
        self.clear_btn.setFixedSize(50, 40)
        self.clear_btn.setText('Clear')
        self.clear_btn.clicked.connect(self.on_clear_btn_press)

        self.to_svg_btn = QToolButton(self)
        self.to_svg_btn.setText('To SVG')
        self.to_svg_btn.setFixedSize(50, 40)
        self.to_svg_btn.clicked.connect(self.on_to_svg_btn_press)

        if not self.viewer._vector_mode:
            self.to_svg_btn.setHidden(True)

        self.raster_btn = QToolButton(self)
        self.raster_btn.setText('To BMP')
        self.raster_btn.setFixedSize(50, 40)
        self.raster_btn.clicked.connect(self.on_raster_btn_press)

        self.rect_btn = DrawModeBtn()
        self.rect_btn.setText('Rect')
        self.rect_btn.clicked.connect(self.on_rect_btn_press)

        self.ellipse_btn = DrawModeBtn()
        self.ellipse_btn.setText('Ellipse')
        self.ellipse_btn.clicked.connect(self.on_ellipse_btn_press)

        self.drawing = False
        # make last point to the point of cursor
        self.lastPoint = QPoint()


        # hotkey binds
        self.no_tool_btn.setShortcut(Qt.Key_1)
        self.pencil_btn.setShortcut(Qt.Key_2)
        self.eraser_btn.setShortcut(Qt.Key_3)
        self.line_btn.setShortcut(Qt.Key_4)



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

    def on_raster_btn_press(self, *args, **kwargs):
        self.viewer.save_raster(*args, **kwargs)

    def on_to_svg_btn_press(self, *args, **kwargs):
        self.viewer.save_svg(*args, **kwargs)

    def on_clear_btn_press(self):
        self.viewer.clear_view()

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
    window = Window()
    window.setGeometry(500, 300, 800, 600)
    window.show()
    sys.exit(app.exec_())
