from .. import metadata
from ..model.column import Column

def _load_columns(self, grid):
    try:
        result = self.db_manager.select_all('''
            SELECT rows.uuid,
                    texts.text0 as order, 
                    texts.text1 as name,
                    rel2.toUuid0 as typeUuid,
                    rel2.toUuid1 as referenceGridUuid,
                    ints.int0 as columnIndex
            FROM relationships rel1
            LEFT OUTER JOIN rows ON rows.gridUuid = %s AND rows.uuid = rel1.toUuid0 AND rows.enabled = true
            LEFT OUTER JOIN texts ON texts.uuid = rows.uuid AND texts.partition = 0
            LEFT OUTER JOIN relationships rel2 ON rel2.fromUuid = rows.uuid AND rel2.partition = 0
            LEFT OUTER JOIN ints ON ints.uuid = rows.uuid AND ints.partition = 0
            WHERE rel1.fromUuid = %s AND rel1.partition = 0
            ORDER BY texts.text0
        ''', (metadata.SystemIds.Columns, grid.uuid)
        )
        index = 0
        for item in result: 
            column = Column(item[0], index, order = item[1], name = item[2], typeUuid = item[3], referenceGridUuid = item[4], columnIndex = item[5])
            index += 1
            print(f"New column: {column}")
            grid.columns.append(column)
    except Exception as e:
        print(f"❌ Error loading columns for grid {grid.uuid}: {e}")
        raise e

