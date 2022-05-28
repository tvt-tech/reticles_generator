from construct import Struct, Container, Const, Int32ul, Int32sl, BitStruct, BitsInteger, ByteSwapped
from PyQt5.QtGui import QImage


HEADER = Struct(
    'PXL2Id' / Const(b'PXL4'),
    'NumberOfReticle' / Int32sl,
    'SizeOfAllDataPXL2' / Int32ul,

    'SmallReticlesCount' / Int32ul,
    'OffsetSmallReticles' / Int32ul,
    'SmallReticlesSize' / Int32ul,

    'HoldOffReticlesCount' / Int32ul,
    'OffsetHoldOffReticles' / Int32ul,
    'HoldOffReticlesSize' / Int32ul,
    'HoldOffReticlesCrc' / Int32ul,

    'BaseReticlesCount' / Int32ul,
    'OffsetBaseReticles' / Int32ul,
    'BaseReticlesSize' / Int32ul,

    'LrfReticlesCount' / Int32ul,
    'OffsetLrfReticles' / Int32ul,
    'LrfReticlesSize' / Int32ul
)

HEADER2 = Struct(
    'offset' / Int32ul,
    'quant' / Int32ul
)

DATA2 = ByteSwapped(BitStruct(
    'x' / BitsInteger(12),
    'y' / BitsInteger(10),
    'q' / BitsInteger(10),
))


class ImgMap(object):
    def __init__(self, img: QImage):
        self._img = img
        self.data = None
        self._parse()

    def _parse(self):
        data, sx, counter = [], None, 0
        for y in range(1, 480):

            for x in range(1, 640):
                pcolor = self._img.pixelColor(x, y).value()
                if pcolor == 0:
                    if not sx:
                        sx = x
                    if sx + counter < 639:
                        counter += 1
                    else:
                        data.append((counter, y, sx))
                        sx, counter = None, 0
                else:
                    if counter > 0:
                        data.append((counter, y, sx))
                    sx, counter = None, 0
        self.data = data


class Reticle4z(object):
    def __init__(self, z1: ImgMap = None, z2: ImgMap = None, z3: ImgMap = None, z4: ImgMap = None):
        self._z1 = z1
        self._z2 = z2
        self._z3 = z3
        self._z4 = z4
        self.data = (self._z1, self._z2, self._z3, self._z4)


