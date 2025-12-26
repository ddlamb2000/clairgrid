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
        self.display_string = ""
        self.display_string = ' | '.join([self.values[column.index] for column in grid.columns if column.display])

    def __repr__(self):
        return f"Row({self.uuid=}, {self.display_string=})"

    def to_json(self):
        result = BaseModel.to_json(self)
        if self.values: result['values'] = self.values
        if self.display_string: result['displayString'] = self.display_string
        return result
