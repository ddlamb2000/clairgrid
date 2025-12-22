'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

from .base import BaseModel

class Row(BaseModel):
    def __init__(self, uuid, created = None, created_by = None, updated = None, updated_by = None):
        BaseModel.__init__(self, uuid, created, created_by, updated, updated_by)

    def __repr__(self):
        return f"Row({self.uuid=})"

    def to_json(self):
        return BaseModel.to_json(self)
