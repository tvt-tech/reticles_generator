from construct import Struct, ByteSwapped, BitStruct, Float16l, Int8ul, BitsInteger



ArcherVectorReticle = Struct(
    header=BitStruct(
        t=BitsInteger(3),
        fill=BitsInteger(1),
        pen=BitsInteger(2),
        mode=BitsInteger(2)
    ),
    x0=Float16l,
    x1=Float16l,
    y0=Float16l,
    y1=Float16l,
    step=Float16l
)
