import json
from pathlib import Path

from PyQt5.QtCore import QSizeF, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QFontDatabase, QWheelEvent
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QToolButton, QDoubleSpinBox, \
    QComboBox, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QSizePolicy, QGridLayout, QMainWindow

from graphics_view.vector_view import VectorViewer
from graphics_view.raster_view import RasterViewer
from graphics_view.gv import DrawMode
from reticle2 import *

import rsrc
assert rsrc


class PreviewLabel(QLabel):
    doubleClicked = pyqtSignal()
    zoomed = pyqtSignal(object)

    def __init__(self, parent=None):
        super(PreviewLabel, self).__init__(parent)
        self._is_full = False
        self.zoom = 1
        self.def_size = QSize(160, 120)
        self.setFixedSize(self.def_size)
        self.setToolTip('Double-click to expand')

    def mouseDoubleClickEvent(self, event: 'QMouseEvent') -> None:
        if self._is_full:
            self.setFixedSize(self.def_size)
            self._is_full = False
            self.setToolTip('Double-click to expand')
        else:
            self.setFixedSize(640, 480)
            self._is_full = True
            self.setToolTip('Double-click to decrease')
        self.doubleClicked.emit()
        super(PreviewLabel, self).mouseDoubleClickEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        self.zoomed.emit(event)
        super(PreviewLabel, self).wheelEvent(event)


class CustomDoubleSpinbox(QDoubleSpinBox):

    def validate(self, text: str, pos: int) -> object:
        text = text.replace(".", ",")
        return QDoubleSpinBox.validate(self, text, pos)

    def valueFromText(self, text: str) -> float:
        text = text.replace(",", ".")
        return float(text)


