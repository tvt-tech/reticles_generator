from PyQt5 import QtCore, QtWidgets, QtGui
from ret_edit import CrossEdit, DotEdit, RulerEdit, LineEdit, TextEdit

DEFAULT_CROSS = {"type": "cross", "margin": 0.5, "size": 1, "mask": 15, "bind": True, "zoomed": True,
                 "min_zoom": 1, "max_zoom": 7, "pen": 1}

DEFAULT_DOT = {"type": "dot", "x_offset": 0, "y_offset": 0, "pen": 3, "min_zoom": 1, "max_zoom": 7}

DEFAULT_RULER = {"type": "vruler", "a": -10, "b": 10, "step": 1, "w": 0.3, "x_offset": 0, "y_offset": 0, "mode": "grid",
                 "min_zoom": 1, "max_zoom": 7, "pen": 1, "exclude_0": True}

DEFAULT_LINE = {"type": "line", "min_zoom": 1, "max_zoom": 6, "x_offset": 0, "y_offset": 0, "p1": [0.7, 1.2],
                "p2": [-0.7, 1.2], "pen": 1, "zoomed": False},

DEFAULT_TEXT = {"type": "text", "text": "SAMPLE TEXT", "x_offset": 2, "y_offset": 2, "min_zoom": 4, "max_zoom": 6,
                "pen": 1}


class ItemAdder(QtWidgets.QPushButton):
    def __init__(self, w):
        super(ItemAdder, self).__init__()
        self.w = w
        self.context = QtWidgets.QMenu()
        self.add_cross_action = self.context.addAction('Cross')
        self.add_dot_action = self.context.addAction('Dot')
        self.add_ruler_action = self.context.addAction('Ruler')
        self.add_line_action = self.context.addAction('Line')
        self.add_text_action = self.context.addAction('Text')

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        action = self.context.exec_(self.mapToGlobal(e.pos()))
        if action == self.add_cross_action:
            self.add_cross()
        if action == self.add_dot_action:
            self.add_dot()
        if action == self.add_ruler_action:
            self.add_ruler()
        if action == self.add_line_action:
            self.add_line()
        if action == self.add_text_action:
            self.add_text()
        self.w.reticle = self.w.combo.currentData()
        self.w.load_table()
        self.w.draw_layers()
        return super().mousePressEvent(e)

    def add_cross(self):
        dlg = CrossEdit(DEFAULT_CROSS)
        self.add_item(dlg)

    def add_dot(self):
        dlg = DotEdit(DEFAULT_DOT)
        self.add_item(dlg)

    def add_ruler(self):
        dlg = RulerEdit(DEFAULT_RULER)
        self.add_item(dlg)

    def add_line(self):
        dlg = LineEdit(DEFAULT_LINE)
        self.add_item(dlg)

    def add_text(self):
        dlg = TextEdit(DEFAULT_TEXT)
        self.add_item(dlg)

    def add_item(self, dlg):
        dlg.exec_()
        if dlg.accepted:
            new_item = dlg.get_data()
            combo = self.w.combo
            reticle = combo.currentData()
            reticle['template'].append(new_item)
            combo.setItemData(combo.currentIndex(), reticle)
            combo.setCurrentIndex(combo.currentIndex())
