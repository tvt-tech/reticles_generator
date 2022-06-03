from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QPixmap, QColor, QPen
from PyQt5.QtCore import Qt, QPoint


class DotLabel(QtWidgets.QLabel):
    def __init__(self):
        super(DotLabel, self).__init__()

    def draw(self, pen=None):
        pixmap = QPixmap(31, 31)
        center = QPoint(15, 15)
        pixmap.fill(QColor(Qt.gray))
        self.setPixmap(pixmap)
        painter = QPainter(self.pixmap())

        painter.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine, Qt.FlatCap))
        painter.drawLine(0, 15, 31, 15)
        painter.drawLine(15, 0, 15, 31)

        painter.setPen(QPen(Qt.black, pen, Qt.SolidLine))

        if pen == 1:
            painter.drawPoint(center)

        if 5 >= pen > 1:
            painter.drawPoint(center)
            painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
            painter.drawPoint(center)

        if pen > 5:
            painter.setPen(QPen(Qt.black, pen, Qt.SolidLine, Qt.RoundCap))
            painter.drawPoint(center)
            painter.setPen(QPen(Qt.white, pen-5, Qt.SolidLine, Qt.RoundCap))
            painter.drawPoint(center)


class DotEdit(QtWidgets.QDialog):
    def __init__(self, dot):
        super(DotEdit, self).__init__()
        self.dot = dot
        self.setupUI()
        self.init_data()

    def init_data(self):
        index = self.min_zoom.findData(self.dot['min_zoom'])
        self.min_zoom.setCurrentIndex(index)

        index = self.max_zoom.findData(self.dot['max_zoom'])
        self.max_zoom.setCurrentIndex(index)

        self.pen.setValue(self.dot['pen'])

        self.x_offset.setValue(self.dot['x_offset'])
        self.y_offset.setValue(self.dot['y_offset'])

        self.dot_view.draw(self.pen.value())

    def setupUI(self):
        self.setWindowTitle('Dot')

        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)

        labels = ['Min zoom', 'Max zoom', 'Horizontal position', 'Vertical position', 'Size']

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

        self.x_offset = QtWidgets.QDoubleSpinBox()
        self.y_offset = QtWidgets.QDoubleSpinBox()

        for j, cb in enumerate([self.x_offset, self.y_offset]):
            cb.setMinimum(-320)
            cb.setMaximum(320)
            self.gridLayout.addWidget(cb, j + 2, 1)

        self.pen = QtWidgets.QSpinBox()
        self.pen.setMinimum(1)
        self.pen.setMaximum(5)
        self.pen.setSingleStep(2)
        self.pen.setValue(3)
        self.pen.lineEdit().setDisabled(True)
        self.gridLayout.addWidget(self.pen, 4, 1)

        self.dot_view = DotLabel()
        self.gridLayout.addWidget(self.dot_view, 5, 1)

        view_changed = lambda: self.dot_view.draw(self.pen.value())
        self.pen.valueChanged.connect(view_changed)

        self.box = QtWidgets.QDialogButtonBox()
        self.box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.box.setCenterButtons(True)
        self.box.accepted.connect(self.accept)
        self.box.rejected.connect(self.reject)
        self.gridLayout.addWidget(self.box, 6, 0, 1, 2)

    def get_data(self):
        self.dot = {'max_zoom': self.max_zoom.currentData(),
                    'min_zoom': self.min_zoom.currentData(),
                    'pen': self.pen.value(),
                    'type': 'dot',
                    'x_offset': self.x_offset.value(),
                    'y_offset': self.y_offset.value()}
        return self.dot
