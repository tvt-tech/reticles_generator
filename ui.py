from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtGui

from layer import PixmapLayer, GridLayer, Watermark, Magnifier
from widgets import ReticleTable, ItemAdder


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.background = PixmapLayer(self.pm_width, self.pm_height, QtCore.Qt.gray)
        self.background.setAlignment(QtCore.Qt.AlignTop)
        self.gridLayout.addWidget(self.background, 0, 0, 1, 3)

        self.grid = GridLayer(self.pm_width, self.pm_height, QtCore.Qt.transparent)
        self.grid.setAlignment(QtCore.Qt.AlignTop)
        self.gridLayout.addWidget(self.grid, 0, 0, 1, 3)

        self.watermark = Watermark(self.pm_width, self.pm_height, QtCore.Qt.transparent)
        self.watermark.setAlignment(QtCore.Qt.AlignTop)
        self.gridLayout.addWidget(self.watermark, 0, 0, 1, 3)

        self.label = QtWidgets.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignTop)
        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)

        self.overlay = PixmapLayer(self.pm_width, self.pm_height, QtCore.Qt.transparent)
        self.overlay.setAlignment(QtCore.Qt.AlignTop)
        self.gridLayout.addWidget(self.overlay, 0, 0, 1, 3)

        self.magnifier = Magnifier(self.pm_width, self.pm_height)
        self.magnifier.setParent(self.label)

        self.btn = QtWidgets.QPushButton('Zoom')
        self.gridLayout.addWidget(self.btn, 1, 0, 1, 1)

        self.info_label = QtWidgets.QLabel()
        self.gridLayout.addWidget(self.info_label, 1, 1, 1, 1)

        self.grid_on = QtWidgets.QCheckBox(text='Enable grid')

        self.gridLayout.addWidget(self.grid_on, 1, 2, 1, 1)

        self.table = ReticleTable()
        self.gridLayout.addWidget(self.table, 0, 3, 2, 1)

        self.spin_x = QtWidgets.QDoubleSpinBox()
        self.spin_y = QtWidgets.QDoubleSpinBox()
        self.spin_x.setPrefix('X:')
        self.spin_y.setPrefix('Y:')
        self.spin_x.setSingleStep(0.01)
        self.spin_x.setMinimum(0.01)
        self.spin_y.setMinimum(0.01)
        self.spin_y.setSingleStep(0.01)

        self.gridLayout.addWidget(self.spin_x, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.spin_y, 2, 1, 1, 1)

        self.combo = QtWidgets.QComboBox()

        self.gridLayout.addWidget(self.combo, 2, 2, 1, 1)
        self.mk_reticle2_x4 = QtWidgets.QPushButton('Сreate 4-zoom reticle2')
        self.gridLayout.addWidget(self.mk_reticle2_x4, 3, 0, 1, 1)
        self.progress = QtWidgets.QProgressBar()
        self.gridLayout.addWidget(self.progress, 3, 1, 1, 2)
        self.edit_click = QtWidgets.QPushButton('Click Calculator')
        self.gridLayout.addWidget(self.edit_click, 3, 3, 1, 1)

        self.preview = QtWidgets.QPushButton('Preview')
        self.gridLayout.addWidget(self.preview)

        self.item_adder = ItemAdder(self)
        self.item_adder.setText('Add')
        self.gridLayout.addWidget(self.item_adder, 2, 3)

        MainWindow.setCentralWidget(self.centralwidget)
