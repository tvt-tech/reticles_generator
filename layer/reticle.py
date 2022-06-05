from PyQt5 import QtGui, QtWidgets, QtCore
from reticle_types import Cross, Dot, VRuler, HRuler, Line, Text


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

            if t['max_zoom'] > zoom >= t['min_zoom'] and not t['hide']:
                if t['type'] == 'line':
                    Line(painter, x0, y0, x1, y1, zoom, **t)
                if t['type'] == 'dot':
                    Dot(painter, x0, y0, x1, y1, zoom, **t)
                if t['type'] == 'cross':
                    Cross(painter, x0, y0, x1, y1, zoom, **t)
                if t['type'] in ['hruler', 'vruler']:
                    if t['type'] == 'hruler':
                        ruler = HRuler
                    elif t['type'] == 'vruler':
                        ruler = VRuler
                    else:
                        ruler = HRuler
                    ruler(painter, x0, y0, x1, y1, zoom, **t)

                    if 'mirror_x' in t:
                        if t['mirror_x']:
                            ruler(painter, x0, y0, x1, y1, zoom, **t, flip_x=True)

                    if 'mirror_y' in t:
                        if t['mirror_y']:
                            ruler(painter, x0, y0, x1, y1, zoom, **t, flip_y=True)

                    if 'mirror_x' in t and 'mirror_y' in t:
                        if t['mirror_x'] and t['mirror_y']:
                            ruler(painter, x0, y0, x1, y1, zoom, **t, flip_x=True, flip_y=True)