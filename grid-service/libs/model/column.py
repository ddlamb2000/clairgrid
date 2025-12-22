'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

from ..metadata import SystemIds

class Column():
    def __init__(self, uuid, index, order = None, name = None, typeUuid = None, dbColumn = None, partition = None):
        self.uuid = str(uuid)
        self.index = index
        self.order = order
        self.name = name
        self.typeUuid = str(typeUuid)
        self.dbColumn = dbColumn
        self.partition = partition
        if self.typeUuid == SystemIds.IntColumnType:
            self.dbTable = "ints"
        elif self.typeUuid == SystemIds.ReferenceColumnType:
            self.dbTable = "relationships"
        else:
            self.dbTable = "texts"
    def __repr__(self):
        return f"Column({self.uuid=}, {self.index=}, {self.order=}, {self.name=}, {self.typeUuid=} {self.dbColumn=} {self.partition=})"

    def to_json(self):
        result = { 'uuid': self.uuid }
        result['index'] = self.index
        result['order'] = self.order
        result['name'] = self.name
        result['dbTable'] = self.dbTable
        result['dbColumn'] = self.dbColumn
        result['partition'] = self.partition
        if self.typeUuid: result['typeUuid'] = str(self.typeUuid)
        return result
