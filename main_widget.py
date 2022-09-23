import json
from pathlib import Path

from PyQt5.QtCore import QSizeF, QSize, Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QGraphicsView, QWidget, QPushButton, QToolButton, QLineEdit, QDoubleSpinBox, \
    QComboBox, QHBoxLayout, QVBoxLayout, QSizePolicy

from gv import VectoRaster, DrawMode

import rsrc

# import os
# os.chdir(__file__)


class DrawModeBtn(QPushButton):
    def __init__(self, *args, **kwargs):
        super(DrawModeBtn, self).__init__(*args, **kwargs)
        self.setFixedSize(70, 40)
        self.setText('Draw')
        self.is_enabled = False
        self.clicked.connect(self.change_mode)
        self.setStyleSheet("""
        QPushButton:pressed {
        background-color: rgb(72, 72, 72);
        }""")

    def change_mode(self):
        self.is_enabled = not self.is_enabled
        self.setDown(self.is_enabled)

    def reset(self):
        self.is_enabled = False
        self.setDown(self.is_enabled)


class Window(QWidget):
    def __init__(self, filename=None):
        super(Window, self).__init__()
        self.setObjectName('RetEdit')

        self.setStyleSheet("#RetEdit {background-color: rgb(72, 72, 72);}")

        # self.filename = filename if filename is not None else 'reticle.abcv'
        self.filename = filename

        if self.filename is not None:

            self.filename = Path(self.filename)
            if self.filename.exists():
                if self.filename.suffix == '.abcv':
                    clicks = QSizeF(0.5, 0.5)
                    self.viewer = VectoRaster(self, QSize(640, 480), clicks=clicks, vector_mode=True)
                    with open(self.filename, 'r') as fp:
                        self.template = json.load(fp)
                    self.viewer.load_reticle_sketch(self.template)
                elif self.filename.suffix == '.png':

                    fn = str(self.filename).replace('.png', '').split('_')
                    x, y = float(fn[2]), float(fn[3])

                    clicks = QSizeF(x, y)
                    self.viewer = VectoRaster(self, QSize(640, 480), clicks=clicks)
                    self.viewer.setPhoto(QPixmap(str(self.filename)))
                else:
                    sys.exit()
            else:
                sys.exit()

        else:
            clicks = QSizeF(0.5, 0.5)
            self.viewer = VectoRaster(self, QSize(640, 480), clicks=clicks, vector_mode=True)

        self.viewer.history_append()

        # 'Load image' button
        self.btnLoad = QToolButton(self)
        self.btnLoad.setText('Load image')
        self.btnLoad.clicked.connect(self.loadImage)
        # Button to change from drag/pan to getting pixel info
        self.btnPixInfo = QToolButton(self)
        self.btnPixInfo.setText('Enter pixel info mode')
        self.btnPixInfo.clicked.connect(self.pixInfo)

        self.editPixInfo = QLineEdit(self)
        self.editPixInfo.setReadOnly(True)
        self.viewer.photoClicked.connect(self.photoClicked)

        self.btnLoad.setHidden(True)
        self.btnPixInfo.setHidden(True)
        self.editPixInfo.setHidden(True)

        self.no_tool_btn = DrawModeBtn(self)
        # self.no_tool_btn.setText('NoTool')
        self.no_tool_btn.setText('1')
        # self.no_tool_btn.s
        self.no_tool_btn.setIcon(QIcon(':/btns/hand-index.svg'))
        self.no_tool_btn.setDown(True)
        self.no_tool_btn.clicked.connect(self.on_notool_btn_press)

        self.pencil_btn = DrawModeBtn(self)
        # self.pencil_btn.setText('Pencil')
        self.pencil_btn.setText('2')
        self.pencil_btn.setIcon(QIcon(':/btns/pencil.svg'))
        self.pencil_btn.clicked.connect(self.on_draw_btn_press)

        self.eraser_btn = DrawModeBtn(self)
        # self.eraser_btn.setText('Eraser')
        self.eraser_btn.setText('3')
        self.eraser_btn.setIcon(QIcon(':/btns/eraser.svg'))
        self.eraser_btn.clicked.connect(self.on_eraser_btn_press)

        self.line_btn = DrawModeBtn(self)
        # self.line_btn.setText('Line')
        self.line_btn.setText('4')
        self.line_btn.setIcon(QIcon(':/btns/slash-lg.svg'))
        self.line_btn.clicked.connect(self.on_line_btn_press)

        self.clear_btn = QToolButton(self)
        self.clear_btn.setFixedSize(70, 40)
        self.clear_btn.setText('Clear')
        self.clear_btn.clicked.connect(self.on_clear_btn_press)

        self.to_svg_btn = QToolButton(self)
        # self.to_svg_btn.setText('To SVG')
        self.to_svg_btn.setIcon(QIcon(':/btns/filetype-json.svg'))
        self.to_svg_btn.setFixedSize(70, 40)
        self.to_svg_btn.clicked.connect(self.on_to_svg_btn_press)

        self.raster_btn = QToolButton(self)
        # self.raster_btn.setText('To BMP')
        self.raster_btn.setIcon(QIcon(':/btns/filetype-bmp.svg'))
        self.raster_btn.setFixedSize(70, 40)
        self.raster_btn.clicked.connect(self.on_raster_btn_press)

        self.rect_btn = DrawModeBtn()
        self.rect_btn.setText('5')
        # self.rect_btn.setText('Rect')
        self.rect_btn.setIcon(QIcon(':/btns/square.svg'))
        self.rect_btn.clicked.connect(self.on_rect_btn_press)

        self.ellipse_btn = DrawModeBtn()
        self.ellipse_btn.setText('6')
        # self.ellipse_btn.setText('Ellipse')
        self.ellipse_btn.setIcon(QIcon(':/btns/circle.svg'))
        self.ellipse_btn.clicked.connect(self.on_ellipse_btn_press)

        self.ruler_btn = DrawModeBtn()
        # self.ruler_btn.setText('Ruler')
        self.ruler_btn.setText('7')
        self.ruler_btn.setIcon(QIcon(':/btns/rulers.svg'))
        self.ruler_btn.clicked.connect(self.on_ruler_btn_press)

        self.ruler_combo = QComboBox()
        self.ruler_combo.setFixedSize(70, 25)
        for i in [0.05, 0.1, 0.2, 0.25, 0.3, 0.5, 1, 2, 5, 10]:
            self.ruler_combo.addItem(f'{i} mil', i)
        self.ruler_combo.currentIndexChanged.connect(self.ruler_step_change)

        self.sb_click_x = QDoubleSpinBox()
        self.sb_click_y = QDoubleSpinBox()
        self.sb_click_x.setValue(clicks.width())
        self.sb_click_y.setValue(clicks.height())
        self.sb_click_x.setMinimum(0.01)
        self.sb_click_x.setMaximum(10)
        self.sb_click_x.setSingleStep(0.01)
        self.sb_click_y.setMinimum(0.01)
        self.sb_click_y.setMaximum(10)
        self.sb_click_y.setSingleStep(0.01)

        self.undo_btn = QPushButton()
        # self.undo_btn.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self.undo_btn.setIcon(QIcon(':/btns/arrow-counterclockwise.svg'))
        self.undo_btn.clicked.connect(self.viewer.undo)

        self.redo_btn = QPushButton()
        # self.redo_btn.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self.redo_btn.setIcon(QIcon(':/btns/arrow-clockwise.svg'))
        self.redo_btn.clicked.connect(self.viewer.redo)

        if not self.viewer._vector_mode:
            self.to_svg_btn.setHidden(True)
            self.ruler_btn.setHidden(True)
            self.ruler_combo.setHidden(True)
            self.sb_click_x.setDisabled(True)
            self.sb_click_y.setDisabled(True)

        # self.drawing = False
        # make last point to the point of cursor

        # hotkey binds
        self.no_tool_btn.setShortcut(Qt.Key_1)
        self.pencil_btn.setShortcut(Qt.Key_2)
        self.eraser_btn.setShortcut(Qt.Key_3)
        self.line_btn.setShortcut(Qt.Key_4)
        self.rect_btn.setShortcut(Qt.Key_5)
        self.ellipse_btn.setShortcut(Qt.Key_6)
        self.ruler_btn.setShortcut(Qt.Key_7)
        self.raster_btn.setShortcut(Qt.CTRL + Qt.Key_S)

        # Arrange layout
        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        do_undo = QHBoxLayout(self)
        do_undo.setContentsMargins(0, 0, 0, 0)
        do_undo.setSpacing(0)
        do_undo.addWidget(self.undo_btn)
        do_undo.addWidget(self.redo_btn)

        toolbar = QVBoxLayout(self)

        toolbar.setAlignment(Qt.AlignTop)
        toolbar.addLayout(do_undo)
        toolbar.addWidget(self.btnLoad)
        toolbar.addWidget(self.btnPixInfo)
        toolbar.addWidget(self.editPixInfo)
        toolbar.addWidget(self.no_tool_btn)
        toolbar.addWidget(self.pencil_btn)
        toolbar.addWidget(self.eraser_btn)
        toolbar.addWidget(self.line_btn)
        toolbar.addWidget(self.rect_btn)
        toolbar.addWidget(self.ellipse_btn)
        toolbar.addWidget(self.ruler_btn)
        toolbar.addWidget(self.ruler_combo)
        toolbar.addWidget(self.clear_btn)
        toolbar.addWidget(self.to_svg_btn)
        toolbar.addWidget(self.raster_btn)
        toolbar.addWidget(self.sb_click_x)
        toolbar.addWidget(self.sb_click_y)

        mainLayout.addLayout(toolbar)
        mainLayout.addWidget(self.viewer)

        self.installEventFilter(self.viewer._scene)

    def on_draw_btn_press(self):
        self.on_notool_btn_press()
        self.viewer.draw_mode = DrawMode.Pencil
        self.viewer.toggleDragMode()

    def on_eraser_btn_press(self):
        self.on_notool_btn_press()
        self.viewer.draw_mode = DrawMode.Eraser
        self.viewer.toggleDragMode()

    def on_line_btn_press(self):
        self.on_notool_btn_press()
        self.viewer.draw_mode = DrawMode.Line
        self.viewer.toggleDragMode()

    def on_notool_btn_press(self):
        self.viewer.draw_mode = DrawMode.Notool
        self.viewer.toggleDragMode()

        buttons = self.findChildren(DrawModeBtn)
        for b in buttons:
            b.reset()
        self.sender().setDown(True)

    def on_rect_btn_press(self):
        self.on_notool_btn_press()
        self.viewer.draw_mode = DrawMode.Rect
        self.viewer.toggleDragMode()

    def on_ellipse_btn_press(self):
        self.on_notool_btn_press()
        self.viewer.draw_mode = DrawMode.Ellipse
        self.viewer.toggleDragMode()

    def on_ruler_btn_press(self):
        self.on_notool_btn_press()
        self.viewer.draw_mode = DrawMode.Ruler
        self.viewer.toggleDragMode()

    def on_raster_btn_press(self, *args, **kwargs):
        if self.viewer._vector_mode:
            for i in [1, 2, 3, 4, 6]:
                # viewer = VectoRaster(self, clicks=QSizeF(2.01, 2.01) / i)
                viewer = VectoRaster(self, clicks=QSizeF(self.sb_click_x.value(), self.sb_click_y.value()) / i)
                viewer.rasterize(self.viewer.get_vectors(False))
                viewer.save_raster()
        else:
            self.viewer.save_raster()

    def on_to_svg_btn_press(self, *args, **kwargs):
        self.save_vectors()

    def on_clear_btn_press(self):
        self.viewer.clear_view()

    def ruler_step_change(self, idx):
        self.viewer.ruler_step = self.ruler_combo.currentData()

    def save_vectors(self):
        template = self.viewer.get_vectors()
        if self.filename:
            with open(self.filename, 'w') as fp:
                json.dump(template, fp)

    def loadImage(self):
        self.viewer.setPhoto(QPixmap('1_3 MIL-R.bmp'))

    def pixInfo(self):
        self.viewer.toggleDragMode()

    def photoClicked(self, pos):
        if self.viewer.dragMode() == QGraphicsView.NoDrag:
            self.editPixInfo.setText('%d, %d' % (pos.x(), pos.y()))


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    filename = app.arguments()[1] if len(app.arguments()) > 1 else None
    window = Window(filename)
    window.setGeometry(500, 300, 800, 600)
    window.show()
    sys.exit(app.exec_())
