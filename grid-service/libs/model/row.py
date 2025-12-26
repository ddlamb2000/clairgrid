'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

from .base import BaseModel

class Row(BaseModel):
    def __init__(self, grid, uuid, revision = 1, values = None):
        BaseModel.__init__(self, uuid, revision)
        self.values = values
        self._set_display_string(grid)

    def _set_display_string(self, grid):
        self.displayString = ""
        self.displayString = ' | '.join([self.values[column.index] for column in grid.columns if column.display])

    def __repr__(self):
        return f"Row({self.uuid=}, {self.displayString=})"

    def to_json(self):
        result = BaseModel.to_json(self)
        if self.values: result['values'] = self.values
        if self.displayString: result['displayString'] = self.displayString
        return result
