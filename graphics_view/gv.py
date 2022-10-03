from enum import IntFlag, auto
from functools import wraps

from PyQt5.QtCore import QPoint, QSize
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QGraphicsPixmapItem, QFrame, QGraphicsView, QInputDialog

from graphics_view.canvas import GraphicsCanvas
from graphics_view.custom_graphics_item import *
from graphics_view.drawable_scene import DrawbleGraphicScene
from graphics_view.example_grid import example_grid
from graphics_view.grid_step import *

from pathlib import Path


def hide_grid(func: callable):
    @wraps(func)
    def _impl(self, *method_args, **method_kwargs):
        children = self._scene.items()
        for ch in children:
            if isinstance(ch, GridItem) or isinstance(ch, PenCircle):
                ch.setVisible(False)
        ret = func(self, *method_args, **method_kwargs)
        for ch in children:
            ch.setVisible(True)
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


class DrawMode(IntFlag):
    Notool = auto()
    Pencil = auto()
    Eraser = auto()
    Line = auto()
    Rect = auto()
    Ellipse = auto()
    Text = auto()
    Ruler = auto()
    Numbers = auto()


class MyCanvasItem(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        super(MyCanvasItem, self).__init__(parent)

    def paint(self, painter, option, widget=None):
        super(MyCanvasItem, self).paint(painter, option, widget)

    # def drawLine(self):


class VectoRaster(QGraphicsView):

    def __init__(self, parent=None,
                 size: QSize = QSize(640, 480),
                 clicks: QSizeF = QSizeF(2.01, 2.01)):
        super(VectoRaster, self).__init__(parent)

        self.setRenderHint(QPainter.Antialiasing)
        self.setCursor(Qt.CrossCursor)

        # drawing flags
        self.draw_mode = DrawMode.Notool
        self.drawing = False
        self.temp_item = None
        self.lastPoint = None
        self._selector = None
        self.ruler_step = 1

        self._history = []
        self._history_idx = -1

        self.mil_grids = []

        self.w = size.width()
        self.h = size.height()

        self._zoom = 0

        self._click_x = clicks.width()
        self._click_y = clicks.height()

        # init canvas center coords
        self._x0 = int(self.w / 2)
        self._y0 = int(self.h / 2)

        # count reticle scale
        self._multiplier = 10  # cm/mil
        self._px_at_mil_h = 1
        self._px_at_mil_v = 1
        self.set_reticle_scale()

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
        rect = QRectF(-self.w / 2, -self.h / 2, self.w, self.h)
        self._scene = DrawbleGraphicScene(self)
        self._scene.setSceneRect(rect)

        self._canvas = GraphicsCanvas(self._scene.sceneRect().size())
        self._canvas.setPos(-0.5, -0.5)
        self._scene.addItem(self._canvas)

        self.draw_grid()
        self.draw_background()

        self._pen_size_ellipse = PenCircle()
        self._scene.addItem(self._pen_size_ellipse)

        self.setScene(self._scene)
        self.toggleDragMode()

    def draw_grid(self):
        pass

    def draw_background(self):
        pass

    def draw_sketch(self, sketch=example_grid):
        pass

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

    def setPix(self, pixmap=None):
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

    def wheelEvent(self, event: 'QWheelEvent') -> None:
        pass

    def toggleDragMode(self):
        if self.draw_mode != DrawMode.Notool:
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    @hide_grid
    def clear_view(self):
        pass

    def _get_pencil_tool_points(self, point, modifiers):
        p1 = QPoint(self.lastPoint.x(), self.lastPoint.y())
        p2 = QPoint(point.x(), point.y())
        if modifiers == Qt.ShiftModifier:
            if abs(p1.x() - p2.x()) <= abs(p1.y() - p2.y()):
                p2.setY(self.lastPoint.y())
            else:
                p2.setX(self.lastPoint.x())
        return p1, p2

    def _get_line_tool_points(self, point, modifiers):
        p1 = QPointF(self.lastPoint)
        p2 = QPointF(point)
        if modifiers == Qt.ShiftModifier:
            if abs(p1.x() - p2.x()) < abs(p1.y() - p2.y()):
                p2.setX(p1.x())
            else:
                p2.setY(p1.y())
        return p1, p2

    def _get_rect_tool_point(self, point, modifiers):
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

    def _get_ellipse_tool_point(self, point, modifiers):
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

    def _get_text_tool_point(self, point, modifiers):
        p1, p2 = self._get_rect_tool_point(point, modifiers)
        text_field = QInputDialog()
        text = text_field.exec_()
        if text:
            print(text, p1, p2)

    def _pencil(self, point, modifiers, pen=CustomPen.PencilVect):
        pass

    def _erase(self, point, modifiers):
        pass

    def _line(self, point, modifiers):
        pass

    def _rect(self, point, modifiers):
        pass

    def _ellipse(self, point, modifiers):
        pass

    def _ruler(self, point, modifiers):
        pass

    def _numbers(self, point, modifiers):
        pass

    def _text(self, point, modifiers):
        pass

    def del_item(self, grab_item):
        if not isinstance(grab_item, PenCircle):
            if isinstance(grab_item, GridItem):
                pass
            elif isinstance(grab_item, RulerGroup):
                pass
            elif grab_item.parentItem() is None:
                self._scene.removeItem(grab_item)
            else:
                if isinstance(grab_item.parentItem(), RulerGroup):
                    self._scene.removeItem(grab_item.parentItem())

    def mousePressEvent(self, event):

        if (event.button() & (Qt.LeftButton | Qt.RightButton)) and self.draw_mode != DrawMode.Notool:
            # make drawing flag true
            self.drawing = True
            # make last point to the point of cursor
            self.lastPoint = self.mapToScene(event.pos()).toPoint()

        elif (event.button() & (Qt.LeftButton | Qt.RightButton)) and self.draw_mode == DrawMode.Notool:
            point = self.mapToScene(event.pos()).toPoint()
            grab_item = self._scene.itemAt(point, self.transform())
            if not isinstance(grab_item, PenCircle):
                # print(grab_item)
                pass

        super(VectoRaster, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        point = self.mapToScene(event.pos()).toPoint()
        modifiers = QApplication.keyboardModifiers()
        self._pen_size_ellipse.setPos(point.x() - 0.5, point.y() - 0.5)

        if (event.buttons() == Qt.RightButton) & self.drawing:
            self._erase(point, modifiers)
        elif (event.buttons() & Qt.LeftButton) & self.drawing:
            if self.draw_mode == DrawMode.Pencil:
                self._pencil(point, modifiers)
            elif self.draw_mode == DrawMode.Eraser:
                self._erase(point, modifiers)
            elif self.draw_mode == DrawMode.Line:
                self._line(point, modifiers)
            elif self.draw_mode == DrawMode.Rect:
                self._rect(point, modifiers)
            elif self.draw_mode == DrawMode.Ellipse:
                self._ellipse(point, modifiers)
            elif self.draw_mode == DrawMode.Ruler:
                self._ruler(point, modifiers)
            elif self.draw_mode == DrawMode.Text:
                self._text(point, modifiers)
            elif self.draw_mode == DrawMode.Numbers:
                self._numbers(point, modifiers)
        super(VectoRaster, self).mouseMoveEvent(event)

    # method for mouse left button release
    def mouseReleaseEvent(self, event):
        point = self.mapToScene(event.pos()).toPoint()

        if event.buttons() == Qt.RightButton:
            grab_item = self._scene.itemAt(point, self.transform())
            if not isinstance(grab_item, PenCircle):
                if isinstance(grab_item, RulerGroup):
                    pass
                elif grab_item.parentItem() is None:
                    self._scene.removeItem(grab_item)
                else:
                    self._scene.removeItem(grab_item.parentItem())

        elif event.button() == Qt.LeftButton:
            self._release_mouse_button(point)
            if self.temp_item:
                self.temp_item = None

        self.lastPoint = point

        # make drawing flag false
        self.drawing = False
        if self._selector:
            self._scene.removeItem(self._selector)
            self._selector = None

        super(VectoRaster, self).mouseReleaseEvent(event)
        self._history_append()

    def _release_mouse_button(self, point):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

    def _history_append(self):
        pass

    @hide_grid
    @hide_canvas
    def get_vectors(self, grouping=True):
        template = []
        for i in self._scene.items():
            rule = (i.parentItem() is None) if grouping else (not isinstance(i, RulerGroup))
            rule1 = not (isinstance(i, RectItem) and isinstance(i, RulerGroup))
            if i.isVisible() and rule and rule1:
                template.append(i.toJson(self._click_x, self._click_y, self._multiplier))
        return template

    @hide_grid
    def get_raster(self, fill_color=Qt.transparent):
        out_pix = QPixmap(self._scene.width(), self._scene.height())
        out_pix.fill(fill_color)
        painter = QPainter(out_pix)
        # painter.setCompositionMode(painter.CompositionMode_Source)
        self._scene.render(painter, QRectF(out_pix.rect()), QRectF(self._scene.sceneRect()),
                           Qt.KeepAspectRatio)
        painter.end()
        return out_pix

    def resizeEvent(self, event: 'QResizeEvent') -> None:
        return super(VectoRaster, self).resizeEvent(event)



