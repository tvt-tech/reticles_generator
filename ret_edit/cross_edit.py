from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QPixmap, QColor, QPen
from PyQt5.QtCore import Qt, QLine


class CrossLabel(QtWidgets.QLabel):
    def __init__(self):
        super(CrossLabel, self).__init__()

    def draw(self, index, pen):
        pixmap = QPixmap(32, 31)
        pixmap.fill(QColor(Qt.gray))
        self.setPixmap(pixmap)
        painter = QPainter(self.pixmap())

        painter.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine, Qt.FlatCap))
        painter.drawLine(0, 15, 31, 15)
        painter.drawLine(15, 0, 15, 31)

        painter.setPen(QPen(Qt.black, pen, Qt.SolidLine, Qt.FlatCap))
        left, right, bottom, top = [index >> i & 1 for i in range(4 - 1, -1, -1)]

        lines = []

        if left:
            lines.append(QLine(13, 15, 4, 15))
        if right:
            lines.append(QLine(18, 15, 27, 15))
        if top:
            lines.append(QLine(15, 13, 15, 4))
        if bottom:
            lines.append(QLine(15, 18, 15, 27))
        painter.drawLines(*lines)


class CrossEdit(QtWidgets.QDialog):
    def __init__(self, cross):
        super(CrossEdit, self).__init__()
        self.cross = cross

        self.setupUI()

        self.init_data()

    def init_data(self):
        index = self.min_zoom.findData(self.cross['min_zoom'])
        self.min_zoom.setCurrentIndex(index)

        index = self.max_zoom.findData(self.cross['max_zoom'])
        self.max_zoom.setCurrentIndex(index)

        self.bind.setCurrentIndex(self.bind.findData(self.cross['bind']))
        self.zoom.setCurrentIndex(self.zoom.findData(self.cross['zoomed']))
        self.margin.setValue(self.cross['margin'])
        self.size.setValue(self.cross['size'])
        self.mask.setValue(self.cross['mask'])
        self.pen.setValue(self.cross['pen'])

        if 'x_offset' in self.cross:
            self.x_offset.setValue(self.cross['x_offset'])
        if 'y_offset' in self.cross:
            self.y_offset.setValue(self.cross['y_offset'])

        self.cross_view.draw(self.mask.value(), self.pen.value())

    def setupUI(self):
        self.setWindowTitle('Cross')

        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)

        labels = ['Min zoom', 'Max zoom', 'Size format', 'Zoomed', 'Margin center', 'Size',
                  'Horizontal position', 'Vertical position',
                  'View', 'Fatness', ]

        for i, k in enumerate(labels):
            label = QtWidgets.QLabel(k)
            self.gridLayout.addWidget(label, i, 0, 1, 1)

        self.min_zoom = QtWidgets.QComboBox()
        self.max_zoom = QtWidgets.QComboBox()
        self.min_zoom.setObjectName('min_zoom')
        self.max_zoom.setObjectName('max_zoom')

        for j, cb in enumerate([self.min_zoom, self.max_zoom]):
            for i in (1, 2, 3, 4, 6, 7):
                cb.addItem(str(i), i)
            self.gridLayout.addWidget(cb, j, 1)

        self.bind = QtWidgets.QComboBox()
        self.bind.setObjectName('bind')
        self.bind.addItem('Pixels', False)
        self.bind.addItem('MIL', True)
        self.gridLayout.addWidget(self.bind, 2, 1)

        self.zoom = QtWidgets.QComboBox()
        self.zoom.setObjectName('zoomed')
        self.zoom.addItem('Disable', False)
        self.zoom.addItem('Enable', True)
        self.gridLayout.addWidget(self.zoom, 3, 1)

        self.margin = QtWidgets.QDoubleSpinBox()
        self.margin.setObjectName('margin')
        self.margin.setMinimum(0)
        self.margin.setMaximum(320)
        self.margin.setSingleStep(0.05)
        self.gridLayout.addWidget(self.margin, 4, 1)

        self.size = QtWidgets.QDoubleSpinBox()
        self.size.setObjectName('size')
        self.size.setMinimum(0)
        self.size.setMaximum(320)
        self.size.setSingleStep(0.05)
        self.gridLayout.addWidget(self.size, 5, 1)

        self.x_offset = QtWidgets.QDoubleSpinBox()
        self.y_offset = QtWidgets.QDoubleSpinBox()

        for j, cb in enumerate([self.x_offset, self.y_offset]):
            cb.setMinimum(-320)
            cb.setMaximum(320)
            self.gridLayout.addWidget(cb, j + 6, 1)

        self.mask = QtWidgets.QSpinBox()
        self.mask.setObjectName('mask')
        self.mask.setMinimum(1)
        self.mask.setMaximum(15)
        self.mask.setValue(15)
        self.gridLayout.addWidget(self.mask, 8, 1)

        self.pen = QtWidgets.QSpinBox()
        self.pen.setMinimum(1)
        self.pen.setMaximum(11)
        self.pen.setSingleStep(2)
        self.pen.lineEdit().setDisabled(True)
        self.gridLayout.addWidget(self.pen, 9, 1)

        self.cross_view = CrossLabel()
        self.gridLayout.addWidget(self.cross_view, 10, 1)

        view_changed = lambda: self.cross_view.draw(self.mask.value(), self.pen.value())

        self.mask.valueChanged.connect(view_changed)
        self.pen.valueChanged.connect(view_changed)

        self.box = QtWidgets.QDialogButtonBox()
        self.box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)
        self.box.setCenterButtons(True)
        self.box.accepted.connect(self.accept)
        self.box.rejected.connect(self.reject)
        self.gridLayout.addWidget(self.box, 11, 0, 1, 2)

    def get_data(self):
        self.cross = {'bind': self.bind.currentData(),
                      'margin': self.margin.value(),
                      'mask': self.mask.value(),
                      'max_zoom': self.max_zoom.currentData(),
                      'min_zoom': self.min_zoom.currentData(),
                      'pen': self.pen.value(),
                      'size': self.size.value(),
                      'type': 'cross',
                      'zoomed': self.zoom.currentData(),
                      'x_offset': self.x_offset.value(),
                      'y_offset': self.y_offset.value()}
        return self.cross
