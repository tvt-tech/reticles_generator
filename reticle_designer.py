import json
import os
import sys

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow

from click_calc import ClickCalc
from layer import ReticleLayer, MagnifierEvent
from reticle_types import Click
from ui import Ui_MainWindow

from widgets import CameraPreview
from widgets import dump_reticles


DEFAULT_RET = {"name": "Cross", "multiplier": 10, "template": [
    {"type": "cross", "margin": 0.5, "size": 1, "mask": 15, "bind": True, "zoom": True,
     "min_zoom": 1, "max_zoom": 7, "pen": 1}]}


class Window(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.top = 300
        self.left = 300
        self.pm_width = 639
        self.pm_height = 479
        self.setupUi(self)

        self.title = "Reticle"

        self.x0 = self.pm_width / 2 + 1
        self.y0 = self.pm_height / 2 + 1
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

        self.magnifier_event = MagnifierEvent(self.x0, self.y0)
        self.draw_magnifier(self.magnifier_event, is_map=False)
        self.magnifier.resetMagnifierPos()

        self.combo.currentIndexChanged.connect(self.change_ret)
        self.grid_on.stateChanged.connect(self.enable_grid)
        self.spin_x.valueChanged.connect(self.edit_x_click)
        self.spin_y.valueChanged.connect(self.edit_y_click)
        self.mk_reticle2_x4.clicked.connect(self.dump_reticles)
        self.edit_click.clicked.connect(self.click_calculator)
        self.table.doubleClicked.connect(self.table_double_clicked)
        self.table.clicked.connect(self.table_clicked)
        self.btn.clicked.connect(self.btn_zoom)

        self.preview.clicked.connect(self.show_preview)

    def show_preview(self):

        camera_layer = self.findChild(QtWidgets.QWidget, 'camera_layer')
        if not camera_layer:

            camera_layer = CameraPreview(self)
            camera_layer.setObjectName('camera_layer')
            self.gridLayout.addWidget(camera_layer, 0, 0, 1, 3)

            camera_layer.stackUnder(self.grid)
            self.gridLayout.addWidget(camera_layer.camera_selector, 4, 1)
            self.preview.setText('Hide preview')

            self.magnifier.setVisible(False)

        else:
            camera_layer.camera = None
            camera_layer.camera_selector.deleteLater()
            camera_layer.deleteLater()

            self.preview.setText('Preview')

            self.magnifier.setVisible(True)

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
        if QApplication.widgetAt(self.cursor().pos()) == self.overlay and not self.magnifier.is_pressed:
            self.draw_magnifier(event)
        elif self.magnifier.is_pressed:
            self.draw_magnifier(event)
        return super().mouseMoveEvent(event)

    def draw_magnifier(self, event, is_map=True):
        self.magnifier.draw(event, self.label, self.grid, is_map)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.magnifier.is_pressed = False
        # if QApplication.widgetAt(self.cursor().pos()) == self.overlay:
        self.draw_magnifier(event)
        return super().mouseReleaseEvent(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.magnifier.is_pressed = True
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
        oname = None
        if self.sender():
            oname = self.sender().objectName()
        if QApplication.widgetAt(self.cursor().pos()) == self.overlay or oname:
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
            if self.magnifier.magnifier_event:
                self.draw_magnifier(self.magnifier.magnifier_event, is_map=False)
            else:
                self.draw_magnifier(MagnifierEvent(self.x0, self.y0))

    def draw_watermark(self):
        self.watermark.draw(
            f'{self.reticle["name"]} {self.zoom}X,'
            f' V:{round(self.click.y / self.zoom, 2)},'
            f' H:{round(self.click.x / self.zoom, 2)}'
        )

    def draw_layers(self):
        canvas = QPixmap(self.pm_width, self.pm_height)
        canvas.fill(Qt.transparent)
        highlighter_color = QtGui.QColor('#3F57D2')
        highlited_index = self.table.currentIndex().row()
        canvas = self.draw_ret(canvas, self.reticle, self.zoom, highlited_index, highlighter_color)
        self.label.setPixmap(canvas)
        self.enable_grid()
        self.draw_watermark()
        self.info_label.setText(
            f'{self.zoom}X, V:{round(self.click.y / self.zoom, 2)}, H:{round(self.click.x / self.zoom, 2)}'
        )
        if hasattr(self, 'magnifier_event'):
            if self.magnifier.magnifier_event:
                self.draw_magnifier(self.magnifier.magnifier_event, is_map=False)
            else:
                self.draw_magnifier(MagnifierEvent(self.x0, self.y0))

    def draw_ret(self, canvas=None, reticle=None, zoom=None, highlited_index=None, highlighter_color=Qt.black):
        multiplier = reticle['multiplier']
        x1 = multiplier / self.click.x
        y1 = multiplier / self.click.y
        painter = QPainter(canvas)
        font = QtGui.QFont("BankGothic Lt BT")
        font.setStyleStrategy(QtGui.QFont.NoAntialias)
        font.setPixelSize(11)
        painter.setFont(font)
        painter.device().height()
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        template = reticle['template']
        reticle_layer = ReticleLayer()
        reticle_layer.draw(painter, template, self.x0, self.y0, x1, y1, zoom, highlited_index, highlighter_color)
        return canvas

    def dump_reticles(self):
        dump_reticles(self)

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.show()


App = QApplication(sys.argv)

from PyQt5 import QtGui

_id = QtGui.QFontDatabase.addApplicationFont("Bank Gothic Light BT.ttf")
fid = QtGui.QFontDatabase.applicationFontFamilies(_id)

window = Window()

sys.exit(App.exec())
