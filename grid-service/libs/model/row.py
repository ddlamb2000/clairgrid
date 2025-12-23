'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

from .base import BaseModel

class Row(BaseModel):
    def __init__(self, uuid, created = None, created_by = None, updated = None, updated_by = None, values = None):
        BaseModel.__init__(self, uuid, created, created_by, updated, updated_by)
        self.values = values

    def __repr__(self):
        return f"Row({self.uuid=})"

    def to_json(self):
        result = BaseModel.to_json(self)
        if self.values: result['values'] = self.values
        return result
