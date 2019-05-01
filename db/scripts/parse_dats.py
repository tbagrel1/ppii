#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Fonctions utilitaires pour traiter/nettoyer les bases de données rendues
disponibles par https://openflights.org/.
"""

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
    {"parser": drop, "name": "id", "opt": True},
    {"parser": field_as_is_builder("airport", "name", *memory), "name": "name", "opt": False},
    {"parser": field_as_is_builder("airport", "city", *memory), "name": "city", "opt": True},
    {"parser": field_as_is_builder("airport", "country", *memory), "name": "country", "opt": False},
    {"parser": airport_iata, "name": "iata", "opt": True},
    {"parser": airport_icao, "name": "icao", "opt": False},
    {"parser": lat, "name": "lat", "opt": False},
    {"parser": long, "name": "long", "opt": False},
    {"parser": altitude_with_ft_to_m_conversion, "name": "altitude", "opt": True},
    {"parser": utc_offset, "name": "utc_offset", "opt": True},
    {"parser": daylight_saving_group, "name": "daylight_saving_group", "opt": True},
    {"parser": tz_name, "name": "tz_name", "opt": True},
    {"parser": airport_type, "name": "type", "opt": True},
    {"parser": airport_data_source, "name": "data_source", "opt": True}
]


# +---------------------------------------------------------------------------+
# |                              Airline parsing                              |
# +---------------------------------------------------------------------------+

AIRLINE_PARSING_RULES = lambda *memory: [
    {"parser": drop, "name": "id", "opt": True},
    {"parser": field_as_is_builder("airline", "name", *memory), "name": "name", "opt": False},
    {"parser": field_as_is_builder("airline", "alias", *memory), "name": "alias", "opt": True},
    {"parser": airline_iata, "name": "iata", "opt": True},
    {"parser": airline_icao, "name": "icao", "opt": False},
    {"parser": field_as_is_builder("airline", "callsign", *memory), "name": "callsign", "opt": True},
    {"parser": field_as_is_builder("airline", "country", *memory), "name": "country", "opt": True},
    {"parser": yes_no, "name": "is_active", "opt": True}
]


# +---------------------------------------------------------------------------+
# |                               Plane parsing                               |
# +---------------------------------------------------------------------------+

PLANE_PARSING_RULES = lambda *memory: [
    {"parser": field_as_is_builder("plane", "name", *memory), "name": "name", "opt": False},
    {"parser": plane_iata, "name": "iata", "opt": False},
    {"parser": plane_icao, "name": "icao", "opt": True}
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
            index_table_by(airports, "Airport", "icao", "iata", memory)


if __name__ == "__main__":
    main()
