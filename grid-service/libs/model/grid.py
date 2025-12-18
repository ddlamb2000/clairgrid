'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

import json

class Grid():
    def __init__(self, uuid, name = None, description = None, created = None, created_by = None, updated = None, updated_by = None):
        self.uuid = str(uuid)
        self.name = name
        self.description = description
        self.created = created
        self.created_by = created_by
        self.updated = updated
        self.updated_by = updated_by

    def to_json(self):
        result = {
            'uuid': self.uuid,
        }
        if self.name: result['name'] = self.name
        if self.description: result['description'] = self.description
        if self.created: result['created'] = self.created
        if self.created_by: result['created_by'] = self.created_by
        if self.updated: result['updated'] = self.updated
        if self.updated_by: result['updated_by'] = self.updated_by
        return json.dumps(result)
