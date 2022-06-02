from PyQt5 import QtWidgets, QtCore
from reticle_types import Kit, Click


class ClickCalc(QtWidgets.QDialog):
    def __init__(self):
        super(ClickCalc, self).__init__()

        self.kit = Kit(360, 288, 17, 50, 720, 576)

        self.setupUI()

        self.setData()

    def setupUI(self):
        self.setWindowTitle('Click Calculator')
        self.gridLayout = QtWidgets.QGridLayout(self)

        self.setLayout(self.gridLayout)

        self.core_rez_x = QtWidgets.QSpinBox(self)
        self.core_rez_y = QtWidgets.QSpinBox(self)
        self.pixel_size = QtWidgets.QSpinBox(self)
        self.lens_focus = QtWidgets.QSpinBox(self)
        self.video_rez_x = QtWidgets.QSpinBox(self)
        self.video_rez_y = QtWidgets.QSpinBox(self)
        self.core_rez_x.setMaximum(4096)
        self.core_rez_y.setMaximum(4096)
        self.pixel_size.setMaximum(20)
        self.lens_focus.setMaximum(100)
        self.lens_focus.setMinimum(1)
        self.video_rez_x.setMaximum(4096)
        self.video_rez_x.setMinimum(1)
        self.video_rez_y.setMaximum(4096)
        self.video_rez_y.setMinimum(1)

        self.gridLayout.addWidget(QtWidgets.QLabel('Core horizontal resolution:'), 0, 0, 1, 1)
        self.gridLayout.addWidget(QtWidgets.QLabel('Core vertical resolution:'), 1, 0, 1, 1)
        self.gridLayout.addWidget(QtWidgets.QLabel('Core pixel size (um):'), 2, 0, 1, 1)
        self.gridLayout.addWidget(QtWidgets.QLabel('Lens focus:'), 3, 0, 1, 1)
        self.gridLayout.addWidget(QtWidgets.QLabel('Output horizontal resolution'), 4, 0, 1, 1)
        self.gridLayout.addWidget(QtWidgets.QLabel('Output vertical resolution:'), 5, 0, 1, 1)

        self.gridLayout.addWidget(self.core_rez_x, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.core_rez_y, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.pixel_size, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.lens_focus, 3, 1, 1, 1)
        self.gridLayout.addWidget(self.video_rez_x, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.video_rez_y, 5, 1, 1, 1)

        self.box = QtWidgets.QDialogButtonBox()
        self.box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)
        self.box.setCenterButtons(True)
        self.gridLayout.addWidget(self.box, 7, 0, 1, 2)

        self.box.accepted.connect(self.accept)
        self.box.rejected.connect(self.reject)

    def setData(self):
        self.core_rez_x.setValue(self.kit.core_rez_x)
        self.core_rez_y.setValue(self.kit.core_rez_y)
        self.pixel_size.setValue(self.kit.pixel_size * 1000)
        self.lens_focus.setValue(self.kit.lens_focus)
        self.video_rez_x.setValue(self.kit.video_rez_x)
        self.video_rez_y.setValue(self.kit.video_rez_y)

    def get_click(self):
        self.kit = Kit(
            self.core_rez_x.value(),
            self.core_rez_y.value(),
            self.pixel_size.value(),
            self.lens_focus.value(),
            self.video_rez_x.value(),
            self.video_rez_y.value(),
        )
        return self.kit.click()
