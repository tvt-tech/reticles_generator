import json
import os
import sys

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QDoubleSpinBox, QPushButton, \
    QCheckBox, QProgressBar, QComboBox

from click_calc import ClickCalc
from layer import PixmapLayer, GridLayer, Watermark, ReticleLayer
from reticle_types import Click
from widgets import ReticleTable

from reticle2 import ImgMap, Reticle4z, SMALL_RETS, LRF_RETS, PXL4


DEFAULT_RET = {"name": "Cross", "multiplier": 10, "template": [
    {"type": "cross", "margin": 0.5, "size": 1, "mask": 15, "bind": True, "zoom": True,
     "min_zoom": 1, "max_zoom": 7, "pen": 1}]}


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.background = PixmapLayer(self.width, self.height, Qt.gray)
        self.background.setAlignment(Qt.AlignTop)
        self.gridLayout.addWidget(self.background, 0, 0, 1, 3)

        self.grid = GridLayer(self.width, self.height, Qt.transparent)
        self.grid.setAlignment(Qt.AlignTop)
        self.gridLayout.addWidget(self.grid, 0, 0, 1, 3)

        self.watermark = Watermark(self.width, self.height, Qt.transparent)
        self.watermark.setAlignment(Qt.AlignTop)
        self.gridLayout.addWidget(self.watermark, 0, 0, 1, 3)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignTop)
        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)

        self.overlay = PixmapLayer(self.width, self.height, Qt.transparent)
        self.overlay.setAlignment(Qt.AlignTop)
        self.gridLayout.addWidget(self.overlay, 0, 0, 1, 3)

        self.magnifier_back = QLabel(self.label)
        magnifier = QPixmap(128, 128)
        magnifier.fill(Qt.gray)
        self.magnifier_back.setPixmap(magnifier)

        self.magnifier_grid = QLabel(self.label)
        magnifier = QPixmap(128, 128)
        self.magnifier_grid.setPixmap(magnifier)

        self.magnifier = QLabel(self.label)
        magnifier = QPixmap(128, 128)
        self.magnifier.setPixmap(magnifier)

        self.btn = QPushButton('Zoom')
        self.gridLayout.addWidget(self.btn, 1, 0, 1, 1)

        self.info_label = QLabel()
        self.gridLayout.addWidget(self.info_label, 1, 1, 1, 1)

        self.grid_on = QCheckBox(text='Enable grid')

        self.gridLayout.addWidget(self.grid_on, 1, 2, 1, 1)

        self.table = ReticleTable()
        self.gridLayout.addWidget(self.table, 0, 3, 2, 1)

        self.spin_x = QDoubleSpinBox()
        self.spin_y = QDoubleSpinBox()
        self.spin_x.setPrefix('X:')
        self.spin_y.setPrefix('Y:')
        self.spin_x.setSingleStep(0.01)
        self.spin_x.setMinimum(0.01)
        self.spin_y.setMinimum(0.01)
        self.spin_y.setSingleStep(0.01)

        self.gridLayout.addWidget(self.spin_x, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.spin_y, 2, 1, 1, 1)

        self.combo = QComboBox()

        self.gridLayout.addWidget(self.combo, 2, 2, 1, 1)
        self.mk_reticle2_x4 = QPushButton('Сreate 4-zoom reticle2')
        self.gridLayout.addWidget(self.mk_reticle2_x4, 3, 0, 1, 1)
        self.progress = QProgressBar()
        self.gridLayout.addWidget(self.progress, 3, 1, 1, 2)
        self.edit_click = QPushButton('Click Calculator')
        self.gridLayout.addWidget(self.edit_click, 3, 3, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)


