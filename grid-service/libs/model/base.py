'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

class BaseModel:
    def __init__(self, uuid, revision = 0):
        self.uuid = uuid
        self.revision = revision

    def to_json(self):
        result = {'uuid': str(self.uuid)}
        if self.revision: result['revision'] = int(self.revision)
        return result
