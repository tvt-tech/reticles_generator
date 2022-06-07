from PyQt5 import QtWidgets

from .cross_edit import CrossLabel
from .dot_edit import DotLabel


class RulerEdit(QtWidgets.QDialog):
    def __init__(self, ruler):
        super(RulerEdit, self).__init__()
        self.ruler = ruler
        self.setupUI()
        self.init_data()

    def setupUI(self):
        self.setWindowTitle('Ruler')

        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)

        labels = ['Direction', 'Min zoom', 'Max zoom',
                  'Horizontal position', 'Vertical position',
                  'Min value', 'Max value',
                  'Step', 'Fatness', 'Width', 'Mode']

        for i, k in enumerate(labels):
            label = QtWidgets.QLabel(k)
            self.gridLayout.addWidget(label, i, 0, 1, 1)

        self.direction = QtWidgets.QComboBox()
        self.direction.addItem('Vertical', 'vruler')
        self.direction.addItem('Horizontal', 'hruler')
        self.gridLayout.addWidget(self.direction, 0, 1)

        self.min_zoom = QtWidgets.QComboBox()
        self.max_zoom = QtWidgets.QComboBox()
        self.min_zoom.setObjectName('min_zoom')
        self.max_zoom.setObjectName('max_zoom')

        for j, cb in enumerate([self.min_zoom, self.max_zoom]):
            for i in (1, 2, 3, 4, 6, 7):
                cb.addItem(str(i), i)
            self.gridLayout.addWidget(cb, j + 1, 1)

        self.x_offset = QtWidgets.QDoubleSpinBox()
        self.y_offset = QtWidgets.QDoubleSpinBox()

        for j, cb in enumerate([self.x_offset, self.y_offset]):
            cb.setMinimum(-320)
            cb.setMaximum(320)
            self.gridLayout.addWidget(cb, j + 3, 1)

        self.a = QtWidgets.QDoubleSpinBox()
        self.b = QtWidgets.QDoubleSpinBox()

        for j, cb in enumerate([self.a, self.b]):
            cb.setMinimum(-320)
            cb.setMaximum(320)
            self.gridLayout.addWidget(cb, j + 5, 1)

        self.step = QtWidgets.QDoubleSpinBox()

        self.gridLayout.addWidget(self.step, 7, 1)

        self.pen = QtWidgets.QSpinBox()
        self.pen.setMinimum(1)
        self.pen.setMaximum(5)
        self.pen.setSingleStep(2)
        self.pen.lineEdit().setDisabled(True)
        self.gridLayout.addWidget(self.pen, 8, 1)

        self.width = QtWidgets.QDoubleSpinBox()
        self.width.setMinimum(0)
        self.width.setMaximum(320)
        self.width.setSingleStep(0.01)
        self.gridLayout.addWidget(self.width, 9, 1)

        self.mode = QtWidgets.QComboBox()
        self.mode.addItem('Grid', 'grid')
        self.mode.addItem('Crosses', 'cross')
        self.mode.addItem('Dots', 'dot')
        self.mode.addItem('Values', 'ruler')
        self.gridLayout.addWidget(self.mode, 10, 1)

        self.mirror_x = QtWidgets.QCheckBox(text='Flip vertically')
        self.mirror_y = QtWidgets.QCheckBox(text='Flip horizontally')
        self.exclude_0 = QtWidgets.QCheckBox(text='Skip center point')

        self.gridLayout.addWidget(self.mirror_x)
        self.gridLayout.addWidget(self.mirror_y)
        self.gridLayout.addWidget(self.exclude_0)


        self.groupbox = QtWidgets.QGroupBox()
        self.groupbox_layout = QtWidgets.QGridLayout()
        self.groupbox.setLayout(self.groupbox_layout)
        self.gridLayout.addWidget(self.groupbox, 1, 3, 5, 2)

        self.gridLayout.addWidget(QtWidgets.QLabel(text='Crosses settings:'), 0, 3, 1, 1)

        cross_labels = ['Size format', 'Zoomed', 'Margin center', 'Size', 'View']

        for i, k in enumerate(cross_labels):
            label = QtWidgets.QLabel(k)
            self.groupbox_layout.addWidget(label, i, 0, 1, 1)

        self.bind = QtWidgets.QComboBox()
        self.bind.setObjectName('bind')
        self.bind.addItem('Pixels', False)
        self.bind.addItem('MIL', True)
        self.groupbox_layout.addWidget(self.bind, 0, 1)

        self.zoom = QtWidgets.QComboBox()
        self.zoom.setObjectName('zoomed')
        self.zoom.addItem('Disable', False)
        self.zoom.addItem('Enable', True)
        self.groupbox_layout.addWidget(self.zoom, 1, 1)

        self.margin = QtWidgets.QDoubleSpinBox()
        self.margin.setObjectName('margin')
        self.margin.setMinimum(0)
        self.margin.setMaximum(320)
        self.margin.setSingleStep(0.05)
        self.groupbox_layout.addWidget(self.margin, 2, 1)

        self.size = QtWidgets.QDoubleSpinBox()
        self.size.setObjectName('size')
        self.size.setMinimum(0)
        self.size.setMaximum(320)
        self.size.setSingleStep(0.05)
        self.groupbox_layout.addWidget(self.size, 3, 1)

        self.mask = QtWidgets.QSpinBox()
        self.mask.setObjectName('mask')
        self.mask.setMinimum(1)
        self.mask.setMaximum(15)
        self.groupbox_layout.addWidget(self.mask, 4, 1)

        self.p_view = None
        view_changed = None
        if self.ruler['mode'] == 'cross':
            self.p_view = CrossLabel()
        elif self.ruler['mode'] == 'dot':
            self.p_view = DotLabel()

        if self.p_view:
            self.gridLayout.addWidget(self.p_view, 6, 3)
            view_changed = lambda: self.p_view.draw(self.mask.value(), self.pen.value())
            self.mask.valueChanged.connect(view_changed)
            self.pen.valueChanged.connect(view_changed)

        self.pen.valueChanged.connect(self.change_view)
        self.mask.valueChanged.connect(self.change_view)
        self.mode.currentIndexChanged.connect(self.change_view)

        self.box = QtWidgets.QDialogButtonBox()
        self.box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.box.setCenterButtons(True)
        self.box.accepted.connect(self.accept)
        self.box.rejected.connect(self.reject)
        self.gridLayout.addWidget(self.box, self.gridLayout.rowCount(), 0, 1, self.gridLayout.columnCount())

    def change_view(self):
        self.p_view = None
        view_changed = None
        if self.mode.currentData() == 'cross':
            self.p_view = CrossLabel()
        elif self.mode.currentData() == 'dot':
            self.p_view = DotLabel()
        else:
            self.p_view = None

        if self.p_view:
            self.gridLayout.addWidget(self.p_view, 6, 3)
            view_changed = lambda: self.p_view.draw(self.mask.value(), self.pen.value())
            self.mask.valueChanged.connect(view_changed)
            self.pen.valueChanged.connect(view_changed)
            if isinstance(self.p_view, DotLabel):
                self.p_view.draw(self.pen.value())
            elif isinstance(self.p_view, CrossLabel):
                self.p_view.draw(self.mask.value(), self.pen.value())

        else:
            item = self.gridLayout.itemAtPosition(6, 3)
            if item:
                widget = item.widget()
                if widget:
                    self.gridLayout.removeWidget(self.gridLayout.itemAtPosition(6, 3).widget())

    def init_data(self):
        self.direction.setCurrentIndex(self.direction.findData(self.ruler['type']))
        self.min_zoom.setCurrentIndex(self.min_zoom.findData(self.ruler['min_zoom']))
        self.max_zoom.setCurrentIndex(self.max_zoom.findData(self.ruler['max_zoom']))
        self.x_offset.setValue(self.ruler['x_offset'])
        self.y_offset.setValue(self.ruler['y_offset'])
        self.a.setValue(self.ruler['a'])
        self.b.setValue(self.ruler['b'])
        self.step.setValue(self.ruler['step'])
        self.pen.setValue(self.ruler['pen'])
        self.width.setValue(self.ruler['w'])
        self.mode.setCurrentIndex(self.mode.findData(self.ruler['mode']))

        if 'mirror_x' in self.ruler:
            self.mirror_x.setChecked(self.ruler['mirror_x'])
        if 'mirror_y' in self.ruler:
            self.mirror_y.setChecked(self.ruler['mirror_y'])
        if 'exclude_0' in self.ruler:
            self.exclude_0.setChecked(self.ruler['exclude_0'])

        if 'cross' in self.ruler:
            self.bind.setCurrentIndex(self.bind.findData(self.ruler['cross']['bind']))
            self.zoom.setCurrentIndex(self.zoom.findData(self.ruler['cross']['zoomed']))
            self.margin.setValue(self.ruler['cross']['margin'])
            self.size.setValue(self.ruler['cross']['size'])
            self.mask.setValue(self.ruler['cross']['mask'])

        if self.p_view:
            self.p_view.draw(self.mask.value(), self.pen.value())


    def get_data(self):
        self.ruler = {
            'a': self.a.value(),
            'b': self.b.value(),
            'min_zoom': self.min_zoom.currentData(),
            'max_zoom': self.max_zoom.currentData(),
            'x_offset': self.x_offset.value(),
            'y_offset': self.y_offset.value(),
            'mirror_x': self.mirror_x.isChecked(),
            'mirror_y': self.mirror_y.isChecked(),
            'exclude_0': self.exclude_0.isChecked(),
            'type': self.direction.currentData(),
            'step': self.step.value(),
            'pen': self.pen.value(),
            'w': self.width.value(),
            'mode': self.mode.currentData(),
            'cross': {
                'margin': self.margin.value(),
                'size': self.size.value(),
                'zoomed': self.zoom.currentData(),
                'bind': self.bind.currentData(),
                'mask': self.mask.value()
            }

        }
        return self.ruler