class MagnifierEvent(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def pos(self):
        return QPoint(self.x, self.y)


class Window(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.top = 300
        self.left = 300
        self.width = 639
        self.height = 479
        self.setupUi(self)

        self.title = "Reticle"

        self.x0 = self.width / 2 + 1
        self.y0 = self.height / 2 + 1
        self._zoom = 1
        self._click = Click(1.7, 1.7)

        # self.click = Click(1.42, 1.42)
        # self.click = Click(2.13, 2.13)
        # self.click = Click(3.01, 3.01)
        # self.click = Click(1.27, 1.27)

        self.spin_x.setValue(self.click.x)
        self.spin_y.setValue(self.click.y)
        self.load_templates()
        self._reticle = self.combo.currentData()

        self.canvas = None

        self.InitWindow()

        self.grid_on.setChecked(True)
        self.load_table()
        self.draw_layers()

        self.is_pressed = False
        self.magnifier_event = MagnifierEvent(self.x0, self.y0)
        self.draw_magnifier(self.magnifier_event, map=False)
        self.resetMagnifierPos()

        self.combo.currentIndexChanged.connect(self.change_ret)
        self.grid_on.stateChanged.connect(self.enable_grid)
        self.spin_x.valueChanged.connect(self.edit_x_click)
        self.spin_y.valueChanged.connect(self.edit_y_click)
        self.mk_reticle2_x4.clicked.connect(self.dump_reticles)
        self.edit_click.clicked.connect(self.click_calculator)
        self.table.doubleClicked.connect(self.table_double_clicked)
        self.table.clicked.connect(self.table_clicked)
        self.btn.clicked.connect(self.btn_zoom)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value: int):
        self._zoom = value
        self.draw_layers()

    @property
    def click(self):
        return self._click

    @click.setter
    def click(self, value: Click):
        self._click = value
        self.draw_layers()

    @property
    def reticle(self):
        return self._reticle

    @reticle.setter
    def reticle(self, value: dict):
        self._reticle = value
        self.draw_layers()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if QApplication.widgetAt(self.cursor().pos()) == self.overlay:
            self.draw_magnifier(event)
        return super().mouseMoveEvent(event)

    def draw_magnifier(self, event, map=True):
        if map:
            label_pos = self.label.mapFrom(self, event.pos())
        else:
            label_pos = event.pos()
        x, y = label_pos.x(), label_pos.y()

        x -= 32 if x >= 32 else 0
        y -= 32 if y >= 32 else 0
        if x >= self.width - 64:
            x = self.width - 64
        if y >= self.height - 64:
            y = self.height - 64

        rect = QtCore.QRect(x, y, 64, 64)
        pixmap = self.label.pixmap().copy(rect)
        pixmap = pixmap.scaled(128, 128)
        self.magnifier.setPixmap(pixmap)
        painter = QPainter(self.magnifier.pixmap())
        painter.setPen(QPen(Qt.black, 1))
        painter.drawLine(0, 0, 0, 127)
        painter.drawLine(0, 0, 127, 0)
        painter.drawLine(127, 127, 127, 0)
        painter.drawLine(127, 127, 0, 127)

        rect = QtCore.QRect(x, y, 64, 64)
        pixmap = self.grid.pixmap().copy(rect)
        pixmap = pixmap.scaled(128, 128)
        self.magnifier_grid.setPixmap(pixmap)

        self.magnifier_event = MagnifierEvent(label_pos.x(), label_pos.y())

        if self.is_pressed:
            self.setMagnifierPos(label_pos)
        else:
            self.resetMagnifierPos()

    def resetMagnifierPos(self):
        self.magnifier.move(self.width - 128, 0)
        self.magnifier_grid.move(self.width - 128, 0)
        self.magnifier_back.move(self.width - 128, 0)

    def setMagnifierPos(self, index):
        self.magnifier.move(index.x() - 64, index.y() - 64)
        self.magnifier_grid.move(index.x() - 64, index.y() - 64)
        self.magnifier_back.move(index.x() - 64, index.y() - 64)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.is_pressed = False
        if QApplication.widgetAt(self.cursor().pos()) == self.overlay:
            self.draw_magnifier(event)
        return super().mouseReleaseEvent(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.is_pressed = True
        if QApplication.widgetAt(self.cursor().pos()) == self.overlay:
            self.draw_magnifier(event)
        return super().mousePressEvent(event)

    def table_clicked(self, index):
        self.zoom = self.table.table_clicked(index, self.reticle['template'], self.zoom)

    def table_double_clicked(self, index):
        template = self.table.table_double_clicked(index, self.reticle['template'], self.zoom)
        self.reticle['template'] = template
        self.combo.setItemData(self.combo.currentIndex(), self.reticle)
        self.draw_layers()

    def load_templates(self):
        self.combo.addItem(DEFAULT_RET['name'], DEFAULT_RET)
        cur_path = os.path.dirname(__file__)
        files = os.listdir(cur_path + r'\reticle_templates')
        templates = [f for f in files if f.endswith('.json')]
        for t in templates:
            with open(f'reticle_templates/{t}', 'r') as fp:
                data = json.load(fp)
                self.combo.addItem(data['name'], data)

    def edit_x_click(self, value):
        self.click = Click(value, self.click.y)

    def edit_y_click(self, value):
        self.click = Click(self.click.x, value)

    def change_ret(self):
        self.reticle = self.combo.currentData()
        self.load_table()

    def click_calculator(self):
        dlg = ClickCalc()
        ret = dlg.exec_()
        if ret:
            click = dlg.get_click()
            self.spin_x.setValue(click.x)
            self.spin_y.setValue(click.y)
            self.draw_layers()

    def load_table(self):
        self.table.load_table(self.reticle['template'])

    def btn_zoom(self):
        if self.zoom < 4:
            z = self.zoom + 1
        elif self.zoom == 4:
            z = 6
        else:
            z = 1
        self.zoom = round(z, 1)

    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        if QApplication.widgetAt(self.cursor().pos()) == self.overlay:
            delta = a0.angleDelta().y()
            idx = 0
            if delta > 0 and self.zoom < 6:
                idx = 1
            elif delta < 0 and self.zoom > 1:
                idx = -1

            if self.zoom + idx == 5:
                self.zoom = round(self.zoom + 2 * idx, 1)
            else:
                self.zoom = round(self.zoom + idx, 1)
        return super().wheelEvent(a0)

    def enable_grid(self, event=None):

        if self.grid_on.isChecked():
            multiplier = self.reticle['multiplier']
            x1 = multiplier / self.click.x
            y1 = multiplier / self.click.y
            self.grid.draw(self.x0, self.y0, x1, y1, self.zoom)
        else:
            self.grid.erase()

        if hasattr(self, 'magnifier_event'):
            if self.magnifier_event:
                self.draw_magnifier(self.magnifier_event, map=False)
            else:
                self.draw_magnifier(MagnifierEvent(self.x0, self.y0))

    def draw_watermark(self):
        self.watermark.draw(
            f'{self.reticle["name"]} {self.zoom}X,'
            f' V:{round(self.click.y / self.zoom, 2)},'
            f' H:{round(self.click.x / self.zoom, 2)}'
        )

    def draw_layers(self):
        canvas = QPixmap(self.width, self.height)
        canvas.fill(Qt.transparent)
        highlighter_color = QtGui.QColor('#3F57D2')
        canvas = self.draw_ret(canvas, highlighter_color)
        self.label.setPixmap(canvas)
        self.enable_grid()
        self.draw_watermark()
        self.info_label.setText(
            f'{self.zoom}X, V:{round(self.click.y / self.zoom, 2)}, H:{round(self.click.x / self.zoom, 2)}'
        )
        if hasattr(self, 'magnifier_event'):
            if self.magnifier_event:
                self.draw_magnifier(self.magnifier_event, map=False)
            else:
                self.draw_magnifier(MagnifierEvent(self.x0, self.y0))

    def draw_ret(self, canvas=None, highlighter_color=Qt.black):
        multiplier = self.reticle['multiplier']
        x1 = multiplier / self.click.x
        y1 = multiplier / self.click.y
        painter = QPainter(canvas)
        font = QtGui.QFont("BankGothic Lt BT")
        font.setStyleStrategy(QtGui.QFont.NoAntialias)
        font.setPixelSize(11)
        painter.setFont(font)
        painter.device().height()
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        template = self.reticle['template']
        highlited_index = self.table.currentIndex().row()
        reticle_layer = ReticleLayer()
        reticle_layer.draw(painter, template, self.x0, self.y0, x1, y1, self.zoom, highlited_index, highlighter_color)
        return canvas

    def dump_reticles(self):
        self.setDisabled(True)
        base = []
        cur_zoom = self.zoom
        cur_reticle = self.combo.currentData()
        progress_max = self.combo.count() * 4
        self.progress.setMaximum(progress_max - 1)

        for i in range(self.combo.count()):
            self.reticle = self.combo.itemData(i)
            zooms = []
            for j in [1, 2, 3, 4]:
                self.zoom = j
                canvas = QPixmap(self.width, self.height)
                canvas.fill(Qt.white)
                self.draw_ret(canvas=canvas)
                img = canvas.toImage()
                zooms.append(ImgMap(img))
                fmt_str = f'{self.reticle["name"]}, {j}X, %p%'
                self.progress.setFormat(fmt_str)
                self.progress.setValue(self.progress.value() + 1)
            base.append(Reticle4z(*zooms))
        d = PXL4.dump(SMALL_RETS, [], base, LRF_RETS)
        file_data = PXL4.build(d)

        click_x = str(self.click.x).replace('.', '_')
        click_y = str(self.click.y).replace('.', '_')
        with open(f'{click_x}x{click_y}_4x.reticle2', 'wb') as fp:
            fp.write(file_data)
        self.progress.setFormat('%p%')
        self.progress.setValue(0)
        self.zoom = cur_zoom
        self.reticle = cur_reticle

        self.setDisabled(False)

        # self.draw_layers()

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.show()


App = QApplication(sys.argv)

from PyQt5 import QtCore, QtGui

_id = QtGui.QFontDatabase.addApplicationFont("Bank Gothic Light BT.ttf")
# _id = QtGui.QFontDatabase.addApplicationFont("square-723.ttf")
fid = QtGui.QFontDatabase.applicationFontFamilies(_id)

window = Window()

sys.exit(App.exec())