class PXL4(object):

    @staticmethod
    def dump(sm_ret: [Reticle4z], ho_ret: [Reticle4z], bs_ret: [Reticle4z], lrf_ret: [Reticle4z]):
        header = dict()
        ret = dict()

        header['NumberOfReticle'] = len(sm_ret) + len(ho_ret) + len(bs_ret) + len(lrf_ret)
        header['SmallReticlesCount'] = len(sm_ret)
        header['HoldOffReticlesCount'] = len(ho_ret)
        header['BaseReticlesCount'] = len(bs_ret)
        header['LrfReticlesCount'] = len(lrf_ret)
        header['HoldOffReticlesCrc'] = 0

        start_offset = HEADER.sizeof() + header['NumberOfReticle'] * 4 * HEADER2.sizeof()

        current_offset = start_offset
        current_quant = 0
        prev_offset = 0

        h2 = []

        header['OffsetSmallReticles'] = current_offset
        sm_ret_quant = 0
        for r in sm_ret:
            for z in r.data:
                if z:
                    current_quant = len(z.data)
                    sm_ret_quant += current_quant
                    h2.append({'offset': current_offset, 'quant': current_quant})
                    prev_offset = current_offset
                    current_offset += current_quant * DATA2.sizeof()
                else:
                    h2.append({'offset': prev_offset, 'quant': 0})
        header['SmallReticlesSize'] = sm_ret_quant * DATA2.sizeof()

        header['OffsetHoldOffReticles'] = current_offset
        ho_ret_quant = 0
        for r in ho_ret:
            for z in r.data:
                if z:
                    current_quant = len(z.data)
                    ho_ret_quant += current_quant
                    h2.append({'offset': current_offset, 'quant': current_quant})
                    prev_offset = current_offset
                    current_offset += current_quant * DATA2.sizeof()
                else:
                    h2.append({'offset': prev_offset, 'quant': 0})
        header['HoldOffReticlesSize'] = ho_ret_quant * DATA2.sizeof()

        header['OffsetBaseReticles'] = current_offset
        bs_ret_quant = 0
        for r in bs_ret:
            for z in r.data:
                if z:
                    current_quant = len(z.data)
                    bs_ret_quant += current_quant
                    h2.append({'offset': current_offset, 'quant': current_quant})
                    prev_offset = current_offset
                    current_offset += current_quant * DATA2.sizeof()
                else:
                    h2.append({'offset': prev_offset, 'quant': 0})
        header['BaseReticlesSize'] = bs_ret_quant * DATA2.sizeof()

        header['OffsetLrfReticles'] = current_offset
        lrf_ret_quant = 0
        for r in lrf_ret:
            for z in r.data:
                if z:
                    current_quant = len(z.data)
                    lrf_ret_quant += current_quant
                    h2.append({'offset': current_offset, 'quant': current_quant})
                    prev_offset = current_offset
                    current_offset += current_quant * DATA2.sizeof()
                else:
                    h2.append({'offset': prev_offset, 'quant': 0})
        header['LrfReticlesSize'] = lrf_ret_quant * DATA2.sizeof()

        header['SizeOfAllDataPXL2'] = start_offset + (
                sm_ret_quant + ho_ret_quant + bs_ret_quant + lrf_ret_quant) * DATA2.sizeof()

        data2 = []
        for r in sm_ret:
            for z in r.data:
                if z:
                    data2.append(z.data)

        for r in ho_ret:
            for z in r.data:
                if z:
                    data2.append(z.data)

        for r in bs_ret:
            for z in r.data:
                if z:
                    data2.append(z.data)

        for r in lrf_ret:
            for z in r.data:
                if z:
                    data2.append(z.data)

        ret.update({'header': header})
        ret.update({'headers2': h2})
        ret.update({'data2': data2})

        return ret

    @staticmethod
    def build(data):
        h = HEADER.build(data['header'])
        h2 = bytes()
        d2 = bytes()
        for i in data['headers2']:
            h2 += HEADER2.build(i)
        for i in data['data2']:
            for j in i:
                d2 += DATA2.build({'x': j[2], 'y': j[1], 'q': j[0]})
        filedata = h + h2 + d2
        return filedata

    @staticmethod
    def parse(filename):
        with open(filename, 'rb') as fp:
            data = fp.read()
            header = HEADER.parse(data)

            headers_2 = []
            for i in range(header.SmallReticlesCount):
                for j in range(1, 5):
                    headers_2.append(f'sm_ret_z{j}[{i}]' / HEADER2)

            for i in range(header.HoldOffReticlesCount):
                for j in range(1, 5):
                    headers_2.append(f'ho_ret_z{j}[{i}]' / HEADER2)

            for i in range(header.BaseReticlesCount):
                for j in range(1, 5):
                    headers_2.append(f'bs_ret_z{j}[{i}]' / HEADER2)

            for i in range(header.LrfReticlesCount):
                for j in range(1, 5):
                    headers_2.append(f'lrf_ret_z{j}[{i}]' / HEADER2)

            HEADER_H2 = Struct('header' / HEADER, *headers_2)
            header_h2: Container = HEADER_H2.parse(data)

            reticle_2 = []
            for i in range(header.SmallReticlesCount):
                for j in range(1, 5):
                    for k in range(header_h2[f'sm_ret_z{j}[{i}]']['quant']):
                        reticle_2.append(f'small_ret_{i}[{k}]' / DATA2)

            for i in range(header.HoldOffReticlesCount):
                for j in range(1, 5):
                    for k in range(header_h2[f'ho_ret_z{j}[{i}]']['quant']):
                        reticle_2.append(f'ho_ret{i}[{k}]' / DATA2)

            for i in range(header.BaseReticlesCount):
                for j in range(1, 5):
                    for k in range(header_h2[f'bs_ret_z{j}[{i}]']['quant']):
                        if header_h2[f'bs_ret_z{j}[{i}]'].offset != header_h2[f'bs_ret_z1[{i}]'].offset:
                            reticle_2.append(f'base_ret{i}[{k}]' / DATA2)

            for i in range(header.LrfReticlesCount):
                for j in range(1, 5):
                    for k in range(header_h2[f'lrf_ret_z{j}[{i}]']['quant']):
                        reticle_2.append(f'lrf_ret{i}[{k}]' / DATA2)

            RETICLE_H2_D2 = Struct('header' / HEADER_H2, *reticle_2)
            reticle_h2_d2 = RETICLE_H2_D2.parse(data)

            # print(dict(reticle_h2_d2.header))

            # point0 = reticle_h2_d2['small_ret_0[0]']
            # point1 = reticle_h2_d2['small_ret_0[1]']
            # point0_bytes = point0.to_bytes(4, 'little')
            # point1_bytes = point1.to_bytes(4, 'little')
            #
            # p_struct = ByteSwapped(BitStruct(
            #     'x' / BitsInteger(12),
            #     'y' / BitsInteger(10),
            #     'q' / BitsInteger(10),
            # ))
            #
            # print(print(point0_bytes), p_struct.parse(point0_bytes))
            # print(print(point1_bytes), p_struct.parse(point1_bytes))

# ret0 = [ImgMap(QImage(f'reticle_templates/small.bmp'))]

SMALL_RETS = [
    Reticle4z(ImgMap(QImage(f'reticle_templates/small.bmp')))
]

LRF_RETS = [
    Reticle4z(ImgMap(QImage('reticle_templates/lrf1.bmp'))),
    Reticle4z(ImgMap(QImage('reticle_templates/lrf2.bmp'))),
    Reticle4z(ImgMap(QImage('reticle_templates/lrf3.bmp')))
]

if __name__ == '__main__':

    ret1 = [ImgMap(QImage(f'_1_7x1_7_z1.bmp'))]

    ret2 = []
    ret3 = []
    ret4 = []
    ret5 = []
    ret6 = []

    for i in range(1, 5):
        ret2.append(ImgMap(QImage(f'3 MIL-R_1_7x1_7_z{i}.bmp')))

    for i in range(1, 5):
        ret3.append(ImgMap(QImage(f'MIL-XT_1_7x1_7_z{i}.bmp')))

    for i in range(1, 5):
        ret4.append(ImgMap(QImage(f'MRAD_1_7x1_7_z{i}.bmp')))

    for i in range(1, 5):
        ret5.append(ImgMap(QImage(f'MSR2_1_7x1_7_z{i}.bmp')))

    for i in range(1, 5):
        ret6.append(ImgMap(QImage(f'____1_7x1_7_z{i}.bmp')))

    BASE_RETS = [
        Reticle4z(*ret1),
        Reticle4z(*ret2),
        Reticle4z(*ret3),
        Reticle4z(*ret4),
        Reticle4z(*ret5),
        Reticle4z(*ret6),
    ]

    new_dump = PXL4.dump(SMALL_RETS, [], BASE_RETS, LRF_RETS)
    file_data = PXL4.build(new_dump)
