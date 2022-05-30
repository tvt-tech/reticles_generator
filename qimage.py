from construct import Struct, Int32ul, Container
from PyQt5.QtGui import QImage


class QImgMap(object):
    def __init__(self, data):
        self.data = data


def read(img: QImage, w: int, h: int):
    pixels = []
    for p in range(w):
        pixels.append(f'{p}' / Int32ul)
    header = Struct(
        *pixels
    )

    output = []
    for y in range(h):
        ptr = img.scanLine(y)
        ptr.setsize(w * 4)
        data = ptr.asstring()
        input: Container = header.parse(data)
        input.pop('_io')

        sx, counter = None, 0
        for x, (k, v) in enumerate(input.items()):

            if v != 4294967295:
                if not sx:
                    sx = x
                    counter += 1
                else:
                    if counter > 0:
                        output.append((counter, y, sx))
                    sx, counter = None, 0
    return output