class DrawModeBtn(QPushButton):
    def __init__(self, *args, **kwargs):
        super(DrawModeBtn, self).__init__(*args, **kwargs)
        self.setFixedSize(50, 30)
        # self.setText('Draw')
        self.is_enabled = False
        self.clicked.connect(self.change_mode)

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

        self.setStyleSheet("""
        #RetEdit {background-color: #303440; color: #dadada;}
                QDoubleSpinBox, QComboBox {
                    background-color: #3c4454;
                    color: #dadada;
                    border: 0px;
                }
                QPushButton, QToolButton {
                    background-color: #303440;
                    color: #dadada;
                    border: 0px;
                }
                QPushButton:pressed, QToolButton:pressed {
                    background-color: #3c4454;
                    color: #dadada;
                }
                QPushButton:hover, QToolButton:hover {
                    background-color: #3c4454;
                    color: #dadada;
                }
        """)

        # self.filename = filename if filename is not None else 'reticle.abcv'
        self.filename = filename

        self._vector_mode = False

        if self.filename is not None:

            self.filename = Path(self.filename)
            if self.filename.exists():
                if self.filename.suffix == '.json':
                    clicks = QSizeF(0.50, 0.50)
                    self._vector_mode = True
                    self.viewer = VectorViewer(self, QSize(640, 480), clicks=clicks)
                    with open(self.filename, 'r') as fp:
                        self.template = json.load(fp)
                    self.viewer.draw_sketch(self.template)
                elif self.filename.suffix == '.png':

                    fn = str(self.filename).replace('.png', '').split('_')
                    x, y = float(fn[1]), float(fn[2])

                    clicks = QSizeF(x, y)
                    self.viewer = RasterViewer(self, QSize(640, 480), clicks=clicks)
                    self.viewer.setPix(QPixmap(str(self.filename)))
                else:
                    sys.exit()
            else:
                sys.exit()

        else:
            clicks = QSizeF(0.5, 0.5)
            self._vector_mode = True
            self.viewer = VectorViewer(self, QSize(640, 480), clicks=clicks)

        self.viewer._history_append()

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
        self.clear_btn.setFixedSize(50, 30)
        self.clear_btn.setText('Clear')
        self.clear_btn.clicked.connect(self.on_clear_btn_press)

        self.to_svg_btn = QToolButton(self)
        # self.to_svg_btn.setText('To SVG')
        self.to_svg_btn.setIcon(QIcon(':/btns/filetype-json.svg'))
        self.to_svg_btn.setFixedSize(50, 30)
        self.to_svg_btn.clicked.connect(self.on_to_svg_btn_press)

        self.raster_btn = QToolButton(self)
        # self.raster_btn.setText('To BMP')
        self.raster_btn.setIcon(QIcon(':/btns/filetype-bmp.svg'))
        self.raster_btn.setFixedSize(50, 30)
        self.raster_btn.clicked.connect(self.on_raster_btn_press)

        self.reticle2_btn = QToolButton(self)
        self.reticle2_btn.setText('To ret2')
        # self.reticle2_btn.setIcon(QIcon(':/btns/filetype-bmp.svg'))
        self.reticle2_btn.setFixedSize(50, 30)
        self.reticle2_btn.clicked.connect(self.on_reticle2_btn_press)

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
        self.ruler_combo.setFixedSize(50, 30)
        for s in [0.05, 0.1, 0.2, 0.25, 0.3, 0.5, 1, 2, 5, 10]:
            self.ruler_combo.addItem(f'{s} mil', s)
        self.ruler_combo.currentIndexChanged.connect(self.ruler_step_change)
        self.ruler_combo.setCurrentIndex(self.ruler_combo.findData(1))

        self.text_btn = DrawModeBtn()
        self.text_btn.setIcon(QIcon(':/btns/type.svg'))
        self.text_btn.clicked.connect(self.on_text_btn_press)

        self.font_size_combo = QComboBox()
        self.font_size_combo.setFixedSize(50, 30)
        for s in [7, 8, 9, 10]:
            self.font_size_combo.addItem(f'{s} pt', s)
        self.font_size_combo.currentIndexChanged.connect(self.font_size_change)

        self.font_size_combo.setCurrentIndex(self.font_size_combo.findData(8))

        # self.nums_btn = DrawModeBtn()
        # self.nums_btn.setText('123')
        # self.nums_btn.clicked.connect(self.on_nums_btn_press)

        self.sb_click_x = CustomDoubleSpinbox()
        self.sb_click_y = CustomDoubleSpinbox()
        self.sb_click_x.setFixedSize(50, 20)
        self.sb_click_y.setFixedSize(50, 20)
        self.sb_click_x.setValue(clicks.width())
        self.sb_click_y.setValue(clicks.height())
        self.sb_click_x.setMinimum(0.01)
        self.sb_click_x.setMaximum(10)
        self.sb_click_x.setSingleStep(0.01)
        self.sb_click_y.setMinimum(0.01)
        self.sb_click_y.setMaximum(10)
        self.sb_click_y.setSingleStep(0.01)

        self.keep_ratio = QCheckBox('Keep ratio')
        self.keep_ratio.setFixedSize(80, 30)
        if self.sb_click_x.value() == self.sb_click_y.value():
            self.keep_ratio.setChecked(True)

        self.undo_btn = QToolButton()
        # self.undo_btn.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self.undo_btn.setIcon(QIcon(':/btns/arrow-counterclockwise.svg'))
        self.undo_btn.clicked.connect(self.viewer.undo)

        self.redo_btn = QToolButton()
        # self.redo_btn.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self.redo_btn.setIcon(QIcon(':/btns/arrow-clockwise.svg'))
        self.redo_btn.clicked.connect(self.viewer.redo)

        # self.drawing = False
        # make last point to the point of cursor

        # hotkey binds
        self.no_tool_btn.setShortcut(Qt.Key_1)
        self.no_tool_btn.setToolTip("1")
        self.pencil_btn.setShortcut(Qt.Key_2)
        self.pencil_btn.setToolTip("2")
        self.eraser_btn.setShortcut(Qt.Key_3)
        self.eraser_btn.setToolTip("3")
        self.line_btn.setShortcut(Qt.Key_4)
        self.line_btn.setToolTip("4")
        self.rect_btn.setShortcut(Qt.Key_5)
        self.rect_btn.setToolTip("5")
        self.ellipse_btn.setShortcut(Qt.Key_6)
        self.ellipse_btn.setToolTip("6")
        self.ruler_btn.setShortcut(Qt.Key_7)
        self.ruler_btn.setToolTip("7")
        self.text_btn.setShortcut(Qt.Key_8)
        self.text_btn.setToolTip('8')
        # self.nums_btn.setShortcut(Qt.Key_9)
        # self.nums_btn.setToolTip("9")

        self.raster_btn.setShortcut(Qt.CTRL + Qt.Key_S)
        self.raster_btn.setToolTip("Ctrl + S")

        self.undo_btn.setShortcut(Qt.CTRL + Qt.Key_Z)
        self.undo_btn.setToolTip("Ctrl + Z")
        self.redo_btn.setShortcut(Qt.CTRL + Qt.SHIFT + Qt.Key_Z)
        self.redo_btn.setToolTip("Ctrl + Shift + Z")
        self.undo_btn.setFixedSize(25, 25)
        self.redo_btn.setFixedSize(25, 25)

        self.preview_label = QLabel('Preview')
        self.preview = PreviewLabel()
        self.preview.setStyleSheet("""QLabel {background-color: white;};""")
        # self.preview_combo = QComboBox()
        # for i in [1, 2, 3, 4, 6]:
        #     self.preview_combo.addItem(f'x{i}', i)

        # self.preview_combo.currentIndexChanged.connect(self.prev_zoom_changed)
        self.sb_click_x.valueChanged.connect(self.prev_zoom_changed)
        self.sb_click_y.valueChanged.connect(self.prev_zoom_changed)
        self.preview.doubleClicked.connect(self.prev_zoom_changed)
        self.preview.zoomed.connect(self.prev_zoom_changed)

        # self.preview_combo.setCurrentIndex(0)

        # Arrange layout
        self.mainLayout = QGridLayout(self)
        self.setLayout(self.mainLayout)

        # self.mainLayout.setContentsMargins(0, 0, 0, 0)


        self.do_undo = QWidget()
        self.do_undoLayout = QHBoxLayout(self)
        self.do_undo.setLayout(self.do_undoLayout)
        self.do_undoLayout.setContentsMargins(0, 0, 0, 0)
        self.do_undoLayout.setSpacing(0)
        self.do_undoLayout.addWidget(self.undo_btn)
        self.do_undoLayout.addWidget(self.redo_btn)

        self.toolbar = QWidget()

        self.toolbarLayout = QVBoxLayout(self)
        self.toolbarLayout.setContentsMargins(0, 0, 0, 0)
        self.toolbarLayout.setSpacing(0)
        self.toolbar.setLayout(self.toolbarLayout)

        self.toolbarLayout.addWidget(self.do_undo)
        self.toolbarLayout.addWidget(self.no_tool_btn)
        self.toolbarLayout.addWidget(self.pencil_btn)
        self.toolbarLayout.addWidget(self.eraser_btn)
        self.toolbarLayout.addWidget(self.line_btn)
        self.toolbarLayout.addWidget(self.rect_btn)
        self.toolbarLayout.addWidget(self.ellipse_btn)
        self.toolbarLayout.addWidget(self.ruler_btn)
        self.toolbarLayout.addWidget(self.text_btn)
        self.toolbarLayout.addWidget(self.clear_btn)
        self.toolbarLayout.addWidget(self.to_svg_btn)
        self.toolbarLayout.addWidget(self.raster_btn)
        self.toolbarLayout.addWidget(self.reticle2_btn)
        self.toolbarLayout.setAlignment(Qt.AlignTop)

        self.toolbar2 = QWidget()
        self.toolbar2Layout = QGridLayout(self)
        self.toolbar2Layout.setContentsMargins(0, 0, 0, 0)
        # self.toolbar2Layout.setSpacing(0)
        self.toolbar2.setLayout(self.toolbar2Layout)
        self.toolbar2Layout.setAlignment(Qt.AlignLeft)
        # self.toolbar2Layout.addWidget(self.do_undo, 0, 0, 2, 1)
        self.toolbar2Layout.addWidget(QLabel('Click H:'), 0, 1)
        self.toolbar2Layout.addWidget(QLabel('Click V:'), 1, 1)
        self.toolbar2Layout.addWidget(self.sb_click_x, 0, 2)
        self.toolbar2Layout.addWidget(self.sb_click_y, 1, 2)
        self.toolbar2Layout.addWidget(self.keep_ratio, 0, 3, 2, 1)
        self.toolbar2Layout.addWidget(self.ruler_combo, 0, 4, 2, 1)
        self.toolbar2Layout.addWidget(self.font_size_combo, 0, 5, 2, 1)

        self.mainLayout.addWidget(self.toolbar, 0, 0, 2, 1)
        self.mainLayout.addWidget(self.toolbar2, 0, 1)
        self.mainLayout.addWidget(self.viewer, 1, 1)
        self.mainLayout.addWidget(self.preview, 1, 1)
        self.mainLayout.addWidget(self.preview_label, 1, 1)

        self.mainLayout.setAlignment(self.preview_label, Qt.AlignTop | Qt.AlignRight)
        self.mainLayout.setAlignment(self.preview, Qt.AlignTop | Qt.AlignRight)

        if not self._vector_mode:
            self.to_svg_btn.setHidden(True)
            self.ruler_btn.setHidden(True)
            self.ruler_combo.setHidden(True)
            self.sb_click_x.setDisabled(True)
            self.sb_click_y.setDisabled(True)
            self.preview.setHidden(True)
            # self.preview_combo.setHidden(True)


        self.installEventFilter(self.viewer._scene)

        self.prev_zoom_changed()

    # def on_nums_btn_press(self):
    #     self.on_notool_btn_press()
    #     self.viewer.draw_mode = DrawMode.Numbers
    #     self.viewer.toggleDragMode()

    def font_size_change(self, index):
        self.viewer.font_size = self.font_size_combo.currentData()

    def prev_zoom_changed(self, event=None):
        if isinstance(event, QWheelEvent):
            if event.angleDelta().y() > 0:
                self.preview.zoom += (2 if self.preview.zoom == 4 else 1 if self.preview.zoom < 6 else 0)
            elif event.angleDelta().y() < 0:
                self.preview.zoom -= (2 if self.preview.zoom == 6 else 1 if self.preview.zoom > 1 else 0)
        if self.keep_ratio.isChecked():
            if self.sender() == self.sb_click_x:
                self.sb_click_y.setValue(self.sb_click_x.value())
            elif self.sender() == self.sb_click_y:
                self.sb_click_x.setValue(self.sb_click_y.value())
        viewer = RasterViewer(self, clicks=QSizeF(self.sb_click_x.value(), self.sb_click_y.value()) / self.preview.zoom)
        viewer.draw_sketch(self.viewer.get_vectors(False))
        pix = viewer.get_raster().scaled(self.preview.rect().size(), transformMode=Qt.SmoothTransformation)


        self.preview.setPixmap(pix)
        self.preview_label.setText(f'Preview {self.preview.zoom}x')
        viewer.deleteLater()

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

    def on_text_btn_press(self):
        self.on_notool_btn_press()
        self.viewer.draw_mode = DrawMode.Text
        self.viewer.toggleDragMode()

    def on_raster_btn_press(self, *args, **kwargs):
        path = Path('compiled')
        if not path.exists():
            Path.mkdir(path)
        if self._vector_mode:
            for z in [1, 2, 3, 4, 6]:
                viewer = RasterViewer(self, clicks=QSizeF(self.sb_click_x.value(), self.sb_click_y.value()) / z)
                viewer.draw_sketch(self.viewer.get_vectors(False))
                pix = viewer.get_raster()
                fpath = Path(path, f'ret_{round(self.sb_click_x.value(), 2)}_{round(self.sb_click_y.value(), 2)}.png')
                pix.save(str(fpath), 'PNG')
        else:
            pix = self.viewer.get_raster()
            fpath = Path(path, f'ret_{round(self.sb_click_x.value(), 2)}_{round(self.sb_click_y.value(), 2)}.png')
            pix.save(str(fpath), 'PNG')

    @timeit
    def on_reticle2_btn_press(self, *args, **kwargs):

        base = []
        lrf = []

        if self._vector_mode:

            templates = Path(Path(__file__).parent, 'vector_templates').iterdir()
            templates = [i for i in templates if i.suffix == '.json']

            for t in templates:

                with open(str(t), 'rb') as fp:
                    template = json.load(fp)
                    print(str(t))

                zooms = []
                for z in [1, 2, 3, 4]:
                    viewer = VectorViewer(self, clicks=QSizeF(0.5, 0.5) / z)
                    viewer.draw_sketch(template)
                    vects = viewer.get_vectors(False)
                    rviewer = RasterViewer(self, clicks=QSizeF(self.sb_click_x.value(), self.sb_click_y.value()) / z)
                    rviewer.draw_sketch(vects)
                    pix = rviewer.get_raster(Qt.white)
                    img = pix.toImage()
                    zooms.append(ImgMap(img))

                base.append(Reticle4z(*zooms))

            d = PXL4.dump(SMALL_RETS, [], base, lrf)
            file_data = PXL4.build(d)

            click_x = str(self.sb_click_y.value()).replace('.', '_')
            click_y = str(self.sb_click_y.value()).replace('.', '_')
            with open(f'{click_x}x{click_y}_4x.reticle2', 'wb') as fp:
                fp.write(file_data)

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
        self.viewer.setPix(QPixmap('1_3 MIL-R.bmp'))

    def pixInfo(self):
        self.viewer.toggleDragMode()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    _id = QFontDatabase.addApplicationFont("Bank Gothic Light BT.ttf")
    fid = QFontDatabase.applicationFontFamilies(_id)

    filename = app.arguments()[1] if len(app.arguments()) > 1 else None
    window = Window(filename)
    window.setGeometry(500, 300, 800, 600)
    window.show()
    sys.exit(app.exec_())
