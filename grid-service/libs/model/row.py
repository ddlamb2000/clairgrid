'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

import json

class Row():
    def __init__(self, uuid, created = None, created_by = None, updated = None, updated_by = None):
        self.uuid = str(uuid)
        self.created = created
        self.created_by = created_by
        self.updated = updated
        self.updated_by = updated_by

    def __repr__(self):
        return f"Row(uuid={self.uuid})"

    def to_json(self):
        result = { 'uuid': self.uuid }
        if self.created: result['created'] = self.created
        if self.created_by: result['created_by'] = self.created_by
        if self.updated: result['updated'] = self.updated
        if self.updated_by: result['updated_by'] = self.updated_by
        return result
