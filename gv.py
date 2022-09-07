from enum import IntFlag, auto
from functools import wraps

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QLine, QPoint, QLineF, QPointF, QRectF
from PyQt5.QtGui import QPen, QPainter, QPixmap, QImage, QFont, QBrush, QPolygonF
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtWidgets import QGraphicsLineItem, QLabel, QGraphicsTextItem, QApplication, QGraphicsPixmapItem, \
    QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsPolygonItem

milatcm = 10
mingridstep_h = 4
mingridstep_v = 2

# click = 4.25


example = [
    {
        't': 'line',
        'mode': 'pt',
        'p1': [2, 0],
        'p2': [4, 0],
        'pen': 1,
    },
    {
        't': 'line',
        'mode': 'pt',
        'p1': [-2, 0],
        'p2': [-4, 0],
        'pen': 1,
    },
    {
        't': 'line',
        'mode': 'pt',
        'p1': [0, 3],
        'p2': [0, 5],
        'pen': 1,
    },
    {
        't': 'line',
        'mode': 'pt',
        'p1': [0, -3],
        'p2': [0, -5],
        'pen': 1,
    },
    {
        't': 'rect',
        'mode': 'pt',
        'p1': [-1, -2],
        'p2': [1, 2],
        'pen': 1,
    },
    {
        't': 'ellipse',
        'mode': 'pt',
        'p1': [-5, -5],
        'p2': [5, 5],
        'pen': 1,
    },
    {
        't': 'circle',
        'mode': 'pt',
        'p': [0, 0],
        'r': 10,
        'pen': 1,
    },
    {
        't': 'polygon',
        'mode': 'pt',
        'points': [[-5, 0], [0, -5], [5, 0], [0, 5]],
        'pen': 1,
    }
]


def hide_grid(func: callable):
    @wraps(func)
    def _impl(self, *method_args, **method_kwargs):
        children = self.viewer._scene.items()
        for ch in children:
            if hasattr(ch, 'pen'):
                if ch.pen().color() == Qt.darkMagenta or ch.pen().color() == Qt.magenta:
                    ch.setVisible(False)

            if hasattr(ch, 'defaultTextColor'):
                if ch.defaultTextColor() == Qt.darkMagenta or ch.defaultTextColor() == Qt.magenta:
                    ch.setVisible(False)

        ret = func(self, *method_args, **method_kwargs)
        for ch in children:
            ch.setVisible(True)
        return ret

    return _impl


def minmilstep(click, mingridstep):
    pixatclick = milatcm / click
    minmilstep = mingridstep / pixatclick
    return minmilstep


def roundmilstep(milstep):
    rlist = [0.1, 0.2, 0.25, 0.3, 0.5, 1]
    if milstep > max(rlist):
        return roundmilstep(milstep / 10) * 10
    elif milstep < min(rlist):
        return roundmilstep(milstep * 10) / 10
    for v in rlist:
        if v >= milstep:
            return v
    return None


# for i in range(1, 7):
#     cl = click / i
#     mm = minmilstep(cl)
#     rm = roundmilstep(mm)
#
#     print(cl, rm)


class CenterPainter(QPainter):
    def __init__(self, pixmap: QPixmap = None):
        super(CenterPainter, self).__init__(pixmap)

        self.pixmap = pixmap
        self.x0 = int(pixmap.width() / 2) + 1
        self.y0 = int(pixmap.height() / 2) + 1

    def drawPointC(self, point: [QtCore.QPointF, QtCore.QPoint]) -> None:
        point = self._transpose_point(point)
        return super(CenterPainter, self).drawPoint(point)

    def drawLineC(self, line: QtCore.QLineF) -> None:
        line = QLine(self._transpose_point(line.p1()), self._transpose_point(line.p2()))
        return super(CenterPainter, self).drawLine(line)

    def drawLinesC(self, lines: list) -> None:
        lines = list(map(lambda line: QLine(self._transpose_point(line.p1()), self._transpose_point(line.p2())), lines))
        return super(CenterPainter, self).drawLines(lines)

    def _transpose_point(self, p: [QtCore.QPointF, QtCore.QPoint]):
        return QPoint(self.x0 + p.x(), self.y0 + p.y())


