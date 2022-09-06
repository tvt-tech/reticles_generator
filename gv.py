from enum import IntFlag, auto

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QLine, QPoint, QLineF, QPointF, QRectF
from PyQt5.QtGui import QPen, QPainter, QPixmap, QImage, QFont, QBrush
from PyQt5.QtWidgets import QGraphicsLineItem, QLabel, QGraphicsTextItem, QApplication, QGraphicsPixmapItem, \
    QGraphicsRectItem


class CenterPainter(QPainter):
    def __init__(self, pixmap: QPixmap = None):
        super(CenterPainter, self).__init__(pixmap)

        self.pixmap = pixmap
        self.x0 = int(pixmap.width() / 2) + 1
        self.y0 = int(pixmap.height() / 2) + 1

    def drawPointC(self, point: [QtCore.QPointF, QtCore.QPoint]) -> None:
        point = self.transpose_point(point)
        return super(CenterPainter, self).drawPoint(point)

    def drawLineC(self, line: QtCore.QLineF) -> None:
        line = QLine(self.transpose_point(line.p1()), self.transpose_point(line.p2()))
        return super(CenterPainter, self).drawLine(line)

    def drawLinesC(self, lines: list) -> None:
        lines = list(map(lambda line: QLine(self.transpose_point(line.p1()), self.transpose_point(line.p2())), lines))
        return super(CenterPainter, self).drawLines(lines)

    def transpose_point(self, p: [QtCore.QPointF, QtCore.QPoint]):
        return QPoint(self.x0 + p.x(), self.y0 + p.y())


