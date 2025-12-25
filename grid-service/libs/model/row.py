'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

from .base import BaseModel

class Row(BaseModel):
    def __init__(self, uuid, revision = 1, values = None):
        BaseModel.__init__(self, uuid, revision)
        self.values = values

    def __repr__(self):
        return f"Row({self.uuid=})"

    def to_json(self):
        result = BaseModel.to_json(self)
        if self.values: result['values'] = self.values
        return result
