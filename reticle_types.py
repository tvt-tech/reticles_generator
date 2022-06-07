import math
from PyQt5.QtCore import Qt, QRect, QPoint, QLine
from PyQt5.QtGui import QPen, QPainter

CROSS_1PX = {'bind': False, 'margin': 0, 'mask': 0b1111, 'pen': 1, 'size': 1, 'zoomed': False}


class Click(object):
    def __init__(self, x, y):
        self.x = round(x, 2)
        self.y = round(y, 2)

    def tuple(self):
        return self.x, self.y


class Kit(object):
    def __init__(self, core_rez_x, core_rez_y, pixel_size, lens_focus, video_rez_x, video_rez_y):
        self.core_rez_x = core_rez_x
        self.core_rez_y = core_rez_y
        self.pixel_size = pixel_size / 1000
        self.lens_focus = lens_focus
        self.video_rez_x = video_rez_x
        self.video_rez_y = video_rez_y

    def click(self):
        atan_x = math.atan((self.core_rez_x / 2) * self.pixel_size / self.lens_focus) * 2
        atan_y = math.atan((self.core_rez_y / 2) * self.pixel_size / self.lens_focus) * 2

        index_x = atan_x / self.video_rez_x
        index_y = atan_y / self.video_rez_y

        x_click_real = math.tan(index_x) * 10000
        y_click_real = math.tan(index_y) * 10000

        x_click = round(x_click_real, 2)
        y_click = round(y_click_real, 2)

        click = Click(x_click, y_click)

        return click

    def fov(self):
        # TODO: =ГРАДУСЫ(2*ATAN(((B1/2)*B3)/B4))
        return


class ReticleItem(object):
    def __init__(self, painter: QPainter, x0, y0, x1, y1, zoom, *args, **kwargs):
        pass


class Cross(object):
    def __init__(self, painter: QPainter, x0, y0, x1, y1,
                 zoom,
                 margin, size, x_offset=0, y_offset=0,
                 pen=1, mask=0b1111, bind=True, zoomed=True, flags=0x11110011, multiplier=1, color=Qt.black,
                 *args, **kwargs):

        # flags = [bool(flags >> i & 1) for i in range(8 - 1, -1, -1)]

        self.flags = int(bind) << 1 | int(zoomed) | mask << 4

        self.painter = painter
        self.margin = margin
        self.size = size
        self.pen = pen
        self.mask = mask
        self.bind = bind
        self.zoom = zoom
        self.zoom = zoom
        self.multiplier = multiplier
        self.x0 = x0 + (x_offset * x1) * zoom
        self.y0 = y0 + (y_offset * y1) * zoom
        self.x1 = x1
        self.y1 = y1
        self.color = color

        self.draw()

    def draw(self):

        left, right, bottom, top, f0, f1, bind, zoomed = [(self.flags >> i & 1) for i in range(8 - 1, -1, -1)]

        if isinstance(self.pen, int):
            penx = QPen(self.color, self.pen, Qt.SolidLine, Qt.SquareCap)
            peny = QPen(self.color, self.pen, Qt.SolidLine, Qt.SquareCap)
            if self.pen > 1:
                penx = QPen(self.color, self.pen / 10 * self.zoom * self.x1, Qt.SolidLine, Qt.FlatCap)
                peny = QPen(self.color, self.pen / 10 * self.zoom * self.y1, Qt.SolidLine, Qt.FlatCap)
        else:
            penx = self.pen
            peny = self.pen

        if bind:
            margin_x = self.margin * self.x1
            margin_y = self.margin * self.y1
            size_x = (self.size + self.margin) * self.x1
            size_y = (self.size + self.margin) * self.y1

            if -1 < margin_x < 1:
                margin_x = 0
            if -1 < margin_y < 1:
                margin_y = 0
        else:
            margin_x, margin_y = self.margin, self.margin
            size_x, size_y = self.size, self.size

        if zoomed:
            zoom = self.zoom
            margin_x, margin_y = margin_x * zoom, margin_y * zoom
            size_x, size_y = size_x * zoom, size_y * zoom

        lines = []
        self.painter.setPen(peny)
        if left:
            lines.append(QLine(self.x0 - margin_x, self.y0, self.x0 - size_x, self.y0))
        if right:
            lines.append(QLine(self.x0 + margin_x, self.y0, self.x0 + size_x, self.y0))
        if lines:
            self.painter.drawLines(*lines)

        lines = []
        self.painter.setPen(penx)
        if bottom:
            lines.append(QLine(self.x0, self.y0 + margin_y, self.x0, self.y0 + size_y))
        if top:
            lines.append(QLine(self.x0, self.y0 - margin_y, self.x0, self.y0 - size_y))
        if lines:
            self.painter.drawLines(*lines)


