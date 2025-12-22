'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

class BaseModel:
    def __init__(self, uuid, created=None, created_by=None, updated=None, updated_by=None):
        self.uuid = uuid
        self.created = created
        self.created_by = created_by
        self.updated = updated
        self.updated_by = updated_by

    def to_json(self):
        result = {'uuid': str(self.uuid)}
        if self.created: result['created'] = str(self.created)
        if self.created_by: result['created_by'] = str(self.created_by)
        if self.updated: result['updated'] = str(self.updated)
        if self.updated_by: result['updated_by'] = str(self.updated_by)
        return result
