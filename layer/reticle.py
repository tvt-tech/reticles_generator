from PyQt5 import QtGui, QtWidgets, QtCore
from reticle_types import TYPES





class ReticleLayer(object):
    def __init__(self):
        super(ReticleLayer, self).__init__()

    def draw(self, painter, template, x0, y0, x1, y1, zoom, highlited_index, highlighter_color):
        for index, t_data in enumerate(template):
            if 'hide' not in t_data:
                t_data['hide'] = False
            t = t_data.copy()
            if highlited_index == index:
                t['color'] = highlighter_color
            else:
                t['color'] = QtCore.Qt.black
            if t['max_zoom'] >= zoom >= t['min_zoom'] and not t['hide']:
                item_class = TYPES[t['type']]
                if t['type'] in ['hruler', 'vruler']:
                    self._draw_ruler(item_class, painter, x0, y0, x1, y1, zoom, **t)
                else:
                    item_class(painter, x0, y0, x1, y1, zoom, **t)

    def _draw_ruler(self, item_class, painter, x0, y0, x1, y1, zoom, **t):
        item_class(painter, x0, y0, x1, y1, zoom, **t)
        if 'mirror_x' in t:
            if t['mirror_x']:
                item_class(painter, x0, y0, x1, y1, zoom, **t, flip_x=True)
        if 'mirror_y' in t:
            if t['mirror_y']:
                item_class(painter, x0, y0, x1, y1, zoom, **t, flip_y=True)
        if 'mirror_x' in t and 'mirror_y' in t:
            if t['mirror_x'] and t['mirror_y']:
                item_class(painter, x0, y0, x1, y1, zoom, **t, flip_x=True, flip_y=True)
