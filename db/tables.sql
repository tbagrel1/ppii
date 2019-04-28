CREATE TABLE Airport (
    icao CHAR(4),
    iata CHAR(3),
    name NVARCHAR2(128) NOT NULL,
    city NVARCHAR2(128),
    country NVARCHAR2(128) NOT NULL,
    lat BINARY_DOUBLE NOT NULL,
    long BINARY_DOUBLE NOT NULL,
    altitude NUMBER(8, 3),
    utc_offset NUMBER(8, 4),
    daylight_saving_group CHAR(1),
    tz_name CHAR(32),
    type CHAR(16),
    data_source CHAR(16),
    PRIMARY KEY (icao, iata)
)

CREATE TABLE Path (
    id NUMBER(8) NOT NULL AUTOINCREMENT,
    real_step_nb NUMBER(2),
    db_step_nb NUMBER(2),
    distance NUMBER(8),
    PRIMARY_KEY (id)
)

CREATE TABLE AirportPath (
    path_id NUMBER(8) NOT NULL,
    airport_icao CHAR(4),
    airport_iata CHAR(3),
    step_no NUMBER(2),
    PRIMARY KEY (path_id, airport_icao, airport_iata),
    FOREIGN KEY (path_id) REFERENCES Path(id),
    FOREIGN KEY (airport_icao, airport_iata) REFERENCES Airport(icao, iata)
)

CREATE TABLE Airline (
    icao CHAR(4),
    iata CHAR(3),
    name NVARCHAR2(128),
    alias NVARCHAR2(128),
    callsign NVARCHAR2(128),
    country NVARCHAR2(128) NOT NULL,
    is_active NUMBER(1),
    PRIMARY_KEY (icao, iata)
)

CREATE TABLE Plane (
    plane_iaco CHAR(4),
    plane_iata CHAR(3),
    name NVARCHAR2(128),
    speed NUMBER(8),
    capacity NUMBER(4),
    co2_emission NUMBER(8),
    PRIMARY_KEY (icao, iata)
)

CREATE TABLE Fleet,
    id NUMBER(8) NOT NULL AUTOINCREMENT,
    plane_nb NUMBER(4),
    PRIMARY_KEY (id)
)

CREATE TABLE PlaneFleet
    fleet_id NUMBER(8) NOT NULL,
    plane_icao CHAR(4),
    plane_iata CHAR(3),
    PRIMARY_KEY (fleet_id, plane_icao, plane_iata),
    FOREIGN KEY (fleet_id) REFERENCES Fleet(id),
    FOREIGN KEY (plane_icao, plane_iata) REFERENCES Plane(icao, iata)
)

CREATE TABLE Exploitation,
    airline_icao CHAR(4),
    airline_iata CHAR(3),
    fleet_id NUMBER(8),
    path_id NUMBER(8),
    is_codeshare NUMBER(1),
    PRIMARY_KEY ( airline_icao, airline_iata, fleet_id, path_id),
    FOREIGN KEY (airline_icao, airline_iata) REFERENCES Airline(icao, iata),
    FOREIGN KEY (fleet_id) REFERENCES Fleet(id),
    FOREIGN KEY (path_id) REFERENCES Path(id)
)