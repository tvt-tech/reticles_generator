from PyQt5 import QtCore, QtWidgets, QtGui
from ret_edit import CrossEdit, DotEdit, RulerEdit

DEFAULT_CROSS = {"type": "cross", "margin": 0.5, "size": 1, "mask": 15, "bind": True, "zoom": True,
                 "min_zoom": 1, "max_zoom": 7, "pen": 1}

DEFAULT_DOT = {"type": "dot", "x_offset": 0, "y_offset": 0, "pen": 3, "min_zoom": 1, "max_zoom": 7}


class ItemAdder(QtWidgets.QPushButton):
    def __init__(self, w):
        super(ItemAdder, self).__init__()
        self.w = w
        self.context = QtWidgets.QMenu()
        self.add_cross_action = self.context.addAction('Cross')
        self.add_dot_action = self.context.addAction('Dot')
        self.add_ruler_action = self.context.addAction('Ruler')

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        action = self.context.exec_(self.mapToGlobal(e.pos()))
        if action == self.add_cross_action:
            self.add_cross()
        if action == self.add_dot_action:
            self.add_dot()
        self.w.reticle = self.w.combo.currentData()
        self.w.load_table()
        self.w.draw_layers()
        return super().mousePressEvent(e)

    def add_cross(self):
        dlg = CrossEdit(DEFAULT_CROSS)
        dlg.exec_()
        if dlg.accepted:
            new_cross = dlg.get_data()
            combo = self.w.combo
            reticle = combo.currentData()
            reticle['template'].append(new_cross)
            combo.setItemData(combo.currentIndex(), reticle)
            combo.setCurrentIndex(combo.currentIndex())

    def add_dot(self):
        dlg = DotEdit(DEFAULT_DOT)
        dlg.exec_()
        if dlg.accepted:
            new_dot = dlg.get_data()
            combo = self.w.combo
            reticle = combo.currentData()
            reticle['template'].append(new_dot)
            combo.setItemData(combo.currentIndex(), reticle)
            combo.setCurrentIndex(combo.currentIndex())