class DrawbleGraphicScene(QtWidgets.QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super(DrawbleGraphicScene, self).__init__(*args, **kwargs)

        self.x0 = int(self.width() / 2) + 1
        self.y0 = int(self.height() / 2) + 1

    def addLineC(self, line: QtCore.QLineF, pen: QtGui.QPen) -> QGraphicsLineItem:
        line = QtCore.QLineF(self.transpose_point(line.p1()), self.transpose_point(line.p2()))
        return super(DrawbleGraphicScene, self).addLine(line, pen)

    def addTextC(self, text: str, pos: QPoint, font: QtGui.QFont = QFont()) -> QGraphicsTextItem:
        text_item = super(DrawbleGraphicScene, self).addText(text, font)
        text_item.setPos(self.transpose_point(pos))
        return text_item

    def addPointC(self, point: QPoint, pen: QPen = QPen(Qt.white), brush: QBrush = QBrush(Qt.white)) -> QGraphicsRectItem:
        point = self.transpose_point(point)
        rect = QLineF(QPoint(point.x(), point.y()), QPoint(point.x()+1, point.y()+1))
        return super(DrawbleGraphicScene, self).addLine(rect, pen)

    def transpose_point(self, p: [QtCore.QPointF, QtCore.QPoint]):
        return QPoint(self.x0 + p.x(), self.y0 + p.y())

    def drawForeground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super(DrawbleGraphicScene, self).drawForeground(painter, rect)


class DrawModeBtn(QtWidgets.QToolButton):
    def __init__(self, *args, **kwargs):
        super(DrawModeBtn, self).__init__(*args, **kwargs)
        self.setText('Draw')
        self.is_enabled = False
        self.clicked.connect(self.change_mode)

    def change_mode(self):
        self.is_enabled = not self.is_enabled


class DrawMode(IntFlag):
    Notool = auto()
    Pencil = auto()
    Eraser = auto()
    Line = auto()
    Rect = auto()
    Elipse = auto()
    Text = auto()


class MyCanvasItem(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        super(MyCanvasItem, self).__init__(parent)

    def paint(self, painter, option, widget=None):
        super(MyCanvasItem, self).paint(painter, option, widget)
        # line_h = QLineF(-self.x1 * 5, 0, self.x1 * 5, 0)
        # line_v = QLineF(0, -self.y1 * 5, 0, self.y1 * 5)
        # painter.drawLines([line_h, line_v])


class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        # self._empty = True

        self.click_x = 2.01
        self.click_y = 2.01

        self.click_x = 3.01
        self.click_y = 3.01

        self.multiplier = 10

        self.x1 = 1
        self.y1 = 1

        self.set_reticle_scale()

        self.w = int(640 / self.x1)
        self.h = int(480 / self.y1)

        self.w = 640
        self.h = 480

        print(self.w, self.h)

        self.x0 = int(self.w / 2) + 1
        self.y0 = int(self.h / 2) + 1

        self.setFixedSize(self.w, self.h)

        # self._scene = QtWidgets.QGraphicsScene(self)
        # self._photo = QtWidgets.QGraphicsPixmapItem()
        # self._scene.addItem(self._photo)

        self.setCursor(Qt.CrossCursor)

        self.draw_mode = DrawMode.Notool
        self.drawing = False
        self.temp_item = None
        self.mp = False

        self._scene = DrawbleGraphicScene(0, 0, self.w, self.h)

        # self.window().setFixedSize(self.w, self.h)
        # self.scene_rect = QRect(0, 0, 640, 480)
        # self._scene.setSceneRect(0, 0, 640, 480)

        self._pmap = QtWidgets.QGraphicsPixmapItem()

        self._pix = QPixmap(640, 480)

        self._pix.fill(Qt.transparent)

        # self._img = QImage(640, 480, QImage.Format_RGB32)

        # self._scene.addPixmap(QPixmap.fromImage(self._img))

        self._scene.addItem(self._pmap)

        # self.canvas_pixmap = self._scene.addPixmap(self._pix)
        self.canvas_pixmap = MyCanvasItem()
        # self.canvas_pixmap = QGraphicsPixmapItem()
        # self.canvas_pixmap.setPixmap(self._pix)
        self._scene.addItem(self.canvas_pixmap)

        self.painter = CenterPainter(self.canvas_pixmap.pixmap())
        line_h = QLineF(-self.x1 * 5, 0, self.x1 * 5, 0)
        line_v = QLineF(0, -self.y1 * 5, 0, self.y1 * 5)

        self._scene.addLineC(line_v, QPen())
        self._scene.addLineC(line_h, QPen())
        self._scene.addPointC(QPoint(0, 0), QPen(Qt.white, 1, Qt.SolidLine, Qt.FlatCap, Qt.MiterJoin))

        self.painter.drawLinesC([line_h, line_v])
        # self.canvas_pixmap.paint(self.painter, QStyleOptionGraphicsItem(), self)
        self.painter.setPen(QPen(Qt.white))
        self.painter.drawPointC(QPoint(0, 0))

        self.draw_reticle_grid(10, True, True, QPen(Qt.darkMagenta, 0.2, Qt.SolidLine, Qt.FlatCap, Qt.MiterJoin))
        self.draw_reticle_grid(2, True, False, QPen(Qt.magenta, 0.1, Qt.SolidLine, Qt.FlatCap, Qt.MiterJoin))

        self.setScene(self._scene)

        # self.canvas_pixmap.paint(self.painter)

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
        # self.setBackgroundBrush(QtGui.QBrush(Qt.gray))

        self.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.setMouseTracking(True)

        # self.set_reticle_scale()
        # self.draw_reticle_grid()

        self.toggleDragMode()
        # self.fitInView()

    def set_reticle_scale(self):
        self.x1 = self.multiplier / self.click_x
        self.y1 = self.multiplier / self.click_y

    def draw_reticle_grid(self, step=10, grid=False, mark=False, pen: QPen = QPen()):
        # pen01 = QPen(Qt.magenta, 0.1, Qt.SolidLine, Qt.FlatCap, Qt.MiterJoin)

        grid_scale_h = int(self.x1 * step)
        grid_scale_v = int(self.y1 * step)
        grid_scale_h_f = self.x1 * step
        grid_scale_v_f = self.y1 * step

        # line = QGraphicsLineItem(self.x0+0.5, 0, self.x0+0.5, self.h)
        # line.setPen(QPen(Qt.white, 0.2, Qt.SolidLine, Qt.FlatCap, Qt.MiterJoin))
        # self._scene.addItem(line)
        #
        # line = QGraphicsLineItem(0, self.y0, self.w, self.y0)
        # line.setPen(QPen(Qt.white, 0.2, Qt.SolidLine, Qt.FlatCap, Qt.MiterJoin))
        # self._scene.addItem(line)

        for i, x in enumerate(range(0, self.x0, grid_scale_h)):
            x_f = i * grid_scale_h_f
            if grid:
                line = QLineF(x_f + 1, self.y0, x_f + 1, -self.y0)
                self._scene.addLineC(line, pen)
            if mark:
                text = self._scene.addTextC(str(i * 10), QPoint(x_f, 0))
                text.setDefaultTextColor(pen.color())

        for i, x in enumerate(range(0, self.x0, grid_scale_h)):
            x_f = -i * grid_scale_h_f
            if grid:
                line = QLineF(x_f, self.y0, x_f, -self.y0)
                self._scene.addLineC(line, pen)
            if mark:
                text = self._scene.addTextC(str(i * 10), QPoint(x_f, 0))
                text.setDefaultTextColor(pen.color())

        for i, y in enumerate(range(0, self.y0, grid_scale_v)):
            y_f = i * grid_scale_v_f
            if grid:
                line = QLine(self.x0, y_f + 1, -self.x0, y_f + 1)
                self._scene.addLineC(line, pen)
            if mark:
                text = self._scene.addTextC(str(i * 10), QPoint(0, y_f))
                text.setDefaultTextColor(pen.color())

        for i, y in enumerate(range(0, self.y0, grid_scale_v)):
            y_f = -i * grid_scale_v_f
            if grid:
                line = QLine(self.x0, y_f, -self.x0, y_f)
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

        print(self._zoom)

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
                # painter = QPainter(self.canvas_pixmap.pixmap())
                self.painter.setPen(QPen(Qt.black))
                if modifiers == Qt.ShiftModifier:
                    if abs(self.lastPoint.x() - point.x()) < abs(self.lastPoint.y() - point.y()):
                        point.setX(self.lastPoint.x())
                    else:
                        point.setY(self.lastPoint.y())
                self.painter.drawLine(QLine(self.lastPoint, point))

            if self.draw_mode == DrawMode.Line:

                if not self.temp_item:
                    line = QLineF(self.lastPoint, point)
                    self.temp_item = self._scene.addLine(line, QPen())
                else:
                    if modifiers == Qt.ShiftModifier:
                        if abs(self.temp_item.line().p1().x() - point.x()) < abs(
                                self.temp_item.line().p1().y() - point.y()):
                            point.setX(self.temp_item.line().p1().x())
                        else:
                            point.setY(self.temp_item.line().p1().y())
                    line = QLineF(self.temp_item.line().p1(), point)
                    self.temp_item.setLine(line)

        self.lastPoint = point
        self.update()
        super(PhotoViewer, self).mouseMoveEvent(event)

    # method for mouse left button release
    def mouseReleaseEvent(self, event):
        point = self.mapToScene(event.pos()).toPoint()
        if event.button() == Qt.LeftButton:
            if self.draw_mode == DrawMode.Pencil:
                # painter = QPainter(self.canvas_pixmap.pixmap())
                self.painter.drawPoint(QPoint(self.lastPoint))
        self.lastPoint = point

        # make drawing flag false
        self.drawing = False
        if self.temp_item:
            if self.draw_mode == DrawMode.Line:
                # painter = QPainter(self.canvas_pixmap.pixmap())
                self.painter.drawLines(self.temp_item.line())
            self._scene.removeItem(self.temp_item)
            self.temp_item = None

        self.update()
        super(PhotoViewer, self).mouseReleaseEvent(event)


class QPixMap:
    pass


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
        HBlayout.addWidget(self.clear_btn)
        VBlayout.addLayout(HBlayout)

        self.installEventFilter(self.viewer._scene)

    def eventFilter(self, a0: 'QObject', a1: 'QEvent') -> bool:
        if a0 == self.viewer._scene:
            print('event')
        super(Window, self).eventFilter(a0, a1)

    def on_draw_btn_press(self):
        self.viewer.draw_mode = DrawMode.Pencil
        self.viewer.toggleDragMode()

    def on_line_btn_press(self):
        self.viewer.draw_mode = DrawMode.Line
        self.viewer.toggleDragMode()

    def on_notool_btn_press(self):
        self.viewer.draw_mode = DrawMode.Notool
        self.viewer.toggleDragMode()

    def on_clear_btn_press(self):
        self.viewer.canvas_pixmap.pixmap().fill(Qt.transparent)

        # self.viewer._scene.addPixmap(self.viewer._pix)

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
