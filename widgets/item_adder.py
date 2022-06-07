from PyQt5 import QtWidgets, QtGui
from ret_edit import DIALOGS


DEFAULT_CROSS = {"type": "cross",
                 "margin": 0.5,
                 "size": 1,
                 "mask": 15,
                 "bind": True,
                 "zoomed": True,
                 "min_zoom": 1,
                 "max_zoom": 6,
                 "pen": 1}

DEFAULT_DOT = {"type": "dot",
               "x_offset": 0,
               "y_offset": 0,
               "pen": 3,
               "min_zoom": 1,
               "max_zoom": 6}

DEFAULT_RULER = {"type": "vruler",
                 "a": -10,
                 "b": 10,
                 "step": 1,
                 "w": 0.3,
                 "x_offset": 0,
                 "y_offset": 0,
                 "mode": "grid",
                 "min_zoom": 1,
                 "max_zoom": 6,
                 "pen": 1,
                 "exclude_0": True}

DEFAULT_LINE = {"type": "line",
                "min_zoom": 1,
                "max_zoom": 6,
                "x_offset": 0,
                "y_offset": 0,
                "p1": [0.7, 1.2],
                "p2": [-0.7, 1.2],
                "pen": 1,
                "zoomed": False},

DEFAULT_TEXT = {"type": "text",
                "text": "SAMPLE TEXT",
                "x_offset": 5,
                "y_offset": 3,
                "min_zoom": 1,
                "max_zoom": 6,
                "pen": 1}

DEFAULTS = {'cross': DEFAULT_CROSS,
            'dot': DEFAULT_DOT,
            'ruler': DEFAULT_RULER,
            'line': DEFAULT_LINE,
            'text': DEFAULT_TEXT}


class ItemAdder(QtWidgets.QPushButton):
    def __init__(self, w):
        super(ItemAdder, self).__init__()
        self.w = w
        self.context = QtWidgets.QMenu()
        for key in DEFAULTS.keys():
            action = self.context.addAction(key)
            action.setText(key[0].upper() + key[1:])
            action.setData(key)

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        action = self.context.exec_(self.mapToGlobal(e.pos()))
        if action:
            dlg = DIALOGS[action.data()](DEFAULTS[action.data()])
            res = dlg.exec_()
            if res:
                new_item = dlg.get_data()
                combo = self.w.combo
                reticle = combo.currentData()
                reticle['template'].append(new_item)
                combo.setItemData(combo.currentIndex(), reticle)
                combo.setCurrentIndex(combo.currentIndex())
                self.w.reticle = self.w.combo.currentData()
                self.w.load_table()
                self.w.draw_layers()
        return super().mousePressEvent(e)
