import json

from construct import Struct, Int8ul, Rebuild, len_, this, BitsInteger, Float16l, BitStruct, Byte
from graphics_view.custom_graphics_item import ItemFlag

# example = [{"t": 8, "step": 1.0, "p1": [0.1, 1.0], "p2": [0.1, 10.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-0.2, 1.0], "p2": [0.1, 10.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-0.3, -5.0], "p2": [0.6, 4.8], "fill": 0},
#            {"t": 1, "step": 1.0, "p1": [0.0, 0.0], "p2": [0.0, 0.0], "fill": 0},
#            {"t": 2, "step": 1.0, "p1": [-10.0, 0.0], "p2": [-0.2, 0.0], "fill": 0},
#            {"t": 2, "step": 1.0, "p1": [0.2, 0.0], "p2": [10.0, 0.0], "fill": 0},
#            {"t": 2, "step": 1.0, "p1": [0.0, -0.2], "p2": [0.0, -5.0], "fill": 0},
#            {"t": 2, "step": 1.0, "p1": [0.0, 0.2], "p2": [0.0, 0.8], "fill": 0},
#            {"t": 2, "step": 1.0, "p1": [0.0, 1.2], "p2": [0.0, 11.0], "fill": 0},
#            {"t": 1, "step": 1.0, "p1": [0.0, 1.0], "p2": [0.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-10.0, -0.3], "p2": [9.0, 0.6], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-9.8, 0.0], "p2": [9.0, 0.15], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-9.6, -0.15], "p2": [9.0, 0.15], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-9.4, -0.15], "p2": [9.0, 0.15], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-9.2, 0.0], "p2": [9.0, 0.15], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, -0.3], "p2": [9.0, 0.6], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [0.4, -0.15], "p2": [9.0, 0.15], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [0.6, -0.15], "p2": [9.0, 0.15], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [0.8, 0.0], "p2": [9.0, 0.15], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [0.2, 0.0], "p2": [9.0, 0.15], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-3.0, 0.95], "p2": [2.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-3.0, 1.05], "p2": [2.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 0.95], "p2": [2.05, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 1.05], "p2": [2.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-3.0, 1.95], "p2": [2.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-3.0, 2.05], "p2": [2.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 1.95], "p2": [2.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 2.05], "p2": [2.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-3.0, 2.95], "p2": [2.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-3.0, 3.05], "p2": [2.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 2.95], "p2": [2.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 3.05], "p2": [2.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 3.95], "p2": [2.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 4.05], "p2": [2.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-3.0, 3.95], "p2": [2.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-3.0, 4.05], "p2": [2.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-4.0, 4.95], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-4.0, 5.05], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 4.95], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 5.05], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 5.95], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 6.05], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-4.0, 5.95], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-4.0, 6.05], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 6.95], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 7.05], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-4.0, 6.95], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-4.0, 7.05], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-4.0, 7.95], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-4.0, 8.05], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 7.95], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 8.05], "p2": [3.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-5.0, 8.95], "p2": [4.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-5.0, 9.05], "p2": [4.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 8.95], "p2": [4.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 9.05], "p2": [4.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-5.0, 9.95], "p2": [4.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-5.0, 10.05], "p2": [4.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 9.95], "p2": [4.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 10.05], "p2": [4.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-5.0, 10.95], "p2": [4.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [-5.0, 11.05], "p2": [4.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 10.95], "p2": [4.0, 0.0], "fill": 0},
#            {"t": 8, "step": 1.0, "p1": [1.0, 11.05], "p2": [4.0, 0.0], "fill": 0}]

with open('../vector_templates/reticle_mil.abcv', 'rb') as fp:
    example1 = json.load(fp)
with open('../vector_templates/reticle_msr.abcv', 'rb') as fp:
    example2 = json.load(fp)

# example = [{'layers': example1}, {'layers': example2}]
example = [example1]

# VLayer = Struct(
#         t=BitsInteger(6),
#         fill=BitsInteger(2),
#         p1=Float16l[2],
#         p2=Float16l[2],
#         step=Float16l,
#     )


VText = Struct(
    chcount=Rebuild(Int8ul, len_(this.chars)),
    chars=Byte[this.chcount]
)

VLayer = Struct(
    t=Byte,
    fill=Byte,
    p1=Float16l[2],
    p2=Float16l[2],
    step=Float16l,
    # text=VText
)

VTemplate = Struct(
    lcount=Rebuild(Int8ul, len_(this.layers)),
    layers=VLayer[this.lcount]
)

VTemplateStack = Struct(
    tcount=Rebuild(Int8ul, len_(this.templates)),
    templates=VTemplate[this.tcount]
)


class VRetStack:
    # def build(self, obj, **contextkw):

    @staticmethod
    def build(vect_reticles: list, **contextkw):
        templates = [{'layers': i} for i in vect_reticles]
        obj = dict(templates=templates)
        return VTemplateStack.build(obj)

    @staticmethod
    def parse(obj: [bytes, bytearray]):
        return VTemplateStack.parse(obj)


ret = VRetStack.build(example)
print(VRetStack.parse(ret))

with open('../vector_templates/packed.bin', 'wb') as fp:
    fp.write(ret)

print(len(ret) / 1000)
print(VLayer.sizeof())

print(ItemFlag.Filled.value)
