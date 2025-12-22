'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

from .base import BaseModel

class Grid(BaseModel):
    def __init__(self, uuid, name = None, description = None, created = None, created_by = None, updated = None, updated_by = None):
        BaseModel.__init__(self, uuid, created, created_by, updated, updated_by)
        self.name = name
        self.description = description
        self.columns = []

    def __repr__(self):
        return f"Grid({self.uuid=}, {self.name=})"

    def to_json(self):
        print(f"Grid.to_json({self.uuid=}, {self.name=}, {self.description=}, {self.columns=})")
        result = BaseModel.to_json(self)
        print(f"Grid.to_json result: {result}")
        if self.name: result['name'] = self.name
        if self.description: result['description'] = self.description   
        result['columns'] = [column.to_json() for column in self.columns]
        print(f"Grid.to_json result: {result}")
        return result
