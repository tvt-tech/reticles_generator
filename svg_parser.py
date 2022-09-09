from enum import IntEnum

import bs4
from PyQt5.QtCore import QRectF


def read_template():
    with open('test_scene.svg', 'r') as fp:
        svg_data = fp.read()

    soup = bs4.BeautifulSoup(svg_data, features="xml")

    view_box = QRectF(*[float(i) for i in soup.find('svg')['viewBox'].split()])
    x0, y0, = view_box.width() / 2, view_box.height() / 2

    rects = soup.find_all('rect')
    lines = soup.find_all('polyline')
    ellipses = soup.find_all('ellipse')
    circles = soup.find_all('circle')

    template = []

    class ItemType(IntEnum):
        Point = 1
        Line = 2
        Rect = 3
        Ellipse = 4
        Circle = 5
        Polygon = 6
        Text = 7

    for item in rects:
        props = item.findParent()
        print(item)
        x = (float(item['x']) - x0) / 20 - 0.05
        y = (float(item['y']) - y0) / 20 - 0.05
        w = float(item['width']) / 20
        h = float(item['height']) / 20
        template.append({
            't': ItemType.Rect,
            'mode': 'pt',
            'p1': [x, y],
            'p2': [x + w, y + h],
            'pen': 1,
        })

    for item in lines:
        props = item.findParent()
        p1, p2 = item['points'].split()
        p1x, p1y = [float(i) for i in p1.split(',')]
        p2x, p2y = [float(i) for i in p2.split(',')]

        template.append({
            't': ItemType.Line,
            'mode': 'pt',
            'p1': [(p1x - x0) / 20 - 0.05, (p1y - y0) / 20 - 0.05],
            'p2': [(p2x - x0) / 20 - 0.05, (p2y - y0) / 20 - 0.05],
            'pen': 1,
        })
    #
    for item in circles:
        props = item.findParent()

        cx = (float(item['cx']) - x0) / 20 - 0.05
        cy = (float(item['cy']) - y0) / 20 - 0.05
        r = float(item['r']) / 20

        template.append({
            't': ItemType.Circle,
            'mode': 'pt',
            'p': [cx, cy],
            'r': r,
            'pen': 1,
        })


    for item in ellipses:
        props = item.findParent()

        cx = (float(item['cx']) - x0) / 20 - 0.05
        cy = (float(item['cy']) - y0) / 20 - 0.05
        rx = float(item['rx']) / 20
        ry = float(item['ry']) / 20

        if rx == ry:
            template.append({
                't': ItemType.Circle,
                'mode': 'pt',
                'p': [cx, cy],
                'r': rx,
                'pen': 1,
            })
        else:
            template.append({
                't': ItemType.Ellipse,
                'mode': 'pt',
                'p1': [cx - rx, cy - ry],
                'p2': [cx + rx, cy + ry],
                'pen': 1,
            })

    return template


if __name__ == '__main__':
    from pprint import pprint

    ret = read_template()
    pprint(ret)
