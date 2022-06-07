from .cross_edit import CrossEdit
from .dot_edit import DotEdit
from .ruler_edit import RulerEdit
from .line_edit import LineEdit
from .text_edit import TextEdit
DIALOGS = {
    'cross': CrossEdit,
    'dot': DotEdit,
    'hruler': RulerEdit,
    'vruler': RulerEdit,
    'line': LineEdit,
    'text': TextEdit
}