class Dot(object):
    def __init__(self, painter: QPainter, x0, y0, x1, y1, zoom, x_offset=0, y_offset=0,
                 is_ring=True, pen=3, color=Qt.black, *args, **kwargs):
        self.painter = painter
        self.is_ring = is_ring
        self.pen = pen
        self.x0 = x0 + (x_offset * x1 * zoom)
        self.y0 = y0 + (y_offset * y1 * zoom)
        self.color = color
        self.draw()

    def draw(self):
        point = QPoint(self.x0, self.y0)
        if isinstance(self.pen, int):
            self.painter.setPen(QPen(self.color, self.pen, Qt.SolidLine))
            self.painter.drawPoint(point)
            if 5 >= self.pen > 1:
                self.painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
                self.painter.drawPoint(point)
        else:
            self.painter.setPen(self.pen)
            self.painter.drawPoint(point)


class Text(object):
    def __init__(self, painter: QPainter, x0, y0, x1, y1, zoom, text: str, pen=1,
                 x_offset=0, y_offset=0, color=Qt.black, *args, **kwargs):
        self.x0 = x0 + x_offset * x1 * zoom
        self.y0 = y0 + y_offset * y1 * zoom
        self.x1 = x1
        self.y1 = y1
        self.color = color
        self.painter = painter
        self.text = text

        if isinstance(pen, int):
            self.painter.setPen(QPen(self.color, pen, Qt.SolidLine))
        else:
            self.painter.setPen(pen)

        self.draw()

    def draw(self):
        strlen = 15 * len(self.text)
        p1 = QPoint(self.x0 - strlen, self.y0 - strlen)
        p2 = QPoint(self.x0 + strlen, self.y0 + strlen)
        self.painter.drawText(QRect(p1, p2), Qt.AlignCenter, self.text)


class Line(object):
    def __init__(self, painter: QPainter, x0, y0, x1, y1, zoom, pen,
                 p1: tuple[int, int], p2: tuple[int, int],
                 x_offset=0, y_offset=0, color=Qt.black, zoomed=True, *args, **kwargs):
        self.x0 = x0 + x_offset * x1 * zoom
        self.y0 = y0 + y_offset * y1 * zoom
        self.x1 = x1
        self.y1 = y1
        self.color = color
        self.painter = painter
        self.zoomed = zoomed

        if isinstance(pen, int):
            self.painter.setPen(QPen(self.color, pen, Qt.SolidLine))
        else:
            self.painter.setPen(pen)

        px1, py1 = p1
        px2, py2 = p2

        if zoomed:
            self.p1 = (self.x0 + px1 * x1 * zoom, self.y0 + py1 * y1 * zoom)
            self.p2 = (self.x0 + px2 * x1 * zoom, self.y0 + py2 * y1 * zoom)
        else:
            self.p1 = (self.x0 + px1 * x1, self.y0 + py1 * y1)
            self.p2 = (self.x0 + px2 * x1, self.y0 + py2 * y1)

        self.draw()

    def draw(self):
        self.painter.drawLine(*self.p1, *self.p2)


