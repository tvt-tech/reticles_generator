from PyQt5.QtWidgets import QLineEdit

from .gv import *


class VectorViewer(VectoRaster):

    def __init__(self, parent=None,
                 size: QSize = QSize(640, 480),
                 clicks: QSizeF = QSizeF(2.01, 2.01)):
        super(VectorViewer, self).__init__(parent, size, clicks)

    def draw_grid(self):
        self.draw_mil_grid(0.1, 0.1, True, False, CustomPen.GridH4)
        self.draw_mil_grid(1, 1, True, True, CustomPen.GridH3, font_size=5)
        self.draw_mil_grid(5, 5, False, False, CustomPen.GridH3, font_size=8)
        self.draw_mil_grid(10, 10, True, False, CustomPen.GridH2)
        self.draw_mil_grid(100, 100, True, False, CustomPen.GridH1)

    def draw_background(self):
        self.setBackgroundBrush(Qt.lightGray)

    def wheelEvent(self, event):
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

    def _release_mouse_button(self, point):
        if not self.temp_item:
            if self.draw_mode == DrawMode.Eraser:
                grab_item = self._scene.itemAt(point, self.transform())
                self.del_item(grab_item)
            elif self.draw_mode == DrawMode.Pencil:
                self._scene.addPoint(point, CustomPen.PencilVect, CustomBrush.Black)
            elif self.draw_mode == DrawMode.Text:
                text = self._text_dlg()
                if text:
                    font = QFont('BankGothic Lt BT')
                    font.setPointSize(8)
                    self._scene.addSimpleText(text, font, point)

    def _erase(self, point, modifiers):
        grab_item = self._scene.itemAt(point, self.transform())
        self.del_item(grab_item)

    def _pencil(self, point, modifiers, pen=CustomPen.PencilVect):
        p1, p2 = self._get_pencil_tool_points(point, modifiers)
        if p1 != p2:
            line = QLineF(p1, p2)
            self.temp_item = self._scene.addLine(line, CustomPen.LineVect)
            self.lastPoint = p2

    def _line(self, point, modifiers):
        p1, p2 = self._get_line_tool_points(point, modifiers)
        line = QLineF(p1, p2)
        if not self.temp_item:
            self.temp_item = self._scene.addLine(line, CustomPen.LineVect)
        else:
            self.temp_item.setLine(line)

    def _rect(self, point, modifiers):
        p1, p2 = self._get_rect_tool_point(point, modifiers)
        rect = QRectF(p1, p2)
        if not self.temp_item:
            self._selector = self._scene.addSelector(rect, (self._click_x, self._click_y, self._multiplier))
            self.temp_item = self._scene.addRect(rect, CustomPen.LineVect)
        else:
            self._selector.setRect(rect)
            self.temp_item.setRect(rect)

    def _ellipse(self, point, modifiers):
        p1, p2 = self._get_ellipse_tool_point(point, modifiers)
        rect = QRectF(p1, p2)
        if not self.temp_item:
            self._selector = self._scene.addSelector(rect, (self._click_x, self._click_y, self._multiplier))
            self.temp_item = self._scene.addEllipse(rect, CustomPen.LineVect)
        else:
            self._selector.setRect(rect)
            self.temp_item.setRect(rect)

    def _ruler(self, point, modifiers):
        p1, p2 = self._get_rect_tool_point(point, modifiers)
        rect = QRectF(p1, p2)

        if not self.temp_item:
            self._selector = self._scene.addSelector(rect, (self._click_x, self._click_y, self._multiplier))
            self.temp_item = self._scene.addRuler(rect, self.ruler_step * self._px_at_mil_h, CustomPen.LineVect)
        else:
            self._selector.setRect(rect)
            self.temp_item.setRect(rect)

    def _numbers(self, point, modifiers):
        p1, p2 = self._get_rect_tool_point(point, modifiers)
        rect = QRectF(p1, p2)

        if not self.temp_item:
            self._selector = self._scene.addSelector(rect, (self._click_x, self._click_y, self._multiplier))
            self.temp_item = self._scene.addNumbers(rect, self.ruler_step * self._px_at_mil_h, CustomPen.LineVect)
        else:
            self._selector.setRect(rect)
            self.temp_item.setRect(rect)

    def _text(self, point, modifiers):
        pass
        # p1, p2 = self._get_rect_tool_point(point, modifiers)
        # rect = QRectF(p1, p2)
        # if not self.temp_item:
        #     self._selector = self._scene.addSelector(rect, (self._click_x, self._click_y, self._multiplier))
        #     self.temp_item = self._scene.addRect(rect, CustomPen.NoPen)
        # else:
        #     self._selector.setRect(rect)
        #     self.temp_item.setRect(rect)

    def _text_dlg(self):
        text, ok = QInputDialog.getText(self, "Enter text", "", QLineEdit.Normal, "")
        if ok:
            return text
        else:
            return

    @hide_grid
    def clear_view(self):
        for item in self._scene.items():
            if item.isVisible() and item.scene() == self._scene:
                self._scene.removeItem(item)

    def draw_sketch(self, sketch=example_grid):
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
            elif layer['t'] == ItemType.Text:
                graphics_item_type = SimpleTextItem
            else:
                continue
            graphics_item = graphics_item_type.fromJson(self._px_at_mil_h, self._px_at_mil_v, **layer)
            self._scene.addItem(graphics_item)

    def undo(self):
        hist_size = len(self._history)
        max_idx = hist_size - 1
        if -1 < self._history_idx <= 20 and self._history_idx <= max_idx:
            self._history_idx -= 1
            if self._history_idx > -1:
                self.clear_view()
                self.draw_sketch(self._history[self._history_idx])

    def redo(self):
        hist_size = len(self._history)
        max_idx = hist_size - 1
        if -1 <= self._history_idx < 20 and self._history_idx < max_idx:
            self._history_idx += 1
            self.clear_view()
            if self._history_idx > -1:
                self.draw_sketch(self._history[self._history_idx])

    def _history_append(self):
        cur_state = self.get_vectors()
        hist_size = len(self._history)
        max_idx = hist_size - 1

        if 0 <= self._history_idx < hist_size:
            if self._history[self._history_idx] == cur_state:
                return

        if self._history_idx <= 0 and hist_size >= 0:
            self._history.append(cur_state)
            self._history_idx += 1

        elif self._history_idx > 0 and self._history_idx <= max_idx:
            self._history.insert(self._history_idx + 1, cur_state)
            self._history_idx += 1
            self._history = self._history[:self._history_idx + 1]

        elif self._history_idx == max_idx and hist_size >= 20:
            self._history.pop(0)
            self._history.append(cur_state)
