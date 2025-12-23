'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

from ..metadata import SystemIds

class Column():
    def __init__(self, uuid, index, order, name, typeUuid, columnIndex):
        self.uuid = str(uuid)
        self.index = index
        self.order = order
        self.name = name
        self.typeUuid = str(typeUuid)
        self.columnIndex = columnIndex
        self._set_db_columns()

    def _set_db_columns(self):
        self.partition = self.columnIndex // 10
        if self.typeUuid == SystemIds.IntColumnType:
            self.dbTable = "ints"
            self.dbColumn = "int" + str(self.columnIndex % 10)
        elif self.typeUuid == SystemIds.ReferenceColumnType:
            self.dbTable = "relationships"
            self.dbColumn = "toUuid" + str(self.columnIndex % 10)
        else:
            self.dbTable = "texts"
            self.dbColumn = "text" + str(self.columnIndex % 10)
    
    def __repr__(self):
        return f"Column({self.uuid=}, {self.index=}, {self.order=}, {self.name=}, {self.typeUuid=} {self.dbColumn=} {self.columnIndex=} {self.partition=})"

    def to_json(self):
        result = { 'uuid': self.uuid }
        result['index'] = self.index
        result['order'] = self.order
        result['name'] = self.name
        result['dbTable'] = self.dbTable
        result['dbColumn'] = self.dbColumn
        result['columnIndex'] = self.columnIndex
        result['partition'] = self.partition
        if self.typeUuid: result['typeUuid'] = str(self.typeUuid)
        return result
