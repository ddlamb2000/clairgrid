'''  
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the UUIDs for the clairgrid database.
'''

class SystemIdsMapping:
    def __init__(self):
        self._map = {
            "Grids": "f35ef7de-66e7-4e51-9a09-6ff8667da8f7",
            "GridColumnName": "e9e4a415-c31e-4383-ae70-18949d6ec692",
            "GridColumnDesc": "bc1c489d-40c3-441c-9257-c8717be290cd",
            "GridColumnColumns": "e91060d9-2887-424e-b8a1-72650cdaafb3",
            "Users": "018803e1-b4bf-42fa-b58f-ac5faaeeb0c2",
            "Columns": "533b6862-add3-4fef-8f93-20a17aaaaf5a",
            "ColumnColumnOrder": "808963d8-dced-4640-8310-00bda0c5faf4",
            "ColumnColumnName": "a5194e16-415e-45fd-a603-b5db45d13d7d",
            "Migrations": "18414786-31cb-47fd-bd18-fa474099bd94",
            "ColumnTypes": "2114a6ae-013c-4bb1-be6e-3ee875ae517f",
            "RootUser": "3a33485c-7683-4482-aa5d-0aa51e58d79d"
        }
        self._inverse_map = {v: k for k, v in self._map.items()}

    def __getattr__(self, name):
        if name in self._map:
            return self._map[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def get_name(self, uuid):
        return self._inverse_map.get(str(uuid))

SystemIds = SystemIdsMapping()

ActionInitialization = "init"
ActionHeartbeat = "heartbeat"
ActionAuthentication = "authentication"
ActionLoad = "load"
ActionChangeGrid = "change"
ActionLocateGrid = "locate"
ActionPrompt = "prompt"

SuccessStatus = "success"
FailedStatus = "failed"