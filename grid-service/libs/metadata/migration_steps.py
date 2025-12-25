'''  
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the migration steps for the clairgrid database.
'''

from .metadata import SystemIds

def get_migration_steps(root_user_name, root_password):
    return {
        10: "CREATE TABLE migrations ("
                "sequence integer NOT NULL,"
                "statement text NOT NULL,"
                "PRIMARY KEY (sequence)"
            ")",

        20: "CREATE EXTENSION IF NOT EXISTS pgcrypto",

        30: "CREATE EXTENSION IF NOT EXISTS vector",
        
        40: "CREATE TABLE rows ("
                "gridUuid uuid NOT NULL, "
                "uuid uuid NOT NULL, "
                "enabled boolean NOT NULL, "
                "revision integer NOT NULL CHECK (revision > 0), "
                "PRIMARY KEY (gridUuid, uuid),"
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
                "fromUuid uuid REFERENCES rows (uuid), "
                "toUuid0 uuid REFERENCES rows (uuid), "
                "toUuid1 uuid REFERENCES rows (uuid), "
                "toUuid2 uuid REFERENCES rows (uuid), "
                "toUuid3 uuid REFERENCES rows (uuid), "
                "toUuid4 uuid REFERENCES rows (uuid), "
                "toUuid5 uuid REFERENCES rows (uuid), "
                "toUuid6 uuid REFERENCES rows (uuid), "
                "toUuid7 uuid REFERENCES rows (uuid), "
                "toUuid8 uuid REFERENCES rows (uuid), "
                "toUuid9 uuid REFERENCES rows (uuid), "
                "PRIMARY KEY (uuid, partition)"
            ")",

        140: "INSERT INTO rows "
                "(gridUuid, uuid, enabled, revision) "
                "VALUES ("
                f"'{SystemIds.Users}',"
                f"'{SystemIds.RootUser}',"
                "true,"
                "1"
            ")",


        150: "INSERT INTO texts "
                "(uuid, partition, text0, text1, text2, text3) "
                "VALUES ("
                f"'{SystemIds.RootUser}',"
                "0,"
                f"'{root_user_name}',"
                f"'{root_user_name}',"
                f"'{root_user_name}',"
                f"'{root_password}'"
            ")",

        160: "CREATE TABLE booleans ("
                "uuid uuid NOT NULL, "
                "partition integer, "
                "bool0 boolean, "
                "bool1 boolean, "
                "bool2 boolean, "
                "bool3 boolean, "
                "bool4 boolean, "
                "bool5 boolean, "
                "bool6 boolean, "
                "bool7 boolean, "
                "bool8 boolean, "
                "bool9 boolean, "
                "PRIMARY KEY (uuid, partition)"
            ")",
    }

def get_deletion_steps():
    return {
        1: "DROP EXTENSION pgcrypto",
        2: "DROP EXTENSION vector",
        3: "DROP TABLE relationships",
        4: "DROP TABLE texts",
        5: "DROP TABLE ints",
        6: "DROP TABLE booleans",
        7: "DROP TABLE rows",
        8: "DROP TABLE migrations"
    }
