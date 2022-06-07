from PyQt5 import QtWidgets


class LineEdit(QtWidgets.QDialog):
    def __init__(self, line):
        super(LineEdit, self).__init__()
        self.line = line

        self.setupUI()

        self.init_data()

    def init_data(self):
        index = self.min_zoom.findData(self.line['min_zoom'])
        self.min_zoom.setCurrentIndex(index)

        index = self.max_zoom.findData(self.line['max_zoom'])
        self.max_zoom.setCurrentIndex(index)

        self.zoom.setCurrentIndex(self.zoom.findData(self.line['zoomed']))

        self.pen.setValue(self.line['pen'])

        if 'x_offset' in self.line:
            self.x_offset.setValue(self.line['x_offset'])
        if 'y_offset' in self.line:
            self.y_offset.setValue(self.line['y_offset'])

        x1, y1 = self.line['p1']
        x2, y2 = self.line['p2']

        self.x1.setValue(x1)
        self.y1.setValue(y1)
        self.x2.setValue(x2)
        self.y2.setValue(y2)

    def setupUI(self):
        self.setWindowTitle('Line')

        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)

        labels = ['Min zoom', 'Max zoom',
                  'Horizontal position', 'Vertical position',
                  'X1', 'Y1', 'X2', 'Y2',
                  'Zoomed', 'Fatness', ]

        for i, k in enumerate(labels):
            label = QtWidgets.QLabel(k)
            self.gridLayout.addWidget(label, i, 0, 1, 1)

        self.min_zoom = QtWidgets.QComboBox()
        self.max_zoom = QtWidgets.QComboBox()
        self.min_zoom.setObjectName('min_zoom')
        self.max_zoom.setObjectName('max_zoom')

        for j, cb in enumerate([self.min_zoom, self.max_zoom]):
            for i in (1, 2, 3, 4, 6):
                cb.addItem(str(i), i)
            self.gridLayout.addWidget(cb, j, 1)

        self.x_offset = QtWidgets.QDoubleSpinBox()
        self.y_offset = QtWidgets.QDoubleSpinBox()

        for j, cb in enumerate([self.x_offset, self.y_offset]):
            cb.setMinimum(-320)
            cb.setMaximum(320)
            self.gridLayout.addWidget(cb, j + 2, 1)

        self.x1 = QtWidgets.QDoubleSpinBox()
        self.y1 = QtWidgets.QDoubleSpinBox()
        self.x2 = QtWidgets.QDoubleSpinBox()
        self.y2 = QtWidgets.QDoubleSpinBox()

        for j, sb in enumerate([self.x1, self.y1, self.x2, self.y2]):
            sb.setMinimum(-320)
            sb.setMaximum(320)
            sb.setSingleStep(0.01)
            self.gridLayout.addWidget(sb, j + 4, 1)

        self.zoom = QtWidgets.QComboBox()
        self.zoom.setObjectName('zoomed')
        self.zoom.addItem('Disable', False)
        self.zoom.addItem('Enable', True)
        self.gridLayout.addWidget(self.zoom, 8, 1)

        self.pen = QtWidgets.QSpinBox()
        self.pen.setMinimum(1)
        self.pen.setMaximum(11)
        self.pen.setSingleStep(2)
        self.pen.lineEdit().setDisabled(True)
        self.gridLayout.addWidget(self.pen, 9, 1)

        self.box = QtWidgets.QDialogButtonBox()
        self.box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.box.setCenterButtons(True)
        self.box.accepted.connect(self.accept)
        self.box.rejected.connect(self.reject)
        self.gridLayout.addWidget(self.box, 10, 0, 1, 2)

    def get_data(self):
        self.line = {"type": "line",
                     'max_zoom': self.max_zoom.currentData(),
                     'min_zoom': self.min_zoom.currentData(),
                     'x_offset': self.x_offset.value(),
                     'y_offset': self.y_offset.value(),
                     "p1": [round(self.x1.value(), 2), round(self.y1.value(), 2)],
                     "p2": [round(self.x2.value(), 2), round(self.y2.value(), 2)],
                     'pen': self.pen.value(),
                     'zoomed': self.zoom.currentData()}
        return self.line
