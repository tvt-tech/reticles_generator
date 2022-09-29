from reticle2 import ImgMap, Reticle4z, SMALL_RETS, LRF_RETS, PXL4
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


def dump_reticles(self):
    self.setDisabled(True)
    base = []
    lrf = []
    cur_zoom = self.zoom
    cur_reticle = self.combo.currentData()
    progress_max = self.combo.count() * 4
    self.progress.setMaximum(progress_max - 1)

    for i in range(self.combo.count()):
        reticle = self.combo.itemData(i)

        zooms = []

        if not reticle['name'].startswith('LRF'):
            zoomlist = [1, 2, 3, 4]
        if reticle['name'].startswith('LRF'):
            zoomlist = [1]

        for zoom in zoomlist:
            canvas = QPixmap(self.pm_width, self.pm_height)
            canvas.fill(Qt.white)
            self.draw_ret(canvas, reticle, zoom)
            img = canvas.toImage()
            zooms.append(ImgMap(img))
            fmt_str = f'{reticle["name"]}, {zoom}X, %_p%'
            self.progress.setFormat(fmt_str)
            self.progress.setValue(self.progress.value() + 1)

        if not reticle['name'].startswith('LRF'):
            base.append(Reticle4z(*zooms))
        elif reticle['name'].startswith('LRF'):
            lrf.append(Reticle4z(*zooms))

    d = PXL4.dump(SMALL_RETS, [], base, lrf)
    file_data = PXL4.build(d)

    click_x = str(self.click.x).replace('.', '_')
    click_y = str(self.click.y).replace('.', '_')
    with open(f'{click_x}x{click_y}_4x.reticle2', 'wb') as fp:
        fp.write(file_data)
    self.progress.setFormat('%_p%')
    self.progress.setValue(0)
    self.zoom = cur_zoom
    self.reticle = cur_reticle

    self.setDisabled(False)