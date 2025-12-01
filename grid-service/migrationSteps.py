import uuids

migrationSteps = {
    10: "CREATE TABLE migrations ("
			"sequence integer NOT NULL,"
			"statement text NOT NULL,"
			"PRIMARY KEY (sequence)"
		")",

    20: "CREATE EXTENSION IF NOT EXISTS pgcrypto",

    30: "CREATE EXTENSION IF NOT EXISTS vector",
    
    40: "CREATE TABLE rows ("
			"gridUuid uuid NOT NULL, "
			"rowUuid uuid NOT NULL, "
			"created timestamp with time zone NOT NULL, "
			"createdByUuid uuid NOT NULL, "
			"updated timestamp with time zone NOT NULL, "
			"updatedByuuid uuid NOT NULL, "
			"enabled boolean NOT NULL, "
			"revision integer NOT NULL CHECK (revision > 0), "
			"PRIMARY KEY (gridUuid, rowUuid)"
		")",

    50: "CREATE TABLE texts ("
			"gridUuid uuid NOT NULL, "
			"rowUuid uuid NOT NULL, "
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
			"PRIMARY KEY (gridUuid, rowUuid, partition)"
		")",

    60: "CREATE TABLE ints ("
			"gridUuid uuid NOT NULL, "
			"rowUuid uuid NOT NULL, "
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
			"PRIMARY KEY (gridUuid, rowUuid, partition)"
		")",

    70: "CREATE TABLE relationships ("
			"gridUuid uuid NOT NULL, "
			"rowUuid uuid NOT NULL, "
			"partition integer, "
			"relGridUuid0 uuid, "
			"relRowUuid0 uuid, "
			"relGridUuid1 uuid, "
			"relRowUuid1 uuid, "
			"relGridUuid2 uuid, "
			"relRowUuid2 uuid, "
			"relGridUuid3 uuid, "
			"relRowUuid3 uuid, "
			"relGridUuid4 uuid, "
			"relRowUuid4 uuid, "
			"relGridUuid5 uuid, "
			"relRowUuid5 uuid, "
			"relGridUuid6 uuid, "
			"relRowUuid6 uuid, "
			"relGridUuid7 uuid, "
			"relRowUuid7 uuid, "
			"relGridUuid8 uuid, "
			"relRowUuid8 uuid, "
			"relGridUuid9 uuid, "
			"relRowUuid9 uuid, "
			"PRIMARY KEY (gridUuid, rowUuid, partition)"
		")",
}

