from construct import Struct, Rebuild, len_, this, Float16l, Byte, Container


# VText = Struct(
#     chcount=Rebuild(Int8ul, len_(this.chars)),
#     chars=Byte[this.chcount]
# )
#
# VLayer = Struct(
#     t=Byte,
#     pen=Byte,
#     p1=Float16l[2],
#     p2=Float16l[2],
#     step=Float16l,
#     text=VText
# )
#
# VTemplate = Struct(
#     lcount=Rebuild(Int8ul, len_(this.layers)),
#     layers=VLayer[this.lcount]
# )
#
# VTemplateStack = Struct(
#     tcount=Rebuild(Int8ul, len_(this.templates)),
#     templates=VTemplate[this.tcount]
# )

VTemplateStack = Struct(
    tcount=Rebuild(Byte, len_(this.templates)),
    templates=Struct(
        lcount=Rebuild(Byte, len_(this.layers)),
        layers=Struct(
            t=Byte,
            pen=Byte,
            p1=Float16l[2],
            p2=Float16l[2],
            step=Float16l,
            text=Struct(
                chcount=Rebuild(Byte, len_(this.chars)),
                chars=Byte[this.chcount]
            )
        )[this.lcount]
    )[this.tcount]
)


class VRetStack:

    @staticmethod
    def build(vect_reticles: list):
        templates = []
        for reticle in vect_reticles:
            layers = []
            for layer in reticle:
                layer['text'] = {'chars': layer['text'].encode('utf-8') if layer['text'] else b'\FF'}
                layers.append(layer)
            templates.append({'layers': layers})

        obj = dict(templates=templates)
        return VTemplateStack.build(obj)

    @staticmethod
    def parse(obj: [bytes, bytearray]):
        vect_reticles = []
        templates: Container = VTemplateStack.parse(obj).templates
        for reticle in templates:
            layers = []
            for layer in reticle.layers:
                layer = dict(layer)
                layer['p1'] = list(layer['p1'])
                layer['p2'] = list(layer['p2'])
                layer['text'] = "".join([chr(ch) for ch in layer['text']['chars']])
                layer.pop('_io')
                layers.append(layer)
            vect_reticles.append(layers)
        return vect_reticles

    @staticmethod
    def save(vect_reticles: list, file_path):
        # with open('../vector_templates/packed.bin', 'wb') as fp:
        ret = VRetStack.build(vect_reticles)
        with open(f'{file_path}.abcv', 'wb') as fp:
            fp.write(ret)

    @staticmethod
    def open(filename):
        with open(f'{filename}.abcv', 'rb') as fp:
            data = fp.read()
            return VRetStack.parse(data)


if __name__ == '__main__':
    pass
