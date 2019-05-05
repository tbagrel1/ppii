#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Fonctions utilitaires pour traiter/nettoyer les bases de données rendues
disponibles par https://openflights.org/.
"""
from pprint import pprint

__author__ = "Timothée Adam, Thomas Bagrel"
__copyright__ = "Copyright 2019, PPII-A1"
__credits__ = ["Thimothée Adam", "Thomas Bagrel"]
__license__ = "Private"


import csv

from parsers import *
from utils import *


ENC = "utf-8"


RESOURCES_ROOT_DIR = "../../resources"
PERSISTANCE_ROOT_DIR = path.join(RESOURCES_ROOT_DIR, "json_persistance")

# +---------------------------------------------------------------------------+
# |                              Airport parsing                              |
# +---------------------------------------------------------------------------+

AIRPORT_PARSING_RULES = lambda *memory: [
    {"name": "id", "parser": drop, "opt": True},
    {"name": "name", "parser": field_as_is_builder("airport", "name", *memory), "opt": False},
    {"name": "city", "parser": field_as_is_builder("airport", "city", *memory), "opt": True},
    {"name": "country", "parser": field_as_is_builder("airport", "country", *memory), "opt": False},
    {"name": "iata", "parser": airport_iata, "opt": True},
    {"name": "icao", "parser": airport_icao, "opt": False},
    {"name": "lat", "parser": lat, "opt": False},
    {"name": "long", "parser": long, "opt": False},
    {"name": "altitude", "parser": altitude_with_ft_to_m_conversion, "opt": True},
    {"name": "utc_offset", "parser": utc_offset, "opt": True},
    {"name": "daylight_saving_group", "parser": daylight_saving_group, "opt": True},
    {"name": "tz_name", "parser": tz_name, "opt": True},
    {"name": "type", "parser": airport_type, "opt": True},
    {"name": "data_source", "parser": airport_data_source, "opt": True}
]


# +---------------------------------------------------------------------------+
# |                              Airline parsing                              |
# +---------------------------------------------------------------------------+

AIRLINE_PARSING_RULES = lambda *memory: [
    {"name": "id", "parser": drop, "opt": True},
    {"name": "name", "parser": field_as_is_builder("airline", "name", *memory), "opt": False},
    {"name": "alias", "parser": field_as_is_builder("airline", "alias", *memory), "opt": True},
    {"name": "iata", "parser": airline_iata, "opt": True},
    {"name": "icao", "parser": airline_icao, "opt": False},
    {"name": "callsign", "parser": field_as_is_builder("airline", "callsign", *memory), "opt": True},
    {"name": "country", "parser": field_as_is_builder("airline", "country", *memory), "opt": True},
    {"name": "is_active", "parser": yes_no, "opt": True}
]


# +---------------------------------------------------------------------------+
# |                               Plane parsing                               |
# +---------------------------------------------------------------------------+

PLANE_PARSING_RULES = lambda *memory: [
    {"name": "name", "parser": field_as_is_builder("plane", "name", *memory), "opt": False},
    {"name": "iata", "parser": plane_iata, "opt": False},
    {"name": "icao", "parser": plane_icao, "opt": True}
]


# +---------------------------------------------------------------------------+
# |                               Route parsing                               |
# +---------------------------------------------------------------------------+

ROUTE_PARSING_RULES = lambda iata_to_plane, icao_to_plane, icao_to_airport, iata_to_airport, icao_to_airline, iata_to_airline: [
    {"name": "airline_icao", "parser": get_primary_key_builder("icao", icao_to_airline, iata_to_airline), "opt": False},
    {"name": "airline_openflights_id", "parser": drop, "opt": True},
    {"name": "source_airport_icao", "parser": get_primary_key_builder("icao", icao_to_airport, iata_to_airport), "opt": False},
    {"name": "source_airport_openflights_id", "parser": drop, "opt": True},
    {"name": "destination_airport_icao", "parser": get_primary_key_builder("icao", icao_to_airport, iata_to_airport), "opt": False},
    {"name": "destination_airport_openflights_id", "parser": drop, "opt": True},
    {"name": "is_codeshare", "parser": yes_no, "opt": True},
    {"name": "real_step_nb", "parser": compose(parse_int, lambda stop_nb: stop_nb + 2), "opt": True},
    {"name": "fleet_tuple", "parser": sorted_tuple(plane_iata, separator=" ", strict=False, min=1, max=None), "opt": True}
]


# +---------------------------------------------------------------------------+
# |                              Flight parsing                               |
# +---------------------------------------------------------------------------+

FLIGHT_PARSING_RULES = lambda iata_to_plane, icao_to_plane, icao_to_airport, iata_to_airport, icao_to_airline, iata_to_airline: [
    {"name": "airline_icao", "parser": get_primary_key_builder("icao", icao_to_airline, iata_to_airline), "opt": False},
    {"name": "flight_no", "parser": flight_no, "opt": True},
    {"name": "path_tuple", "parser": ordered_tuple(get_primary_key_builder("icao", icao_to_airport, iata_to_airport), separator="-", strict=True, min=2, max=None), "opt": False}
]

# +---------------------------------------------------------------------------+


def parse_table(input_path, table_name, table_parsing_rules_func, *memory):
    print("======== {} ========\n".format(table_name))

    with open(input_path, "r", encoding=ENC) as input_file:
        csv_reader = csv.reader(input_file, delimiter=",", quotechar="\"")
        data = [list(row) for row in csv_reader]

    table_parsing_rules = table_parsing_rules_func(*memory)
    n = len(table_parsing_rules)

    output_data = []
    valid_rows = 0

    for i_row, row in enumerate(data):
        if len(row) > len(table_parsing_rules):
            display_alert(
                WARNING, i_row, row, "len(row): {} > len(parsers): {}"
                                     .format(len(row), n))
        if len(row) < len(table_parsing_rules):
            display_alert(
                ERROR, i_row, row, "len(row): {} < len(parsers): {}"
                                   .format(len(row), n))
            continue

        output_row = {}
        valid = True

        for i_field, (field_format, field) in enumerate(
                zip(table_parsing_rules, row)):
            if field_format["parser"] == drop:
                continue
            result = field_format["parser"](field)
            if result is None and not field_format["opt"]:
                display_alert_field(
                    ERROR, i_row, row, i_field, field_format["name"])
                valid = False
                break
            output_row[field_format["name"]] = result

        if valid:
            output_data.append(output_row)
            valid_rows += 1

    print("\n--- Valid rows: {} / {} ({:.2f} %)\n\n".format(
        valid_rows, len(data), valid_rows * 100 / len(data)))

    return output_data


def index_table_by(
        rows, table_name, default_index, fallback_index, unique_choice_memory):

    table_with_unique_default_index = make_unique(
        rows, table_name, default_index, unique_choice_memory)
    table_default_index_to_row = index_list_by(
        table_with_unique_default_index, default_index)
    table_with_unique_fallback_index = make_unique(
        table_with_unique_default_index, "_{}".format(table_name),
        fallback_index, unique_choice_memory)
    table_fallback_index_to_row = index_list_by(
        table_with_unique_fallback_index, fallback_index)

    return (
        table_with_unique_default_index,
        table_default_index_to_row,
        table_fallback_index_to_row
    )


def replace_source_destination_by_path(routes):
    for route in routes:
        route["path_tuple"] = (route["source_airport_icao"], route["destination_airport_icao"])

        del route["source_airport_icao"]
        del route["destination_airport_icao"]


def path_length(icao_to_airport, path_tuple):
    # TODO implémenter le calcul des distances
    return 0.0


def extract_paths(exploitations, icao_to_airport):
    pt_rsn_to_path = {}
    next_path_id = 0
    for exploitation in exploitations:
        path_tuple, real_step_nb = exploitation["path_tuple"], exploitation["real_step_nb"]
        if (path_tuple, real_step_nb) not in pt_rsn_to_path:
            path_id = next_path_id
            next_path_id += 1

            pt_rsn_to_path[(path_tuple, real_step_nb)] = {
                "id": path_id,
                "real_step_nb": real_step_nb,
                "db_step_nb": len(path_tuple),
                "real_distance": None if real_step_nb != len(path_tuple) is None else path_length(icao_to_airport, path_tuple),
                "straight_distance": path_length(icao_to_airport, (path_tuple[0], path_tuple[:-1])),
                "path_tuple": path_tuple
            }
        else:
            path_id = pt_rsn_to_path[(path_tuple, real_step_nb)]["id"]
        exploitation["path_id"] = path_id
        del exploitation["path_tuple"]
        del exploitation["real_step_nb"]

    return list(pt_rsn_to_path.values())


def extract_airports_paths(paths):
    airports_paths = []
    for path in paths:
        path_id = path["id"]
        for step_no, airport_icao in enumerate(path["path_tuple"]):
            airports_paths.append({
                "path_id": path_id,
                "airport_icao": airport_icao,
                "step_no": step_no
            })
        del path["path_tuple"]
    return airports_paths


def extract_fleets(exploitations):
    ft_to_fleet = {}
    next_fleet_id = 0
    for exploitation in exploitations:
        fleet_tuple = exploitation["fleet_tuple"]
        if fleet_tuple is None:
            fleet_id = None
        else:
            if fleet_tuple not in ft_to_fleet:
                fleet_id = next_fleet_id
                next_fleet_id += 1

                ft_to_fleet[fleet_tuple] = {
                    "id": fleet_id,
                    "plane_nb": len(fleet_tuple),
                    "fleet_tuple": fleet_tuple
                }
            else:
                fleet_id = ft_to_fleet[fleet_tuple]["id"]
        exploitation["fleet_id"] = fleet_id
        del exploitation["fleet_tuple"]

    return list(ft_to_fleet.values())


def extract_planes_fleets(fleets):
    planes_fleets = []
    for fleet in fleets:
        fleet_id = fleet["id"]
        for plane_iata in fleet["fleet_tuple"]:
            planes_fleets.append({
                "fleet_id": fleet_id,
                "plane_iata": plane_iata
            })
        del fleet["fleet_tuple"]
    return planes_fleets


def main():
    """Si le module est lancé directement (ie n'est pas un import)."""

    with JsonPersistance(PERSISTANCE_ROOT_DIR, [
                ("to_keep.json", dict),
                ("to_edit.json", dict),
                ("to_discard.json", dict),
            ], ask_confirmation=False) as memory:
        planes = parse_table(
            path.join(RESOURCES_ROOT_DIR, "planes.dat"), "Plane",
            PLANE_PARSING_RULES, *memory)
        add_new_fields(planes, [("speed", None), ("capacity", None), ("co2_emission", None)])

        airports = parse_table(
            path.join(RESOURCES_ROOT_DIR, "airports.dat"), "Airport",
            AIRPORT_PARSING_RULES, *memory)
        airlines = parse_table(
            path.join(RESOURCES_ROOT_DIR, "airlines.dat"), "Airline",
            AIRLINE_PARSING_RULES, *memory)

    print("\n-------------------------------------------------\n")

    with JsonPersistance(PERSISTANCE_ROOT_DIR, [
                ("unique_choice.json", dict)
            ], ask_confirmation=False) as memory:
        memory = memory[0]

        # Identification pour Plane : IATA en premier, ICAO en secours
        planes, iata_to_plane, icao_to_plane = \
            index_table_by(planes, "Plane", "iata", "icao", memory)

        # Identification pour Airport : ICAO en premier, IATA en secours
        airports, icao_to_airport, iata_to_airport = \
            index_table_by(airports, "Airport", "icao", "iata", memory)

        # Identification pour Airline : ICAO en premier, IATA en secours
        airlines, icao_to_airline, iata_to_airline = \
            index_table_by(airlines, "Airline", "icao", "iata", memory)

    maps = (iata_to_plane, icao_to_plane, icao_to_airport, iata_to_airport, icao_to_airline, iata_to_airline)

    routes = parse_table(path.join(RESOURCES_ROOT_DIR, "routes.dat"), "Route", ROUTE_PARSING_RULES, *maps)
    replace_source_destination_by_path(routes)
    add_new_fields(routes, [("flight_no", None)])

    flights = parse_table(path.join(RESOURCES_ROOT_DIR, "flights.dat"), "Flight", FLIGHT_PARSING_RULES, *maps)
    add_new_fields(flights, [("fleet_tuple", None), ("real_step_nb", lambda row: len(row["path_tuple"])), ("is_codeshare", None)])

    # routes et flights ont la même structure maintenant
    exploitations = routes + flights

    paths = extract_paths(exploitations, icao_to_airport)
    fleets = extract_fleets(exploitations)
    airports_paths = extract_airports_paths(paths)
    planes_fleets = extract_planes_fleets(fleets)

    print("\n\n")
    for elt in [planes, airports, airlines, exploitations, paths, airports_paths, fleets, planes_fleets]:
        pprint(elt[:10])
        print("\n{} ready to insert\n{}\n".format(len(elt), "-" * 79))

    # TODO: s'assurer qu'un aéroport n'est pas présent 2 fois dans un path
    # TODO: s'assurer qu'un avion n'est pas présent 2 fois dans un fleet
    # Done !


if __name__ == "__main__":
    main()