class Ruler(object):
    def __init__(self, painter, x0, y0, x1, y1,
                 zoom,
                 a, b, step,
                 w, pen=1, mode='grid',
                 x_offset=0, y_offset=0,
                 color=Qt.black, flip_x=False, flip_y=False,
                 *args, **kwargs):
        self.painter = painter
        self.zoom = zoom

        if flip_x:
            a, b, x_offset, y_offset = self.flip_by_x(a, b, x_offset, y_offset)
        if flip_y:
            a, b, x_offset, y_offset = self.flip_by_y(a, b, x_offset, y_offset)

        self.a = a
        self.b = b
        self.x0 = x0 + x_offset * x1 * zoom
        self.y0 = y0 + y_offset * y1 * zoom
        self.w = w
        self.pen = pen
        self.mode = mode
        self.x1 = x1
        self.y1 = y1

        self.step = step
        self.color = color

        self.kwargs = kwargs

        if isinstance(pen, int):
            self.painter.setPen(QPen(self.color, pen, Qt.SolidLine))
        else:
            self.painter.setPen(pen)

        self.draw()

    @staticmethod
    def flip_by_x(a, b, x_offset, y_offset):
        return a, b, x_offset, y_offset

    @staticmethod
    def flip_by_y(a, b, x_offset, y_offset):
        return a, b, x_offset, y_offset

    def draw_dot(self, x, y):
        Dot(self.painter, self.x0 + x, self.y0 + y, self.x1, self.y1, self.zoom, pen=self.pen, color=self.color)

    def draw_cross(self, x, y):
        if 'cross' not in self.kwargs:
            CROSS_1PX['pen'] = self.pen
            self.kwargs['cross'] = CROSS_1PX
        Cross(self.painter, self.x0 + x, self.y0 + y, self.x1, self.y1, self.zoom,
              color=self.color, **self.kwargs['cross'])

    def draw_dash(self, x, y):
        return

    def draw_ruler(self, x, y, string):
        p1 = QPoint(self.x0 + x - 15, self.y0 + y - 15)
        p2 = QPoint(self.x0 + x + 15, self.y0 + y + 15)
        if len(string) > 1:
            cx = self.painter.device().width() / 2
            offset = self.painter.font().pixelSize() / 1.3
            if self.x0 + x < cx:
                p1.setX(p1.x() - offset)
            if self.x0 + x > cx:
                p2.setX(p2.x() + offset)
        self.painter.drawText(QRect(p1, p2), Qt.AlignCenter, string)

    def draw(self):
        pass

    def draw_xy(self, x, y, i):
        if 'exclude_0' in self.kwargs and i == 0:
            pass
        else:
            if self.mode == 'grid':
                return self.draw_dash(x, y)
            elif self.mode == 'dot':
                self.draw_dot(x, y)
            elif self.mode == 'cross':
                self.draw_cross(x, y)
            elif self.mode == 'ruler':
                i = int(i) if i % 1 == 0 else round(i, 1)

                if y == 0:
                    string = f'{i}' if x >= 0 else f'{-i}'
                else:
                    string = f'{i}' if y >= 0 else f'{-i}'
                self.draw_ruler(x, y, string)


class HRuler(Ruler):

    @staticmethod
    def flip_by_x(a, b, x_offset, y_offset):
        return a, b, x_offset, -y_offset

    @staticmethod
    def flip_by_y(a, b, x_offset, y_offset):
        return -b, -a, -x_offset, y_offset

    def draw(self):
        i = self.a
        items = []
        if int(self.x1 * self.step * self.zoom) > 3:
            y = 0
            while i <= self.b:
                x = i * self.x1 * self.zoom
                item = self.draw_xy(x, y, i)
                if item:
                    items.append(item)
                i = round(i + self.step, 2)
        if items and self.mode == 'grid':
            self.painter.drawLines(*items)

    def draw_dash(self, x, y):
        width = int(self.w * self.y1 * self.zoom)
        return QLine(self.x0 + x, self.y0 + width,
                     self.x0 + x, self.y0 - width)


class VRuler(Ruler):

    @staticmethod
    def flip_by_x(a, b, x_offset, y_offset):
        return -b, -a, x_offset, -y_offset

    @staticmethod
    def flip_by_y(a, b, x_offset, y_offset):
        return a, b, -x_offset, y_offset

    def draw(self):
        i = self.a
        x = 0
        items = []
        while i <= self.b:
            y = i * self.y1 * self.zoom
            item = self.draw_xy(x, y, i)
            if item:
                items.append(item)
            i = round(i + self.step, 2)
        if items and self.mode == 'grid':
            self.painter.drawLines(*items)

    def draw_dash(self, x, y):
        width = int(self.w * self.x1 * self.zoom)
        return QLine(self.x0 + width, self.y0 + y,
                     self.x0 - width, self.y0 + y)

TYPES = {
    'cross': Cross,
    'dot': Dot,
    'hruler': HRuler,
    'vruler': VRuler,
    'line': Line,
    'text': Text
}