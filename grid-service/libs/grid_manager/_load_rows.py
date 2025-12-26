from typing import LiteralString

from ..model.row import Row, ReferenceRow
from ..utils.decorators import echo
from ..metadata import SystemIds

@echo
def _load_rows(self, grid):
    print(f"Loading rows for grid {grid.uuid}")
    self.allRows[grid.uuid] = { } # dictionary of rows by uuid
    dbSelectClauses = [column.dbSelectClause for column in grid.columns]
    dbSelectColumns = (',\n' if len(dbSelectClauses) > 1 else '') + ',\n'.join(dbSelectClauses)
    dbJoinClauses = ''.join(list[LiteralString](dict.fromkeys([column.dbJoinClause for column in grid.columns])))
    try:
        result = self.db_manager.select_all('''
            -- Load rows
            SELECT rows.uuid,
            rows.revision''' + dbSelectColumns + '''
            FROM rows''' +  dbJoinClauses + '''
            -- Filter by grid uuid and enabled
            WHERE rows.gridUuid = ''' + f"'{grid.uuid}' -- {grid.name}" + '''
            AND rows.enabled = true
        '''
        )
        indexData = 2
        for item in result:
            uuid, revision = item[0], item[1]
            existingRow = self.allRows[grid.uuid].get(uuid)
            newItem = []
            for column in grid.columns:
                if column.typeUuid and str(column.typeUuid) == SystemIds.ReferenceColumnType:
                    if column.referenceGrid and item[indexData+column.fieldIndex]:
                        referenceUuid = item[indexData+column.fieldIndex]
                        referenceValues = item[indexData+column.fieldIndex+1:indexData+column.fieldIndex+column.numberOfFields]
                        referenceRow = ReferenceRow(column.referenceGrid, uuid =referenceUuid, values = referenceValues)
                        if existingRow:
                            existingRow.values[column.index] += [referenceRow.to_json()]
                        else:
                            newItem.append([referenceRow.to_json()])
                    else:
                        if not existingRow:
                            newItem.append([])
                else:
                    if not existingRow:
                        newItem.append(item[indexData+column.fieldIndex])
            if not existingRow:
                row = Row(grid, uuid = uuid, revision = revision, values = newItem)
                self.allRows[grid.uuid][uuid] = row
                print(f"New row: {row}")
        print(f"Rows loaded: {len(self.allRows[grid.uuid])}")
    except Exception as e:
        print(f"❌ Error loading rows for grid {grid.uuid}: {e}")
        raise e

