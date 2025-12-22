'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

'''

class Column():
    def __init__(self, uuid, order = None, name = None, typeUuid = None, dbName = None, partition = None):
        self.uuid = str(uuid)
        self.order = order
        self.name = name
        self.typeUuid = typeUuid
        self.dbName = dbName
        self.partition = partition
    def __repr__(self):
        return f"Column({self.uuid=}, {self.order=}, {self.name=}, {self.typeUuid=} {self.dbName=} {self.partition=})"

    def to_json(self):
        result = { 'uuid': self.uuid }
        result['order'] = self.order
        result['name'] = self.name
        result['dbName'] = self.dbName
        result['partition'] = self.partition
        if self.typeUuid: result['typeUuid'] = str(self.typeUuid)
        return result
