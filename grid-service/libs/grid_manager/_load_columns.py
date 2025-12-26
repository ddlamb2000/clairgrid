from .. import metadata
from ..model.column import Column
from ..utils.decorators import echo

@echo
def _load_columns(self, grid, load_reference_grid = True):
    try:
        result = self.db_manager.select_all('''
            SELECT rows.uuid,
                    texts.text0 as order, 
                    texts.text1 as name,
                    rel2.toUuid0 as typeUuid,
                    rel2.toUuid1 as referenceGridUuid,
                    ints.int0 as columnIndex,
                    booleans.bool0 as display
            FROM relationships rel1
            LEFT OUTER JOIN rows ON rows.gridUuid = %s AND rows.uuid = rel1.toUuid0 AND rows.enabled = true
            LEFT OUTER JOIN texts ON texts.uuid = rows.uuid AND texts.partition = 0
            LEFT OUTER JOIN relationships rel2 ON rel2.fromUuid = rows.uuid AND rel2.partition = 0
            LEFT OUTER JOIN ints ON ints.uuid = rows.uuid AND ints.partition = 0
            LEFT OUTER JOIN booleans ON booleans.uuid = rows.uuid AND booleans.partition = 0
            WHERE rel1.fromUuid = %s AND rel1.partition = 0
            ORDER BY texts.text0
        ''', (metadata.SystemIds.Columns, grid.uuid)
        )
        index = 0
        for item in result: 
            referenceGridUuid = item[4]
            referenceGrid = _get_reference_grid(self, referenceGridUuid, load_reference_grid)
            column = Column(item[0],
                            index,
                            order = item[1],
                            name = item[2],
                            typeUuid = item[3],
                            referenceGridUuid = referenceGridUuid,
                            referenceGrid = referenceGrid,
                            columnIndex = item[5],
                            display = item[6])
            index += column.number_of_fields
            print(f"New column: {column}")
            grid.columns.append(column)
    except Exception as e:
        print(f"❌ Error loading columns for grid {grid.uuid}: {e}")
        raise e

def _get_reference_grid(self, referenceGridUuid, load_reference_grid):
    if referenceGridUuid and load_reference_grid:
        print(f"Loading reference grid: {referenceGridUuid}")
        referenceGrid = self.all_grids.get(referenceGridUuid)
        if not referenceGrid:
            print(f"Reference grid not found in memory, loading from database")
            referenceGrid = self._load_grid(referenceGridUuid, load_reference_grid = False)
            if referenceGrid:
                self.all_grids[referenceGridUuid] = referenceGrid
                print(f"Reference grid loaded: {referenceGridUuid}")
            else:
                print(f"❌ Error loading reference grid {referenceGridUuid}")
                raise Exception(f"Error loading reference grid {referenceGridUuid}")
        return referenceGrid
    else:
        return None

