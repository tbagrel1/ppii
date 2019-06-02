#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Fonctions utilitaires pour les données nettoyées dans la base de l'école.
"""
from parse_dats import get_final_tables

__author__ = "Timothée Adam, Thomas Bagrel"
__copyright__ = "Copyright 2019, PPII-A1"
__credits__ = ["Timothée Adam", "Thomas Bagrel"]
__license__ = "Private"

import cx_Oracle

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
    fleet_id NUMBER(8),
    path_id NUMBER(8) NOT NULL,
    flight_no CHAR(8),
    is_codeshare NUMBER(1),
    PRIMARY KEY (airline_icao, path_id, flight_no),
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
    """INSERT INTO Airport (icao, iata, name, city, country, latitude, longitude, altitude, utc_offset, daylight_saving_group, tz_name, type, data_source) VALUES (:icao, :iata, :name, :city, :country, :latitude, :longitude, :altitude, :utc_offset, :daylight_saving_group, :tz_name, :type, :data_source)""",
    """INSERT INTO Airline (icao, iata, name, alias, callsign, country, is_active) VALUES (:icao, :iata, :name, :alias, :callsign, :country, :is_active)""",
    """INSERT INTO Plane (icao, iata, name, speed, capacity, co2_emission) VALUES (:icao, :iata, :name, :speed, :capacity, :co2_emission)""",
    """INSERT INTO Path (id, real_step_nb, db_step_nb, real_distance, straight_distance) VALUES (:id, :real_step_nb, :db_step_nb, :real_distance, :straight_distance)""",
    """INSERT INTO AirportPath (path_id, airport_icao, step_no) VALUES (:path_id, :airport_icao, :step_no)""",
    """INSERT INTO Fleet (id, plane_nb) VALUES (:id, :plane_nb)""",
    """INSERT INTO PlaneFleet (fleet_id, plane_iata) VALUES (:fleet_id, :plane_iata)""",
    """INSERT INTO Exploitation (airline_icao, fleet_id, path_id, flight_no, is_codeshare) VALUES (:airline_icao, :fleet_id, :path_id, :flight_no, :is_codeshare)"""
]

N = cx_Oracle.NUMBER
B = cx_Oracle.NATIVE_FLOAT
U = cx_Oracle.NCHAR

INPUT_SIZESS = [
    {
        "icao": 4,
        "iata": 3,
        "name": U,
        "city": U,
        "country": U,
        "latitude": B,
        "longitude": B,
        "altitude": N,
        "utc_offset": N,
        "daylight_saving_group": 1,
        "tz_name": U,
        "type": U,
        "data_source": U
    },
    {
        "icao": 3,
        "iata": 2,
        "name": U,
        "alias": U,
        "callsign": U,
        "country": U,
        "is_active": N
    },
    {
        "icao": 4,
        "iata": 3,
        "name": U,
        "speed": B,
        "capacity": N,
        "co2_emission": B
    },
    {
        "id": N,
        "real_step_nb": N,
        "db_step_nb": N,
        "real_distance": B,
        "straight_distance": B
    },
    {
        "path_id": N,
        "airport_icao": 4,
        "step_no": N
    },
    {
        "id": N,
        "plane_nb": N
    },
    {
        "fleet_id": N,
        "plane_iata": 3
    },
    {
        "airline_icao": 3,
        "fleet_id": N,
        "path_id": N,
        "flight_no": 8,
        "is_codeshare": N
    }
]


def main():
    connection = cx_Oracle.connect(user="grpa1", password="TPOracle", dsn="oracle.telecomnancy.univ-lorraine.fr:1521/TNCY", nencoding="utf-8")

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
            cursor.setinputsizes(**input_sizes)
            cursor.prepare(insert_values_statement)
            cursor.executemany(None, tables[table_name])
            print("OK {}".format(i))

        connection.commit()

    except Exception as ee:
        e = ee

    finally:
        connection.close()

    if e is not None:
        raise e


if __name__ == "__main__":
    main()

