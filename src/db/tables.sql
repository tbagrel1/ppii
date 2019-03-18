Valider les champs avec une regex!!! surtout les IATA/ICAO

CREATE TABLE AIRPORTS (
    airport_id NUMBER(8) NOT NULL, // valeur max constatée : 13000, donc 5 + un peu de marge
    airport_name NVARCHAR2(128) NOT NULL, // valeur max constatée : 65
    city_name NVARCHAR2(128), // max : 33
    country_name NVARCHAR2(128) NOT NULL, // max : 32
    airport_iata CHAR(3),
    airport_icao CHAR(4),
    airport_lat BINARY_DOUBLE NOT NULL,
    airport_long BINARY_DOUBLE NOT NULL,
    airport_altitude NUMBER(8, 3), //!\ ne pas oublier de convertir en mètres !!!
    utc_offset NUMBER(8, 4),
    dst CHAR(1),
    tz_name CHAR(32),
    airport_type CHAR(16),
    data_source CHAR(16)
)

CREATE TABLE AIRLINES (
    airline_id NUMBER(8) NOT NULL,
    airline_name NVARCHAR2(128) // max: 81,
    airline_alias NVARCHAR2(128) // max: 30,
    airline_iata CHAR(3),
    airline_icao CHAR(4),
    airline_callsign NVARCHAR2(128) // max: 50,
    country_name NVARCHAR2(128) NOT NULL, // max : 32
    is_active NUMBER(1)
)

CREATE TABLE ROUTES (
    route_id NUMBER(8) NOT NULL AUTOINCREMENT,
    airline_id NUMBER(8),
    src_airport_id NUMBER(8),
    dst_airport_id NUMBER(8),
    is_codeshare NUMBER(1),
    route_stops_nb NUMBER(2)
)

CREATE TABLE PLANES (
    plane_id NUMBER(8) NOT NULL AUTOINCREMENT,
    plane_name NVARCHAR2(128),
    plane_iata CHAR(3),
    plane_iaco CHAR(4)
)

CREATE TABLE PREFERRED_PLANES (
    route_id NUMBER(8) NOT NULL,
    plane_iata CHAR(3) NOT NULL
)


