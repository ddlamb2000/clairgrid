import uuids

migration_steps = {
    10: "CREATE TABLE migrations ("
			"sequence integer NOT NULL,"
			"statement text NOT NULL,"
			"PRIMARY KEY (sequence)"
		")",

    20: "CREATE EXTENSION IF NOT EXISTS pgcrypto",

    30: "CREATE EXTENSION IF NOT EXISTS vector",
    
    40: "CREATE TABLE rows ("
			"uuid uuid NOT NULL, "
			"gridUuid uuid NOT NULL, "
			"enabled boolean NOT NULL, "
			"revision integer NOT NULL CHECK (revision > 0), "
			"created timestamp with time zone NOT NULL, "
			"createdByUuid uuid NOT NULL, "
			"updated timestamp with time zone NOT NULL, "
			"updatedByuuid uuid NOT NULL, "
			"PRIMARY KEY (uuid),"
			"UNIQUE (uuid)"
		")",

    50: "CREATE TABLE texts ("
			"uuid uuid NOT NULL, "
			"partition integer, "
			"text0 text, "
			"text1 text, "
			"text2 text, "
			"text3 text, "
			"text4 text, "
			"text5 text, "
			"text6 text, "
			"text7 text, "
			"text8 text, "
			"text9 text, "
			"PRIMARY KEY (uuid, partition)"
		")",

    60: "CREATE TABLE ints ("
			"uuid uuid NOT NULL, "
			"partition integer, "
			"int0 integer, "
			"int1 integer, "
			"int2 integer, "
			"int3 integer, "
			"int4 integer, "
			"int5 integer, "
			"int6 integer, "
			"int7 integer, "
			"int8 integer, "
			"int9 integer, "
			"PRIMARY KEY (uuid, partition)"
		")",

    70: "CREATE TABLE relationships ("
			"uuid uuid NOT NULL, "
			"partition integer, "
			"rel0 uuid REFERENCES rows (uuid), "
			"rel1 uuid REFERENCES rows (uuid), "
			"rel2 uuid REFERENCES rows (uuid), "
			"rel3 uuid REFERENCES rows (uuid), "
			"rel4 uuid REFERENCES rows (uuid), "
			"rel5 uuid REFERENCES rows (uuid), "
			"rel6 uuid REFERENCES rows (uuid), "
			"rel7 uuid REFERENCES rows (uuid), "
			"rel8 uuid REFERENCES rows (uuid), "
			"rel9 uuid REFERENCES rows (uuid), "
			"PRIMARY KEY (uuid, partition)"
		")",

	80: "INSERT INTO rows "
			"(uuid, gridUuid, enabled, revision, created, createdByUuid, updated, updatedByuuid) "
			"VALUES ("
			f"'{uuids.UuidGrids}',"
			f"'{uuids.UuidGrids}',"
			"true,"
			"1,"
			"now(),"
			f"'{uuids.UuidRootUser}',"
			"now(),"
			f"'{uuids.UuidRootUser}'"
		")",

	90: "INSERT INTO texts "
			"(uuid, partition, text0) "
			"VALUES ("
			f"'{uuids.UuidGrids}',"
			"0,"
			"'Grids'"
		")",

	100: "INSERT INTO rows "
			"(uuid, gridUuid, enabled, revision, created, createdByUuid, updated, updatedByuuid) "
			"VALUES ("
			f"'{uuids.UuidColumns}',"
			f"'{uuids.UuidGrids}',"
			"true,"
			"1,"
			"now(),"
			f"'{uuids.UuidRootUser}',"
			"now(),"
			f"'{uuids.UuidRootUser}'"
		")",

	110: "INSERT INTO texts "
			"(uuid, partition, text0) "
			"VALUES ("
			f"'{uuids.UuidColumns}',"
			"0,"
			"'Columns'"
		")",

	120: "INSERT INTO rows "
			"(uuid, gridUuid, enabled, revision, created, createdByUuid, updated, updatedByuuid) "
			"VALUES ("
			f"'{uuids.UuidUsers}',"
			f"'{uuids.UuidGrids}',"
			"true,"
			"1,"
			"now(),"
			f"'{uuids.UuidRootUser}',"
			"now(),"
			f"'{uuids.UuidRootUser}'"
		")",

	130: "INSERT INTO texts "
			"(uuid, partition, text0) "
			"VALUES ("
			f"'{uuids.UuidUsers}',"
			"0,"
			"'Users'"
		")",
}

deletion_steps = {
	1: "DROP EXTENSION pgcrypto",
	2: "DROP EXTENSION vector",
	3: "DROP TABLE relationships",
	4: "DROP TABLE texts",
	5: "DROP TABLE ints",
	6: "DROP TABLE rows",
	7: "DROP TABLE migrations",
}
