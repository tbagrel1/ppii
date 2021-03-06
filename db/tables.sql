CREATE TABLE Airport (
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
);

CREATE TABLE Airline (
    icao CHAR(3) NOT NULL,
    iata CHAR(2),
    name NVARCHAR2(128) NOT NULL,
    alias NVARCHAR2(128),
    callsign NVARCHAR2(128),
    country NVARCHAR2(128),
    is_active NUMBER(1),
    PRIMARY KEY (icao)
);

CREATE TABLE Plane (
    icao CHAR(4),
    iata CHAR(3) NOT NULL,
    name NVARCHAR2(128) NOT NULL,
    speed BINARY_DOUBLE,
    capacity NUMBER(8),
    co2_emission BINARY_DOUBLE,
    PRIMARY KEY (iata)
)

CREATE TABLE Path (
    id NUMBER(8) NOT NULL,
    real_step_nb NUMBER(8),
    db_step_nb NUMBER(8) NOT NULL,
    real_distance BINARY_DOUBLE,
    straight_distance BINARY_DOUBLE NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE AirportPath (
    path_id NUMBER(8) NOT NULL,
    airport_icao CHAR(4) NOT NULL,
    step_no NUMBER(8) NOT NULL,
    PRIMARY KEY (path_id, airport_icao),
    FOREIGN KEY (path_id) REFERENCES Path(id),
    FOREIGN KEY (airport_icao) REFERENCES Airport(icao)
);

CREATE TABLE Fleet (
    id NUMBER(8) NOT NULL,
    plane_nb NUMBER(8),
    PRIMARY KEY (id)
);

CREATE TABLE PlaneFleet (
    fleet_id NUMBER(8) NOT NULL,
    plane_iata CHAR(3) NOT NULL,
    PRIMARY KEY (fleet_id, plane_iata),
    FOREIGN KEY (fleet_id) REFERENCES Fleet(id),
    FOREIGN KEY (plane_iata) REFERENCES Plane(iata)
);

CREATE TABLE Exploitation,
    airline_icao CHAR(3) NOT NULL,
    fleet_id NUMBER(8),
    path_id NUMBER(8) NOT NULL,
    flight_no CHAR(8),
    is_codeshare NUMBER(1),
    PRIMARY KEY (airline_icao, path_id, flight_no),
    FOREIGN KEY (airline_icao) REFERENCES Airline(icao),
    FOREIGN KEY (fleet_id) REFERENCES Fleet(id),
    FOREIGN KEY (path_id) REFERENCES Path(id)
);