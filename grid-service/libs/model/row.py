'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

from .base import BaseModel

class Row(BaseModel):
    def __init__(self, grid, uuid, revision = 0, values = None):
        BaseModel.__init__(self, uuid, revision)
        self.values = values
        self._set_display_string(grid)

    def _set_display_string(self, grid):
        if self.values:
            self.displayString = ' | '.join([self.values[column.index] for column in grid.columns if column.display])
        else:
            self.displayString = ""

    def __repr__(self):
        return f"Row({self.uuid}, {self.displayString})"

    def to_json(self):
        result = BaseModel.to_json(self)
        if self.values: result['values'] = self.values
        if self.displayString: result['displayString'] = self.displayString
        return result

class ReferenceRow(Row):
    def __init__(self, grid, uuid, values = None):
        Row.__init__(self, grid, uuid, values = values)

    def _set_display_string(self, grid):
        if self.values:
            self.displayString = ' | '.join([str(value) for value in self.values])
        else:
            self.displayString = ""

    def __repr__(self):
        return f"ReferenceRow({self.uuid}, {self.displayString})"

    def to_json(self):
        result = BaseModel.to_json(self)
        if self.displayString: result['displayString'] = self.displayString
        return result
