'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

from ..metadata import SystemIds

class Column():
    def __init__(self, uuid, index, order, name, typeUuid, referenceGridUuid = None, referenceGrid = None, columnIndex = 0, display = False):
        self.uuid = str(uuid)
        self.index = index
        self.order = order
        self.name = name
        self.typeUuid = str(typeUuid)
        self.referenceGridUuid = str(referenceGridUuid)
        self.referenceGrid = referenceGrid
        self.columnIndex = columnIndex
        self.display = display
        self._set_db_columns()
        self._set_db_clauses()

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

    def _set_db_reference_columns(self, referencedColumnIndex):
        self.dbReferenceColumn = f"{self.dbTable}_{self.partition}_{referencedColumnIndex}.text{self.columnIndex % 10}"
        self.dbReferenceJoinKey = "uuid"

    def _set_db_reference_clauses(self, referencedColumnIndex):
        self.dbSelectReferenceClause = f"{self.dbTable}_{self.partition}.{self.dbColumn}"
        self.dbJoinReferenceClause = f"\n-- Join {self.dbTable}\n" + \
                                f"LEFT OUTER JOIN {self.dbTable} {self.dbTable}_{self.partition}_{referencedColumnIndex}\n" + \
                                f"ON {self.dbTable}_{self.partition}_{referencedColumnIndex}.{self.dbJoinKey} = ref_rows_{referencedColumnIndex}.uuid\n" + \
                                f"AND {self.dbTable}_{self.partition}_{referencedColumnIndex}.partition = {self.partition}"            

    def _set_db_clauses(self):
        self.numberOfFields = 1
        if self.typeUuid == SystemIds.ReferenceColumnType and self.referenceGrid:
            displayColumns = [column for column in self.referenceGrid.columns if column.dbTable == 'texts' and column.display]

            for column in displayColumns:
                column._set_db_reference_columns(self.columnIndex)
                column._set_db_reference_clauses(self.columnIndex)

            dbSelectReferenceClauses = [column.dbReferenceColumn for column in displayColumns]
            dbSelectReferenceColumns = (',\n' if len(dbSelectReferenceClauses) > 0 else '') + ',\n'.join(dbSelectReferenceClauses)
            dbJoinReferenceClauses = ''.join(list(dict.fromkeys([column.dbJoinReferenceClause for column in displayColumns])))

            self.dbSelectClause = f"{self.dbTable}_{self.partition}.{self.dbColumn}" + dbSelectReferenceColumns
            self.dbJoinClause = f"\n-- Join {self.dbTable} for reference grid {self.referenceGrid.name}\n" + \
                                    f"LEFT OUTER JOIN {self.dbTable} {self.dbTable}_{self.columnIndex}\n" + \
                                    f"ON {self.dbTable}_{self.columnIndex}.{self.dbJoinKey} = rows.uuid\n" + \
                                    f"AND {self.dbTable}_{self.columnIndex}.partition = {self.partition}\n" + \
                                    f"LEFT OUTER JOIN rows ref_rows_{self.columnIndex}\n" + \
                                    f"ON ref_rows_{self.columnIndex}.gridUuid = '{self.referenceGridUuid}' -- {self.referenceGrid.name}\n" + \
                                    f"AND ref_rows_{self.columnIndex}.uuid = {self.dbTable}_{self.columnIndex}.toUuid{self.columnIndex % 10}\n" + \
                                    f"AND ref_rows_{self.columnIndex}.enabled = true" + dbJoinReferenceClauses

            self.numberOfFields += len(displayColumns)
        else:
            self.dbSelectClause = f"{self.dbTable}_{self.partition}.{self.dbColumn}"
            self.dbJoinClause = f"\n-- Join {self.dbTable}\n" + \
                                    f"LEFT OUTER JOIN {self.dbTable} {self.dbTable}_{self.partition}\n" + \
                                    f"ON {self.dbTable}_{self.partition}.{self.dbJoinKey} = rows.uuid\n" + \
                                    f"AND {self.dbTable}_{self.partition}.partition = {self.partition}"            
    
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
        if self.referenceGrid: result['referenceGrid'] = self.referenceGrid.to_json()
        return result
