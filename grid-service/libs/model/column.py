'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

class Column():
    def __init__(self, uuid, order = None, name = None, type = None):
        self.uuid = str(uuid)
        self.order = order
        self.name = name
        self.type = type
    def __repr__(self):
        return f"Column({self.uuid=}, {self.order=}, {self.name=})"

    def to_json(self):
        result = { 'uuid': self.uuid }
        if self.order: result['order'] = self.order
        if self.name: result['name'] = self.name
        if self.type: result['type'] = self.type
        return result
