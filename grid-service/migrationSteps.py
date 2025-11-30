migrationSteps = {
    1: "CREATE EXTENSION IF NOT EXISTS pgcrypto",

    2: "CREATE EXTENSION IF NOT EXISTS vector",
    
    3: "CREATE TABLE rows ("
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
}

