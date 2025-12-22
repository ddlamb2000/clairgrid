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
            "Columns": "533b6862-add3-4fef-8f93-20a17aaaaf5a",
            "ColumnColumnOrder": "808963d8-dced-4640-8310-00bda0c5faf4",
            "ColumnColumnName": "a5194e16-415e-45fd-a603-b5db45d13d7d",
            "ColumnColumnColumnType": "87245ad9-323a-4946-a0a7-a4082beae745",
            "ColumnColumnDbName": "bb79b1f3-966a-4084-a72e-814c203bfa70",
            "ColumnColumnPartition": "0e3d5511-bc1c-4dfd-98ce-9ce369e05908",
            "ColumnTypes": "2114a6ae-013c-4bb1-be6e-3ee875ae517f",
            "ColumnTypeColumnName": "9da0e49f-528c-4081-bc07-3c32497857ff",
            "ColumnTypeColumnDesc": "5a9eba36-7601-4627-be8e-50cf027d9ad8",
            "TextColumnType": "65f3c258-fb1e-4f8b-96ca-f790e70d29c1",
            "IntColumnType": "8c28d527-66f4-481c-902e-ac1e65a8abb0",
            "ReferenceColumnType": "c8b16312-d4f0-40a5-aa04-c0bc1350fea7",
            "PasswordColumnType": "5f038b21-d9a4-45fc-aa3f-fc405342c287",
            "BooleanColumnType": "6e205ebd-6567-44dc-8fd4-ef6ad281ab40",
            "UuidColumnType": "d7c004ff-da5e-4a18-9520-cd42b2847508",
            "DateColumnType": "28ac131f-f04b-4350-b464-3db4f8920597",
            "Users": "018803e1-b4bf-42fa-b58f-ac5faaeeb0c2",
            "UserColumnId": "927a3228-f83d-4235-b70a-e0d3c0881598",
            "UserColumnFirstName": "83762777-8bd3-4f7c-a060-e7ceebfebe1c",
            "UserColumnLastName": "afe9d02b-0313-44d7-965f-e84a7047e047",
            "UserColumnPassword": "51270c2c-704d-4ae7-9fdb-08fd6f0c9065",
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