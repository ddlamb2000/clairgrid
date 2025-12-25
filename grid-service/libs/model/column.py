'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

from ..metadata import SystemIds

class Column():
    def __init__(self, uuid, index, order, name, typeUuid, referenceGridUuid, columnIndex, display):
        self.uuid = str(uuid)
        self.index = index
        self.order = order
        self.name = name
        self.typeUuid = str(typeUuid)
        self.referenceGridUuid = str(referenceGridUuid)
        self.columnIndex = columnIndex
        self.display = display
        self._set_db_columns()

    def _set_db_columns(self):
        self.partition = self.columnIndex // 10
        if self.typeUuid == SystemIds.IntColumnType:
            self.dbTable = "ints"
            self.dbColumn = f"int{self.columnIndex % 10}"
            self.dbJoinKey = "uuid"
        elif self.typeUuid == SystemIds.ReferenceColumnType:
            self.dbTable = "relationships"
            self.dbColumn = f"toUuid{self.columnIndex % 10}::text"
            self.dbJoinKey = "fromUuid"
        elif self.typeUuid == SystemIds.BooleanColumnType:
            self.dbTable = "booleans"
            self.dbColumn = f"bool{self.columnIndex % 10}"
            self.dbJoinKey = "uuid"
        else:
            self.dbTable = "texts"
            self.dbColumn = f"text{self.columnIndex % 10}"
            self.dbJoinKey = "uuid"
        self.db_select_clause = f"{self.dbTable}_{self.partition}.{self.dbColumn}"
        self.db_join_clause = f"LEFT OUTER JOIN {self.dbTable} {self.dbTable}_{self.partition} ON {self.dbTable}_{self.partition}.{self.dbJoinKey} = rows.uuid AND {self.dbTable}_{self.partition}.partition = {self.partition}"
    
    def __repr__(self):
        return f"Column({self.uuid=}, {self.index=}, {self.order=}, {self.name=}, {self.typeUuid=} {self.dbColumn=} {self.columnIndex=} {self.partition=})"

    def to_json(self):
        result = { 'uuid': str(self.uuid) }
        result['index'] = self.index
        result['order'] = self.order
        result['name'] = self.name
        result['columnIndex'] = self.columnIndex
        if self.display: result['display'] = bool(self.display)
        if self.typeUuid: result['typeUuid'] = str(self.typeUuid)
        if self.referenceGridUuid: result['referenceGridUuid'] = str(self.referenceGridUuid)
        return result