class DrawbleGraphicScene(QtWidgets.QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super(DrawbleGraphicScene, self).__init__(*args, **kwargs)

        self.x0 = int(self.width() / 2) + 1
        self.y0 = int(self.height() / 2) + 1

    def addLineC(self, line: QtCore.QLineF, pen: QtGui.QPen) -> QGraphicsLineItem:
        line = QtCore.QLineF(self._transpose_point(line.p1()), self._transpose_point(line.p2()))
        return super(DrawbleGraphicScene, self).addLine(line, pen)

    def addTextC(self, text: str, pos: QPoint, font: QtGui.QFont = QFont()) -> QGraphicsTextItem:
        text_item = super(DrawbleGraphicScene, self).addText(text, font)
        text_item.setPos(self._transpose_point(pos))
        return text_item

    def addRectC(self, rect: QtCore.QRectF, pen: QtGui.QPen, brush: QtGui.QBrush = Qt.transparent) -> QGraphicsRectItem:
        p1 = QPointF(self._transpose_point(QPointF(rect.x(), rect.y())))
        p2 = QPointF(self._transpose_point(QPointF(rect.width(), rect.height())))
        rect = QRectF(p1, p2)
        super(DrawbleGraphicScene, self).addRect(rect, pen, brush)

    def addEllipseC(self, rect: QtCore.QRectF, pen: QtGui.QPen,
                    brush: QtGui.QBrush = Qt.transparent) -> QGraphicsEllipseItem:
        p1 = QPointF(self._transpose_point(QPointF(rect.x(), rect.y())))
        p2 = QPointF(self._transpose_point(QPointF(rect.width(), rect.height())))
        rect = QRectF(p1, p2)
        super(DrawbleGraphicScene, self).addEllipse(rect, pen, brush)

    def addPolygonC(self, polygon: QtGui.QPolygonF, pen: QPen,
                    brush: QtGui.QBrush = Qt.transparent) -> QGraphicsPolygonItem:
        points = [self._transpose_point(point) for point in polygon]
        polygon = QPolygonF(points)
        super(DrawbleGraphicScene, self).addPolygon(polygon, pen, brush)

    def addPoint(self, point: QPointF, pen: QPen = QPen(Qt.black),
                 brush: QBrush = QBrush(Qt.white)) -> QGraphicsRectItem:
        rect = QRectF(QPointF(point.x() - 0.5, point.y() - 0.5), QPointF(point.x() + 0.5, point.y() + 0.5))
        return super(DrawbleGraphicScene, self).addRect(rect, pen, brush)

    def addPointC(self, point: QPointF, pen: QPen = QPen(Qt.black),
                  brush: QBrush = QBrush(Qt.white)) -> QGraphicsRectItem:
        point = self._transpose_point(point)
        rect = QRectF(QPointF(point.x() - 0.5, point.y() - 0.5), QPointF(point.x() + 0.5, point.y() + 0.5))
        return super(DrawbleGraphicScene, self).addRect(rect, pen, brush)

    def _transpose_point(self, p: [QtCore.QPointF, QtCore.QPoint]):
        return QPointF(self.x0 + p.x(), self.y0 + p.y())

    def drawForeground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super(DrawbleGraphicScene, self).drawForeground(painter, rect)


class CustomPen:
    GridH1 = QPen(Qt.darkMagenta, 0.2, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    GridH2 = QPen(Qt.darkMagenta, 0.1, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    GridH3 = QPen(Qt.magenta, 0.05, Qt.SolidLine, Qt.FlatCap, Qt.BevelJoin)
    Pencil = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)
    Line = QPen(Qt.black, 1, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
    Ellipse = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin)


class DrawModeBtn(QtWidgets.QToolButton):
    def __init__(self, *args, **kwargs):
        super(DrawModeBtn, self).__init__(*args, **kwargs)
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


class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0

        self.setRenderHint(QPainter.Antialiasing)

        self.click_x = 2.01
        self.click_y = 2.01

        self.multiplier = 10

        self.x1 = 1
        self.y1 = 1

        mmsx = minmilstep(self.click_x, mingridstep_h)
        mmsy = minmilstep(self.click_y, mingridstep_v)
        mmrx = roundmilstep(mmsx)
        mmry = roundmilstep(mmsy)

        self.xs = mmrx * self.x1
        self.ys = mmry * self.y1

        self.set_reticle_scale()

        self.w = int(640 / self.x1)
        self.h = int(480 / self.y1)

        self.w = 640
        self.h = 480

        self.x0 = int(self.w / 2)
        self.y0 = int(self.h / 2)

        self.setFixedSize(self.w, self.h)

        self.setCursor(Qt.CrossCursor)

        self.draw_mode = DrawMode.Notool
        self.drawing = False
        self.temp_item = None
        self.mp = False

        self._scene = DrawbleGraphicScene(0, 0, self.w, self.h)

        self._pmap = QtWidgets.QGraphicsPixmapItem()

        self._scene.addItem(self._pmap)

        self.draw_reticle_grid(10, 10, True, True, CustomPen.GridH3)
        self.draw_reticle_grid(self.xs, self.ys, True, False, CustomPen.GridH2)
        self.draw_reticle_grid(100, 100, True, False, CustomPen.GridH1)

        self.setScene(self._scene)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        background_texture = QImage(2, 2, QImage.Format_RGB32)
        background_texture.fill(Qt.white)
        background_texture.setPixelColor(0, 1, Qt.lightGray)
        background_texture.setPixelColor(1, 0, Qt.lightGray)
        background_brush = QtGui.QBrush()
        background_brush.setTexture(QPixmap.fromImage(background_texture))

        self.setBackgroundBrush(background_brush)

        self.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.setMouseTracking(True)

        self.toggleDragMode()
        # self.fitInView()

        self.draw_test_reticle()

    def draw_test_reticle(self):

        for item in example:
            if item['t'] == 'line':

                if item['mode'] == 'pt':
                    p1 = (int(self.x1 * item['p1'][0]), int(self.y1 * item['p1'][1]))
                    p2 = (int(self.x1 * item['p2'][0]), int(self.y1 * item['p2'][1]))

                else:
                    p1 = item['p1']
                    p2 = item['p2']

                line = QLineF(*p1, *p2)
                pen = CustomPen.Line
                pen.setWidth(item['pen'])
                self._scene.addLineC(line, pen)

            if item['t'] == 'rect':
                if item['mode'] == 'pt':
                    p1 = (int(self.x1 * item['p1'][0]), int(self.y1 * item['p1'][1]))
                    p2 = (int(self.x1 * item['p2'][0]), int(self.y1 * item['p2'][1]))

                else:
                    p1 = item['p1']
                    p2 = item['p2']

                rect = QRectF(*p1, *p2)
                pen = CustomPen.Line
                pen.setWidth(item['pen'])
                self._scene.addRectC(rect, pen)

            if item['t'] == 'ellipse':
                if item['mode'] == 'pt':
                    p1 = (int(self.x1 * item['p1'][0]), int(self.y1 * item['p1'][1]))
                    p2 = (int(self.x1 * item['p2'][0]), int(self.y1 * item['p2'][1]))

                else:
                    p1 = item['p1']
                    p2 = item['p2']

                rect = QRectF(*p1, *p2)
                pen = CustomPen.Line
                pen.setWidth(item['pen'])
                self._scene.addEllipseC(rect, pen)

            if item['t'] == 'circle':
                if item['mode'] == 'pt':
                    p1 = (
                        int(self.x1 * (item['p'][0] - item['r'])),
                        int(self.y1 * (item['p'][1] - item['r']))
                    )
                    p2 = (
                        int(self.x1 * (item['p'][0] + item['r'])),
                        int(self.y1 * (item['p'][1] + item['r']))
                    )

                else:
                    p1 = (int(item['p'][0] - item['r']), int(item['p'][1] - item['r']))
                    p2 = (int(item['p'][0] + item['r']), int(item['p'][1] + item['r']))

                rect = QRectF(*p1, *p2)
                pen = CustomPen.Line
                pen.setWidth(item['pen'])
                self._scene.addEllipseC(rect, pen)

            if item['t'] == 'polygon':
                if item['mode'] == 'pt':
                    points = [QPointF(int(self.x1 * x), int(self.y1 * y)) for x, y in item['points']]
                else:
                    points = [QPointF(x, y) for x, y in item['points']]
                polygon = QtGui.QPolygonF(points)

                pen = CustomPen.Line
                pen.setWidth(item['pen'])
                self._scene.addPolygonC(polygon, pen)

    def set_reticle_scale(self):
        self.x1 = self.multiplier / self.click_x
        self.y1 = self.multiplier / self.click_y

    def draw_reticle_grid(self, step_h=10, step_v=10, grid=False, mark=False, pen: QPen = QPen()):
        grid_scale_h = int(self.x1 * step_h)
        grid_scale_v = int(self.y1 * step_v)
        grid_scale_h_f = self.x1 * step_h
        grid_scale_v_f = self.y1 * step_v

        for i, x in enumerate(range(0, self.x0, grid_scale_h)):
            x_f = int(i * grid_scale_h_f)
            if grid:
                line = QLineF(x_f, self.y0, x_f, -self.y0)
                self._scene.addLineC(line, pen)
            if mark:
                text = self._scene.addTextC(str(i * 10), QPoint(x_f, 0))
                text.setDefaultTextColor(pen.color())

        for i, x in enumerate(range(0, self.x0, grid_scale_h)):
            x_f = int(-i * grid_scale_h_f)
            if grid:
                line = QLineF(x_f, self.y0, x_f, -self.y0)
                self._scene.addLineC(line, pen)
            if mark:
                text = self._scene.addTextC(str(i * 10), QPoint(x_f, 0))
                text.setDefaultTextColor(pen.color())

        for i, y in enumerate(range(0, self.y0, grid_scale_v)):
            y_f = int(i * grid_scale_v_f)
            if grid:
                line = QLineF(self.x0, y_f, -self.x0, y_f)
                self._scene.addLineC(line, pen)
            if mark:
                text = self._scene.addTextC(str(i * 10), QPoint(0, y_f))
                text.setDefaultTextColor(pen.color())

        for i, y in enumerate(range(1, self.y0, grid_scale_v)):
            y_f = int(-i * grid_scale_v_f)
            if grid:
                line = QLineF(self.x0, y_f, -self.x0, y_f)
                self._scene.addLineC(line, pen)
            if mark:
                text = self._scene.addTextC(str(i * 10), QPoint(0, y_f))
                text.setDefaultTextColor(pen.color())

    def fitInView(self, scale=True):
        rect = self.sceneRect()
        unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
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
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._pmap.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._pmap.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            # factor = 1.25
            # factor = 1.6
            factor = 2
            self._zoom += 1
        else:
            # factor = 0.8
            # factor = 0.625
            factor = 0.5
            self._zoom -= 1
        if 6 >= self._zoom > 0:
            self.scale(factor, factor)
        elif self._zoom > 6:
            self._zoom = 6
        elif self._zoom == 0:
            self.fitInView()
        else:
            self._zoom = 0

        # print(self._zoom)

    def toggleDragMode(self):
        if self.draw_mode != DrawMode.Notool:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        else:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        # if True:
        #     self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())

        if event.button() == Qt.LeftButton:
            # make drawing flag true
            self.drawing = True
            # make last point to the point of cursor
            self.lastPoint = self.mapToScene(event.pos()).toPoint()

        super(PhotoViewer, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        point = self.mapToScene(event.pos()).toPoint()
        modifiers = QApplication.keyboardModifiers()
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            if self.draw_mode == DrawMode.Pencil:

                p1 = QPointF(self.lastPoint.x(), self.lastPoint.y())
                p2 = QPointF(point.x(), point.y())

                if modifiers == Qt.ShiftModifier:
                    if abs(p1.x() - p2.x()) < abs(p1.y() - p2.y()):
                        p2.setX(self.lastPoint.x())
                    else:
                        p2.setY(self.lastPoint.y())
                self._scene.addLine(QLineF(p1, p2), CustomPen.Pencil)

                self.lastPoint = point

            if self.draw_mode == DrawMode.Line:

                if not self.temp_item:
                    p1 = QPointF(self.lastPoint)
                    p2 = QPointF(point)
                    line = QLineF(p1, p2)
                    self.temp_item = self._scene.addLine(line, CustomPen.Line)
                else:
                    p1 = QPointF(self.lastPoint)
                    p2 = QPointF(point)
                    if modifiers == Qt.ShiftModifier:
                        if abs(p1.x() - p2.x()) < abs(p1.y() - p2.y()):
                            p2.setX(p1.x())
                        else:
                            p2.setY(p1.y())
                    line = QLineF(p1, p2)
                    self.temp_item.setLine(line)

                # self.lastPoint = point

            if self.draw_mode == DrawMode.Rect:

                p1 = QPointF(self.lastPoint)
                p2 = QPointF(point)
                rect = QRectF(p1, p2)

                if not self.temp_item:
                    self.temp_item = self._scene.addRect(rect, CustomPen.Line)
                else:
                    self.temp_item.setRect(rect)

            if self.draw_mode == DrawMode.Ellipse:
                delta_x = abs(self.lastPoint.x() - point.x())
                delta_y = abs(self.lastPoint.y() - point.y())

                if modifiers == Qt.ShiftModifier:
                    p1 = QPointF(self.lastPoint.x() - delta_x, self.lastPoint.y() - delta_x)
                    p2 = QPointF(self.lastPoint.x() + delta_x, self.lastPoint.y() + delta_x)
                else:
                    p1 = QPointF(self.lastPoint.x() - delta_x, self.lastPoint.y() - delta_y)
                    p2 = QPointF(self.lastPoint.x() + delta_x, self.lastPoint.y() + delta_y)

                rect = QRectF(p1, p2)

                if not self.temp_item:
                    self.temp_item = self._scene.addEllipse(rect, CustomPen.Ellipse)
                else:
                    self.temp_item.setRect(rect)

        # self.lastPoint = point
        self.update()
        super(PhotoViewer, self).mouseMoveEvent(event)

    # method for mouse left button release
    def mouseReleaseEvent(self, event):
        point = self.mapToScene(event.pos()).toPoint()
        if event.button() == Qt.LeftButton:
            if self.draw_mode == DrawMode.Pencil:
                p1 = QPointF(self.lastPoint.x(), self.lastPoint.y())
                self._scene.addPoint(p1, QPen(Qt.black, 0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin), QBrush(Qt.black))
        self.lastPoint = point

        # make drawing flag false
        self.drawing = False
        if self.temp_item:
            self.temp_item = None

        self.update()
        super(PhotoViewer, self).mouseReleaseEvent(event)


class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.setFixedSize(640, 600)
        self.viewer = PhotoViewer(self)
        # 'Load image' button
        self.btnLoad = QtWidgets.QToolButton(self)
        self.btnLoad.setText('Load image')
        self.btnLoad.clicked.connect(self.loadImage)
        # Button to change from drag/pan to getting pixel info
        self.btnPixInfo = QtWidgets.QToolButton(self)
        self.btnPixInfo.setText('Enter pixel info mode')
        self.btnPixInfo.clicked.connect(self.pixInfo)
        self.editPixInfo = QtWidgets.QLineEdit(self)
        self.editPixInfo.setReadOnly(True)
        self.viewer.photoClicked.connect(self.photoClicked)

        self.no_tool_btn = DrawModeBtn(self)
        self.no_tool_btn.setText('NoTool')
        self.no_tool_btn.clicked.connect(self.on_notool_btn_press)

        self.draw_btn = DrawModeBtn(self)
        self.draw_btn.setText('Pencil')
        self.draw_btn.clicked.connect(self.on_draw_btn_press)

        self.line_btn = DrawModeBtn(self)
        self.line_btn.setText('Line')
        self.line_btn.clicked.connect(self.on_line_btn_press)

        self.clear_btn = QtWidgets.QToolButton(self)
        self.clear_btn.setText('Clear')
        self.clear_btn.clicked.connect(self.on_clear_btn_press)

        self.to_svg_btn = QtWidgets.QToolButton(self)
        self.to_svg_btn.setText('To SVG')
        self.to_svg_btn.clicked.connect(self.on_to_svg_btn_press)

        self.raster_btn = QtWidgets.QToolButton(self)
        self.raster_btn.setText('To BMP')
        self.raster_btn.clicked.connect(self.on_raster_btn_press)

        self.rect_btn = DrawModeBtn()
        self.rect_btn.setText('Rect')
        self.rect_btn.clicked.connect(self.on_rect_btn_press)

        self.ellipse_btn = DrawModeBtn()
        self.ellipse_btn.setText('Ellipse')
        self.ellipse_btn.clicked.connect(self.on_ellipse_btn_press)

        self.lab = QLabel()
        self.labpix = QPixmap(640, 480)
        self.labpix.fill(Qt.transparent)

        self.lab.setPixmap(self.labpix)

        self.drawing = False
        # make last point to the point of cursor
        self.lastPoint = QPoint()

        # Arrange layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.setContentsMargins(0, 0, 0, 0)
        VBlayout.addWidget(self.viewer)
        # VBlayout.addWidget(self.lab, 0, 0)

        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.setAlignment(QtCore.Qt.AlignLeft)
        HBlayout.addWidget(self.btnLoad)
        HBlayout.addWidget(self.btnPixInfo)
        HBlayout.addWidget(self.editPixInfo)
        HBlayout.addWidget(self.no_tool_btn)
        HBlayout.addWidget(self.draw_btn)
        HBlayout.addWidget(self.line_btn)
        HBlayout.addWidget(self.rect_btn)
        HBlayout.addWidget(self.ellipse_btn)
        HBlayout.addWidget(self.clear_btn)
        HBlayout.addWidget(self.to_svg_btn)
        HBlayout.addWidget(self.raster_btn)
        VBlayout.addLayout(HBlayout)

        self.installEventFilter(self.viewer._scene)

    def on_draw_btn_press(self):

        self.viewer.draw_mode = DrawMode.Pencil
        self.viewer.toggleDragMode()

    def on_line_btn_press(self):

        self.viewer.draw_mode = DrawMode.Line
        self.viewer.toggleDragMode()

    def on_notool_btn_press(self):
        self.viewer.draw_mode = DrawMode.Notool
        self.viewer.toggleDragMode()

        buttons = self.findChildren(DrawModeBtn)
        for b in buttons:
            b.reset()

    def on_rect_btn_press(self):

        self.viewer.draw_mode = DrawMode.Rect
        self.viewer.toggleDragMode()

    def on_ellipse_btn_press(self):

        self.viewer.draw_mode = DrawMode.Ellipse
        self.viewer.toggleDragMode()

    def on_clear_btn_press(self):
        # self.viewer.remove_drawed()
        pass

    # @hide_grid
    def on_to_svg_btn_press(self, *args, **kwargs):
        svg_gen = QSvgGenerator()
        svg_gen.setFileName('test_scene.svg')
        svg_gen.setSize(QtCore.QSize(640, 480))
        svg_gen.setViewBox(QRectF(0, 0, 640, 480))
        svg_gen.setTitle("SVG Generator Example Drawing")
        svg_gen.setDescription("An SVG drawing created by the SVG Generator "
                               "Example provided with Qt.")

        painter = QPainter(svg_gen)
        self.viewer._scene.render(painter)
        painter.end()

    @hide_grid
    def on_raster_btn_press(self, *args, **kwargs):
        out_pix = QPixmap(640, 480)
        painter = QPainter(out_pix)
        # painter.setRenderHint(QPainter.Antialiasing)
        out_pix.fill(Qt.white)

        self.viewer._scene.render(painter, QRectF(out_pix.rect()), QRectF(0, 0, 640, 480), Qt.KeepAspectRatio)
        painter.end()
        out_pix.save('test_scene.bmp', 'BMP')

    def loadImage(self):
        self.viewer.setPhoto(QtGui.QPixmap('1_3 MIL-R.bmp'))

    def pixInfo(self):
        self.viewer.toggleDragMode()

    def photoClicked(self, pos):
        if self.viewer.dragMode() == QtWidgets.QGraphicsView.NoDrag:
            self.editPixInfo.setText('%d, %d' % (pos.x(), pos.y()))

    # def mousePressEvent(self, event):
    #
    #     # if left mouse button is pressed
    #     if event.button() == Qt.LeftButton:
    #         # make drawing flag true
    #         self.drawing = True
    #         # make last point to the point of cursor
    #         self.lastPoint = event.pos()
    #
    # # method for tracking mouse activity
    # def mouseMoveEvent(self, event):
    #
    #     # checking if left button is pressed and drawing flag is true
    #     if (event.buttons() & Qt.LeftButton) & self.drawing:
    #         # creating painter object
    #         painter = QPainter(self.viewer._pix)
    #
    #         # set the pen of the painter
    #         painter.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    #
    #         # draw line from the last point of cursor to the current point
    #         # this will draw only one step
    #         painter.drawLine(self.lastPoint, event.pos())
    #
    #         # change the last point
    #         self.lastPoint = event.pos()
    #         # update
    #         self.update()
    #
    # # method for mouse left button release
    # def mouseReleaseEvent(self, event):
    #
    #     if event.button() == Qt.LeftButton:
    #         # make drawing flag false
    #         self.drawing = False


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(500, 300, 800, 600)
    window.show()
    sys.exit(app.exec_())
