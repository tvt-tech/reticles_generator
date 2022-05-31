from PyQt5 import QtWidgets, QtGui, QtCore
from ret_edit import CrossEdit, DotEdit, RulerEdit


class ReticleTable(QtWidgets.QTableView):
    def __init__(self):
        super(ReticleTable, self).__init__()
        self.setMinimumWidth(300)
        self.setMaximumWidth(300)
        self.setSelectionBehavior(self.SelectRows)
        header = self.verticalHeader()
        header.setDefaultSectionSize(1)

    def table_clicked(self, index, template, zoom):
        item = template[index.row()]
        if index.column() == 4:
            if item['hide']:
                item['hide'] = False
            else:
                item['hide'] = True

            self.table_model.item(index.row(), 4).setData(item['hide'], QtCore.Qt.DisplayRole)
        min_zoom = item['min_zoom']
        max_zoom = item['max_zoom']
        if zoom < min_zoom:
            return min_zoom
        elif zoom >= max_zoom:
            return max_zoom-1
        else:
            return zoom

    def table_double_clicked(self, index):
        item = self.reticle['template'][index.row()]

        dlg = None

        if -1 < index.column() < 4:
            if item['type'] == 'cross':
                dlg = CrossEdit(item)
            if item['type'] == 'dot':
                dlg = DotEdit(item)
            if item['type'] in ['vruler', 'hruler']:
                dlg = RulerEdit(item)
            if dlg is not None:
                if dlg.exec_():
                    self.reticle['template'][index.row()] = dlg.get_data()
                    self.combo.setItemData(self.combo.currentIndex(), self.reticle)
                    self.load_table()
                    self.draw_layers()
        self.table.selectRow(index.row())
        self.table_clicked(index)

    def load_table(self, template):
        self.table_model = QtGui.QStandardItemModel(self)

        for i, y in enumerate(template):
            self.table_model.setItem(i, 0, QtGui.QStandardItem())
            self.table_model.item(i, 0).setData(y['type'], QtCore.Qt.DisplayRole)
            self.table_model.setItem(i, 1, QtGui.QStandardItem())
            self.table_model.item(i, 1).setData(y['mode'] if 'mode' in y else '', QtCore.Qt.DisplayRole)
            self.table_model.setItem(i, 2, QtGui.QStandardItem())
            self.table_model.item(i, 2).setData(y['min_zoom'], QtCore.Qt.DisplayRole)
            self.table_model.setItem(i, 3, QtGui.QStandardItem())
            self.table_model.item(i, 3).setData(y['max_zoom'], QtCore.Qt.DisplayRole)

            item = QtGui.QStandardItem()
            self.table_model.setItem(i, 4, item)
            if not 'hide' in 'y':
                template[i]['hide'] = False
                y['hide'] = False
            self.table_model.item(i, 4).setData(y['hide'], QtCore.Qt.DisplayRole)

        self.table_model.setHorizontalHeaderLabels(['Type', 'Mode', 'Min zoom', 'Max zoom', 'Hide'])
        self.setModel(self.table_model)
        header = self.horizontalHeader()
        for i in range(header.count()):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)