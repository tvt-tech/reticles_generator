from PyQt5 import QtWidgets


class TextEdit(QtWidgets.QDialog):
    def __init__(self, line):
        super(TextEdit, self).__init__()
        self.line = line

        self.setupUI()

        self.init_data()

    def init_data(self):
        index = self.min_zoom.findData(self.line['min_zoom'])
        self.min_zoom.setCurrentIndex(index)

        index = self.max_zoom.findData(self.line['max_zoom'])
        self.max_zoom.setCurrentIndex(index)

        self.pen.setValue(self.line['pen'])

        if 'x_offset' in self.line:
            self.x_offset.setValue(self.line['x_offset'])
        if 'y_offset' in self.line:
            self.y_offset.setValue(self.line['y_offset'])

        self.text.setText(self.line['text'])

    def setupUI(self):
        self.setWindowTitle('Line')

        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)

        labels = ['Min zoom', 'Max zoom',
                  'Horizontal position', 'Vertical position',
                  'Text',
                  'Fatness', ]

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

        self.text = QtWidgets.QLineEdit()
        self.gridLayout.addWidget(self.text, 4, 1)

        self.pen = QtWidgets.QSpinBox()
        self.pen.setMinimum(1)
        self.pen.setMaximum(11)
        self.pen.setSingleStep(2)
        self.pen.lineEdit().setDisabled(True)
        self.gridLayout.addWidget(self.pen, 5, 1)

        self.box = QtWidgets.QDialogButtonBox()
        self.box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.box.setCenterButtons(True)
        self.box.accepted.connect(self.accept)
        self.box.rejected.connect(self.reject)
        self.gridLayout.addWidget(self.box, 6, 0, 1, 2)

    def get_data(self):
        self.line = {"type": "text",
                     "text": self.text.text(),
                     'max_zoom': self.max_zoom.currentData(),
                     'min_zoom': self.min_zoom.currentData(),
                     'x_offset': self.x_offset.value(),
                     'y_offset': self.y_offset.value(),
                     "pen": self.pen.value()}
        return self.line
