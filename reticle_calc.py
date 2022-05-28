import json
import os
import sys

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QDoubleSpinBox, QPushButton, \
    QCheckBox, QProgressBar, QComboBox, QTableView

from click_calc import ClickCalc
from layer import PixmapLayer, GridLayer, Watermark
from ret_edit import CrossEdit, DotEdit, RulerEdit
from reticle_types import Click, Cross, Dot, HRuler, VRuler

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

        self.background = PixmapLayer(640, 480, Qt.gray)
        self.gridLayout.addWidget(self.background, 0, 0, 1, 3)

        self.grid = GridLayer(640, 480, Qt.transparent)
        self.gridLayout.addWidget(self.grid, 0, 0, 1, 3)

        self.watermark = Watermark(640, 480, Qt.transparent)
        self.gridLayout.addWidget(self.watermark, 0, 0, 1, 3)

        self.magnifier_back = QLabel()
        magnifier = QPixmap(128, 128)
        magnifier.fill(Qt.gray)
        self.magnifier_back.setPixmap(magnifier)
        self.magnifier_back.setAlignment(Qt.AlignTop|Qt.AlignRight)
        self.gridLayout.addWidget(self.magnifier_back, 0, 2, 1, 1)

        self.magnifier_grid = QLabel()
        magnifier = QPixmap(128, 128)
        self.magnifier_grid.setPixmap(magnifier)
        self.magnifier_grid.setAlignment(Qt.AlignTop|Qt.AlignRight)
        self.gridLayout.addWidget(self.magnifier_grid, 0, 2, 1, 1)

        self.magnifier = QLabel()
        magnifier = QPixmap(128, 128)
        self.magnifier.setPixmap(magnifier)
        self.magnifier.setAlignment(Qt.AlignTop|Qt.AlignRight)
        self.gridLayout.addWidget(self.magnifier, 0, 2, 1, 1)

        self.label = QLabel()
        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)

        self.btn = QPushButton('Zoom')
        self.gridLayout.addWidget(self.btn, 1, 0, 1, 1)

        self.info_label = QLabel()
        self.gridLayout.addWidget(self.info_label, 1, 1, 1, 1)

        self.grid_on = QCheckBox(text='Enable grid')

        self.gridLayout.addWidget(self.grid_on, 1, 2, 1, 1)

        self.table = QTableView()
        self.gridLayout.addWidget(self.table, 0, 3, 2, 1)
        self.table.setMinimumWidth(300)
        self.table.setMaximumWidth(300)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        header = self.table.verticalHeader()
        header.setDefaultSectionSize(1)

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
        self.setupUi(self)

        self.title = "Reticle"

        self.top = 300
        self.left = 300
        self.width = 639
        self.height = 479

        self.x0 = self.width / 2 + 1
        self.y0 = self.height / 2 + 1
        self.zoom = 1
        self.click = Click(1.7, 1.7)

        # self.click = Click(1.42, 1.42)
        # self.click = Click(2.13, 2.13)
        # self.click = Click(3.01, 3.01)
        # self.click = Click(1.27, 1.27)

        self.spin_x.setValue(self.click.x)
        self.spin_y.setValue(self.click.y)
        self.load_templates()
        self.reticle = self.combo.currentData()

        self.InitWindow()

        self.load_table()
        self.draw_ret()

        self.magnifier_event = MagnifierEvent(self.x0, self.y0)
        self.draw_magnifier(self.magnifier_event, map=False)

        self.combo.currentIndexChanged.connect(self.change_ret)
        self.grid_on.stateChanged.connect(self.enable_grid)
        self.spin_x.valueChanged.connect(self.edit_x_click)
        self.spin_y.valueChanged.connect(self.edit_y_click)
        self.mk_reticle2_x4.clicked.connect(self.dump_reticles)
        self.edit_click.clicked.connect(self.click_calculator)
        self.table.doubleClicked.connect(self.table_double_clicked)
        self.table.clicked.connect(self.table_clicked)
        self.btn.clicked.connect(self.btn_zoom)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if QApplication.widgetAt(self.cursor().pos()) == self.label:
            self.draw_magnifier(event)
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if QApplication.widgetAt(self.cursor().pos()) == self.label:
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

    def table_clicked(self, index):

        if index.column() == 4:
            if self.reticle['template'][index.row()]['hide']:
                self.reticle['template'][index.row()]['hide'] = False
            else:
                self.reticle['template'][index.row()]['hide'] = True

            self.table_model.item(index.row(), 4).setData(self.reticle['template'][index.row()]['hide'], QtCore.Qt.DisplayRole)
        self.draw_ret()

    def table_double_clicked(self, index):
        item = self.reticle['template'][index.row()]

        dlg = None

        if -1 < index.column() < 4:
            if item['type'] == 'cross':
                dlg = CrossEdit(item)
            if item['type'] == 'dot':
                dlg = DotEdit(item)
            if item['type'] in ['vruler', 'hruler']:
                dlg = RulerEdit(item)
            if dlg is not None:
                if dlg.exec_():
                    self.reticle['template'][index.row()] = dlg.get_data()
                    self.combo.setItemData(self.combo.currentIndex(), self.reticle)
                    self.load_table()
                    self.draw_ret()

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
        self.click.x = value
        self.draw_ret()

    def edit_y_click(self, value):
        self.click.y = value
        self.draw_ret()

    def change_ret(self):
        self.reticle = self.combo.currentData()
        self.load_table()
        self.draw_ret()

    def click_calculator(self):
        dlg = ClickCalc()
        ret = dlg.exec_()
        if ret:
            click = dlg.get_click()
            self.spin_x.setValue(click.x)
            self.spin_y.setValue(click.y)
            self.draw_ret()

    def load_table(self):
        self.table_model = QtGui.QStandardItemModel(self)

        for i, y in enumerate(self.reticle['template']):
            self.table_model.setItem(i, 0, QtGui.QStandardItem())
            self.table_model.item(i, 0).setData(y['type'], QtCore.Qt.DisplayRole)
            self.table_model.setItem(i, 1, QtGui.QStandardItem())
            self.table_model.item(i, 1).setData(y['mode'] if 'mode' in y else '', QtCore.Qt.DisplayRole)
            self.table_model.setItem(i, 2, QtGui.QStandardItem())
            self.table_model.item(i, 2).setData(y['min_zoom'], QtCore.Qt.DisplayRole)
            self.table_model.setItem(i, 3, QtGui.QStandardItem())
            self.table_model.item(i, 3).setData(y['max_zoom'], QtCore.Qt.DisplayRole)

            item = QtGui.QStandardItem()
            self.table_model.setItem(i, 4, item)
            if not 'hide' in 'y':
                self.reticle['template'][i]['hide'] = False
                y['hide'] = False
            self.table_model.item(i, 4).setData(y['hide'], QtCore.Qt.DisplayRole)

        self.table_model.setHorizontalHeaderLabels(['Type', 'Mode', 'Min zoom', 'Max zoom', 'Hide'])
        self.table.setModel(self.table_model)
        header = self.table.horizontalHeader()
        for i in range(header.count()):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)

    def btn_zoom(self):
        if self.zoom < 4:
            z = self.zoom + 1
        elif self.zoom == 4:
            z = 6
        else:
            z = 1
        self.zoom = round(z, 1)
        self.draw_ret()

    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        if QApplication.widgetAt(self.cursor().pos()) == self.label:
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
            self.draw_ret()
        return super().wheelEvent(a0)

    def enable_grid(self):
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

    def draw_ret(self, canvas=None):
        self.enable_grid()
        self.draw_watermark()

        self.info_label.setText(
            f'{self.zoom}X, V:{round(self.click.y / self.zoom, 2)}, H:{round(self.click.x / self.zoom, 2)}')

        multiplier = self.reticle['multiplier']
        x1 = multiplier / self.click.x
        y1 = multiplier / self.click.y

        if not canvas:
            canvas = QPixmap(640, 480)
            canvas.fill(Qt.transparent)
            self.label.setPixmap(canvas)
            painter = QPainter(self.label.pixmap())
            highlighter_color = Qt.magenta

        else:
            painter = QPainter(canvas)
            highlighter_color = Qt.black

        font = QtGui.QFont("BankGothic Lt BT")
        font.setStyleStrategy(QtGui.QFont.NoAntialias)
        font.setPixelSize(11)
        painter.setFont(font)

        painter.device().height()
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))

        template = self.reticle['template']

        for index, t_data in enumerate(template):
            if 'hide' not in t_data:
                t_data['hide'] = False
            t = t_data.copy()
            if self.table.currentIndex().row() == index:
                t['color'] = highlighter_color
            else:
                t['color'] = Qt.black

            if t['max_zoom'] > self.zoom >= t['min_zoom'] and not t['hide']:
                if t['type'] == 'dot':
                    Dot(painter, self.x0, self.y0, x1, y1, self.zoom, **t)
                if t['type'] == 'cross':
                    Cross(painter, self.x0, self.y0, x1, y1, self.zoom, **t)
                if t['type'] in ['hruler', 'vruler']:
                    if t['type'] == 'hruler':
                        ruler = HRuler
                    elif t['type'] == 'vruler':
                        ruler = VRuler
                    else:
                        ruler = HRuler
                    ruler(painter, self.x0, self.y0, x1, y1, self.zoom, **t)

                    if 'mirror_x' in t:
                        if t['mirror_x']:
                            ruler(painter, self.x0, self.y0, x1, y1, self.zoom, **t, flip_x=True)

                    if 'mirror_y' in t:
                        if t['mirror_y']:
                            ruler(painter, self.x0, self.y0, x1, y1, self.zoom, **t, flip_y=True)

                    if 'mirror_x' in t and 'mirror_y' in t:
                        if t['mirror_x'] and t['mirror_y']:
                            ruler(painter, self.x0, self.y0, x1, y1, self.zoom, **t, flip_x=True, flip_y=True)

        if hasattr(self, 'magnifier_event'):
            if self.magnifier_event:
                self.draw_magnifier(self.magnifier_event, map=False)
            else:
                self.draw_magnifier(MagnifierEvent(self.x0, self.y0))

    def dump_reticles(self):
        from reticle2 import ImgMap, Reticle4z, SMALL_RETS, LRF_RETS, PXL4
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
                canvas = QPixmap(640, 480)
                canvas.fill(Qt.white)
                self.draw_ret(canvas=canvas)
                zooms.append(ImgMap(canvas.toImage()))
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
        self.draw_ret()

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
