from typing import LiteralString

from ..model.row import Row, ReferenceRow
from ..utils.decorators import echo
from ..metadata import SystemIds
from ..utils.report_exception import report_exception

@echo
def _load_rows(self, grid):
    print(f"Loading rows for grid {grid.uuid}")
    self.allRows[str(grid.uuid)] = { } # dictionary of rows by uuid
    dbSelectClauses = [column.dbSelectClause for column in grid.columns]
    dbSelectColumns = (',\n' if len(dbSelectClauses) > 0 else '') + ',\n'.join(dbSelectClauses)
    dbGroupClauses = [column.dbSelectClause for column in grid.columns if column.typeUuid and str(column.typeUuid) != SystemIds.ReferenceColumnType]
    dbGroupColumns = (',\n' if len(dbGroupClauses) > 0 else '') + ',\n'.join(dbGroupClauses)
    dbJoinClauses = ''.join(list[LiteralString](dict.fromkeys([column.dbJoinClause for column in grid.columns])))
    try:
        result = self.db_manager.select_all(
            '''-- Load rows
            SELECT rows.uuid, rows.revision''' + dbSelectColumns + '''
            FROM rows''' +  dbJoinClauses + '''
            -- Filter by grid uuid and enabled
            WHERE rows.gridUuid = ''' + f"'{grid.uuid}' -- {grid.name}" + '''
            AND rows.enabled = true
            GROUP BY rows.uuid, rows.revision''' + dbGroupColumns
        )
        indexData = 2
        for item in result:
            uuid, revision = item[0], item[1]
            newItem = []
            for column in grid.columns:
                if column.typeUuid and str(column.typeUuid) == SystemIds.ReferenceColumnType:
                    references = []
                    if column.referenceGrid and item[indexData+column.fieldIndex]:
                        referenceUuid = item[indexData+column.fieldIndex]
                        referenceValues = item[indexData+column.fieldIndex+1]
                        for (refUuid, value) in zip(referenceUuid.split('||||'), referenceValues.split('||||')):
                            referenceRow = ReferenceRow(column.referenceGrid, uuid =refUuid, values = [value])
                            references += [referenceRow.to_json()]
                    newItem.append(references)
                else:
                    newItem.append(item[indexData+column.fieldIndex])
            row = Row(grid, uuid = uuid, revision = revision, values = newItem)
            self.allRows[str(grid.uuid)][str(uuid)] = row
            print(f"New row: {row}")
        print(f"Rows loaded: {len(self.allRows[str(grid.uuid)])}")
    except Exception as e:
        report_exception(e, f"Error loading rows for grid {str(grid.uuid)}")
        raise e

