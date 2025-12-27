from .. import metadata
from ..model.column import Column
from ..utils.decorators import echo
from ..utils.report_exception import report_exception

@echo
def _load_columns(self, grid, loadReferenceGrid = True):
    try:
        result = self.db_manager.select_all('''
            -- Load columns
            SELECT rows.uuid,
                    texts.text0, -- order
                    texts.text1, -- name
                    rel2.toUuid0, -- type uuid
                    rel2.toUuid1, -- reference grid uuid
                    ints.int0, -- column index
                    booleans.bool0 -- display flag
            FROM relationships rel1
            -- Join rows to get column uuid
            LEFT OUTER JOIN rows ON rows.gridUuid = ''' + f"'{metadata.SystemIds.Columns}' -- Columns" + '''
            AND rows.uuid = rel1.toUuid0 AND rows.enabled = true
            -- Join texts to get order and name
            LEFT OUTER JOIN texts ON texts.uuid = rows.uuid AND texts.partition = 0
            -- Join relationships to get type uuid and reference grid uuid
            LEFT OUTER JOIN relationships rel2 ON rel2.fromUuid = rows.uuid AND rel2.partition = 0
            -- Join ints to get column index
            LEFT OUTER JOIN ints ON ints.uuid = rows.uuid AND ints.partition = 0
            -- Join booleans to get display flag
            LEFT OUTER JOIN booleans ON booleans.uuid = rows.uuid AND booleans.partition = 0
            -- Filter by grid uuid and enabled
            WHERE rel1.fromUuid = ''' + f"'{grid.uuid}' -- {grid.name}" + '''
            AND rel1.partition = 0
            ORDER BY texts.text0
        '''
        )
        index = 0
        fieldIndex = 0
        for item in result: 
            referenceGridUuid = item[4]
            referenceGrid = _get_reference_grid(self, referenceGridUuid, loadReferenceGrid)
            column = Column(item[0],
                            index,
                            fieldIndex,
                            order = item[1],
                            name = item[2],
                            typeUuid = item[3],
                            referenceGridUuid = referenceGridUuid,
                            referenceGrid = referenceGrid,
                            columnIndex = item[5],
                            display = item[6])
            index += 1
            fieldIndex += column.numberOfFields
            print(f"New column: {column}")
            grid.columns.append(column)
    except Exception as e:
        report_exception(e, f"Error loading columns for grid {grid.uuid}")
        raise e

def _get_reference_grid(self, referenceGridUuid, loadReferenceGrid):
    if referenceGridUuid and loadReferenceGrid:
        print(f"Loading reference grid: {referenceGridUuid}")
        referenceGrid = self.allGrids.get(referenceGridUuid)
        if not referenceGrid:
            print(f"Reference grid not found in memory, loading from database")
            referenceGrid = self._load_grid(referenceGridUuid, loadReferenceGrid = False)
            if referenceGrid:
                self.allGrids[referenceGridUuid] = referenceGrid
                print(f"Reference grid loaded: {referenceGridUuid}")
            else:
                print(f"❌ Error loading reference grid {referenceGridUuid}")
                raise Exception(f"Error loading reference grid {referenceGridUuid}")
        return referenceGrid
    else:
        return None
