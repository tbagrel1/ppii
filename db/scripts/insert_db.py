#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Fonctions utilitaires pour les données nettoyées dans la base de l'école.
"""
from parse_dats import get_final_tables

__author__ = "Timothée Adam, Thomas Bagrel"
__copyright__ = "Copyright 2019, PPII-A1"
__credits__ = ["Thimothée Adam", "Thomas Bagrel"]
__license__ = "Private"

import cx_Oracle

DB_URI = "grpa1/TPOracle@"

TABLE_NAMES = [
    "Airport",
    "Airline",
    "Plane",
    "Path",
    "AirportPath",
    "Fleet",
    "PlaneFleet",
    "Exploitation"
]

CREATE_TABLE_STATEMENTS = [
    """CREATE TABLE Airport (
    icao CHAR(4) NOT NULL,
    iata CHAR(3),
    name NVARCHAR2(128) NOT NULL,
    city NVARCHAR2(128),
    country NVARCHAR2(128) NOT NULL,
    latitude BINARY_DOUBLE NOT NULL,
    longitude BINARY_DOUBLE NOT NULL,
    altitude NUMBER(8, 3),
    utc_offset NUMBER(8, 4),
    daylight_saving_group CHAR(1),
    tz_name NVARCHAR2(32),
    type NVARCHAR2(32),
    data_source NVARCHAR2(32),
    PRIMARY KEY (icao)
)""",
    """CREATE TABLE Airline (
    icao CHAR(3) NOT NULL,
    iata CHAR(2),
    name NVARCHAR2(128) NOT NULL,
    alias NVARCHAR2(128),
    callsign NVARCHAR2(128),
    country NVARCHAR2(128),
    is_active NUMBER(1),
    PRIMARY KEY (icao)
)""",
    """CREATE TABLE Plane (
    icao CHAR(4),
    iata CHAR(3) NOT NULL,
    name NVARCHAR2(128) NOT NULL,
    speed BINARY_DOUBLE,
    capacity NUMBER(8),
    co2_emission BINARY_DOUBLE,
    PRIMARY KEY (iata)
)""",
    """CREATE TABLE Path (
    id NUMBER(8) NOT NULL,
    real_step_nb NUMBER(8),
    db_step_nb NUMBER(8) NOT NULL,
    real_distance BINARY_DOUBLE,
    straight_distance BINARY_DOUBLE NOT NULL,
    PRIMARY KEY (id)
)""",
    """CREATE TABLE AirportPath (
    path_id NUMBER(8) NOT NULL,
    airport_icao CHAR(4) NOT NULL,
    step_no NUMBER(8) NOT NULL,
    PRIMARY KEY (path_id, airport_icao),
    FOREIGN KEY (path_id) REFERENCES Path(id),
    FOREIGN KEY (airport_icao) REFERENCES Airport(icao)
)""",
    """CREATE TABLE Fleet (
    id NUMBER(8) NOT NULL,
    plane_nb NUMBER(8),
    PRIMARY KEY (id)
)""",
    """CREATE TABLE PlaneFleet (
    fleet_id NUMBER(8) NOT NULL,
    plane_iata CHAR(3) NOT NULL,
    PRIMARY KEY (fleet_id, plane_iata),
    FOREIGN KEY (fleet_id) REFERENCES Fleet(id),
    FOREIGN KEY (plane_iata) REFERENCES Plane(iata)
)""",
    """CREATE TABLE Exploitation (
    airline_icao CHAR(3) NOT NULL,
    fleet_id NUMBER(8) NOT NULL,
    path_id NUMBER(8) NOT NULL,
    flight_no CHAR(8),
    is_codeshare NUMBER(1),
    PRIMARY KEY (airline_icao, fleet_id, path_id, flight_no),
    FOREIGN KEY (airline_icao) REFERENCES Airline(icao),
    FOREIGN KEY (fleet_id) REFERENCES Fleet(id),
    FOREIGN KEY (path_id) REFERENCES Path(id)
)"""
]

DROP_TABLE_STATEMENTS = [
    """DROP TABLE Exploitation""",
    """DROP TABLE PlaneFleet""",
    """DROP TABLE Fleet""",
    """DROP TABLE AirportPath""",
    """DROP TABLE Path""",
    """DROP TABLE Plane""",
    """DROP TABLE Airline""",
    """DROP TABLE Airport"""
]


INSERT_VALUES_STATEMENTS = [
    """INSERT INTO Airport (icao, iata, name, city, country, latitude, longitude, altitude, utc_offset, daylight_saving_group, tz_name, type, data_source) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13)""",
    """INSERT INTO Airline (icao, iata, name, alias, callsign, country, is_active) VALUES (:1, :2, :3, :4, :5, :6, :7)""",
    """INSERT INTO Plane (icao, iata, name, speed, capacity, co2_emission) VALUES (:1, :2, :3, :4, :5, :6)""",
    """INSERT INTO Path (id, real_step_nb, db_step_nb, real_distance, straight_distance) VALUES (:1, :2, :3, :4, :5)""",
    """INSERT INTO AirportPath (path_id, airport_icao, step_no) VALUES (:1, :2, :3)""",
    """INSERT INTO Fleet (id, plane_nb) VALUES (:1, :2)""",
    """INSERT INTO PlaneFleet (fleet_id, plane_iata) VALUES (:1, :2)""",
    """INSERT INTO Exploitation (airline_icao, fleet_id, path_id, flight_no, is_codeshare) VALUES (:1, :2, :3, :4, :5)"""
]

INPUT_SIZESS = [
    (4, 3, 128, 128, 128, cx_Oracle.NATIVE_FLOAT, cx_Oracle.NATIVE_FLOAT, cx_Oracle.NUMBER, cx_Oracle.NUMBER, 1, 32, 32, 32),
    (3, 2, 128, 128, 128, 128, cx_Oracle.NUMBER),
    (4, 3, 128, cx_Oracle.NATIVE_FLOAT, cx_Oracle.NUMBER, cx_Oracle.NATIVE_FLOAT),
    (cx_Oracle.NUMBER, cx_Oracle.NUMBER, cx_Oracle.NUMBER, cx_Oracle.NATIVE_FLOAT, cx_Oracle.NATIVE_FLOAT),
    (cx_Oracle.NUMBER, 4, cx_Oracle.NUMBER),
    (cx_Oracle.NUMBER, cx_Oracle.NUMBER),
    (cx_Oracle.NUMBER, 3),
    (3, cx_Oracle.NUMBER, cx_Oracle.NUMBER, 8, cx_Oracle.NUMBER)
]

MAPPERS = {
    "Airport": lambda d: (d["icao"], d["iata"], d["name"], d["city"], d["country"], d["lat"], d["long"], d["altitude"], d["utc_offset"], d["daylight_saving_group"], d["tz_name"], d["type"], d["data_source"]),
    "Airline": lambda d: (d["icao"], d["iata"], d["name"], d["alias"], d["callsign"], d["country"], d["is_active"]),
    "Plane": lambda d: (d["icao"], d["iata"], d["name"], d["speed"], d["capacity"], d["co2_emission"]),
    "Path": lambda d: (d["id"], d["real_step_nb"], d["db_step_nb"], d["real_distance"], d["straight_distance)"]),
    "AirportPath": lambda d: (d["path_id"], d["airport_icao"], d["step_no"]),
    "Fleet": lambda d: (d["id"], d["plane_nb"]),
    "PlaneFleet": lambda d: (d["fleet_id"], d["plane_iata"]),
    "Exploitation": lambda d: (d["airline_icao"], d["fleet_id"], d["path_id"], d["flight_no"], d["is_codeshare"])
}

def main():
    connection = cx_Oracle.connect(user="grpa1", password="TPOracle", dsn="oracle.telecomnancy.univ-lorraine.fr:1521/TNCY")

    e = None

    try:

        cursor = connection.cursor()

        for drop_table_statement in DROP_TABLE_STATEMENTS:
            try:
                cursor.execute(drop_table_statement)
            except:
                pass

        for table_create_statement in CREATE_TABLE_STATEMENTS:
            cursor.execute(table_create_statement)

        tables = get_final_tables()

        for i, (table_name, insert_values_statement, input_sizes) in enumerate(zip(TABLE_NAMES, INSERT_VALUES_STATEMENTS, INPUT_SIZESS)):
            cursor.setinputsizes(*input_sizes)
            cursor.executemany(INSERT_VALUES_STATEMENTS, list(map(MAPPERS[table_name], tables[table_name])))
            print("OK {}".format(i))

    except Exception as ee:
        e = ee

    finally:
        connection.close()

    if e is not None:
        raise e

if __name__ == "__main__":
    main()

