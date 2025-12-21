'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

import json

class Column():
    def __init__(self, uuid, name = None, description = None):
        self.uuid = str(uuid)
        self.name = name
        self.description = description

    def __repr__(self):
        return f"Column(uuid={self.uuid}, name={self.name}, description={self.description})"

    def to_json(self):
        result = { 'uuid': self.uuid }
        if self.name: result['name'] = self.name
        if self.description: result['description'] = self.description
        return result
