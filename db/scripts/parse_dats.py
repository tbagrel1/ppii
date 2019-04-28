#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Fonctions utilitaires pour traiter/nettoyer les bases de données rendues
disponibles par https://openflights.org/.
"""

__author__ = "Timothée Adam, Thomas Bagrel"
__copyright__ = "Copyright 2019, PPII-A1"
__credits__ = ["Thimothée Adam", "Thomas Bagrel"]
__license__ = "Private"


from os import path

import csv
import json


from parsers import *


ENC = "utf-8"

AIRPORT_IATA_REC = re.compile(r"^[A-Z0-9]{3}$")
AIRPORT_ICAO_REC = re.compile(r"^[A-Z0-9]{4}$")

AIRLINE_IATA_REC = re.compile(r"^[A-Z0-9]{2}$")
AIRLINE_ICAO_REC = re.compile(r"^[A-Z0-9]{3}$")

PLANE_IATA_REC = re.compile(r"^[A-Z0-9]{3}$")
PLANE_ICAO_REC = re.compile(r"^[A-Z0-9]{4}$")

WARNING = "W"
ERROR = "E"

SEVERITY_TO_COLOR = {
    WARNING: 221,
    ERROR: 196
}

RESOURCES_ROOT_DIR = "../../resources"
PERSISTANCE_ROOT_DIR = path.join(RESOURCES_ROOT_DIR, "json_persistance")


def _should_(prompt_part, path_):
    choice = input((
        "Should we {} {}?\n"
        "    [Y]es (default)\n"
        "    [N]o\n"
        ">>> "
    ).format(prompt_part, path_)).strip().lower()

    if choice in ["n", "no"]:
        return False

    return True


def should_load(path_):
    return _should_("load from", path_)


def should_save(path_):
    return _should_("save to", path_)


class JsonPersistance:
    def __init__(self, root_dir, names_types, ask_confirmation=False):
        self.root_dir = root_dir
        self.names_types = names_types
        self.ask_confirmation = ask_confirmation

    def __enter__(self):
        self.contents = []
        for name, type_ in self.names_types:
            path_ = path.join(self.root_dir, name)
            try:
                if self.ask_confirmation and not should_load(path_):
                    raise Exception("Should create instead")
                with open(path_, "r", encoding=ENC) as file:
                    content = json.load(file)
                print("    --- LOADED FROM {}".format(path_))
            except Exception as _:
                content = type_()
                print("    --- CREATED ({})".format(path_))
            self.contents.append(content)
        print("\n")

        return self.contents

    def __exit__(self, type, value, traceback):
        print("\n")
        for ((name, type_), content) in zip(self.names_types, self.contents):
            path_ = path.join(self.root_dir, name)
            try:
                if self.ask_confirmation and not should_save(path_):
                    raise Exception("Should not save")
                with open(path_, "w", encoding=ENC) as file:
                    json.dump(content, file, indent=2, sort_keys=True)
                print("    --- SAVED TO {}".format(path_))
            except Exception as _:
                print("    --- NOT SAVED ({})".format(path_))


def color_escapes(color_code):
    return "\u001b[38;5;{}m".format(color_code), "\u001b[0m"


def memorize_unique_choice(unique_choice_memory, context, unique_field, unique_field_value, choice_no, total_choices_nb):
    if context not in unique_choice_memory:
        unique_choice_memory[context] = {}
    if unique_field not in unique_choice_memory[context]:
        unique_choice_memory[context][unique_field] = {}
    unique_choice_memory[context][unique_field][unique_field_value] = (choice_no, total_choices_nb)


def is_memorized_unique_choice(unique_choice_memory, context, unique_field, unique_field_value):
    if context not in unique_choice_memory:
        return False
    if unique_field not in unique_choice_memory[context]:
        return False
    if unique_field_value not in unique_choice_memory[context][unique_field]:
        return False
    return True


def ask_unique_choice(unique_field, rows):
    print("[{}: {}]".format(unique_field, rows[0][unique_field]))
    for i, row in enumerate(rows):
        text_for_default_choice = " (default)" if i == 0 else ""
        print("    {}) {} {}".format(i, row, text_for_default_choice))
    raw_choice_no = input(">>> ").strip()
    try:
        choice_no = int(raw_choice_no)
        if choice_no not in range(len(rows)):
            raise Exception("Choice no not in allowed range: {} vs [{}-{}]"
                            .format(choice_no, 0, len(rows) - 1))
        print()
        return choice_no
    except:
        print()
        return 0


def get_active_rows(rows):
    if "is_active" not in rows[0]:
        return []
    active_rows = []
    for row in rows:
        if row["is_active"]:
            active_rows.append(row)
    return active_rows


def make_unique(data, context, unique_field, unique_choice_memory):
    unique_field_to_rows = {}
    for row in data:
        unique_field_value = row[unique_field]
        if unique_field_value not in unique_field_to_rows:
            unique_field_to_rows[unique_field_value] = []
        unique_field_to_rows[unique_field_value].append(row)

    result = []
    for unique_field_value, rows in unique_field_to_rows.items():
        if unique_field_value is None:
            continue
        if len(rows) == 1:
            result.append(rows[0])
        else:
            if is_memorized_unique_choice(
                    unique_choice_memory, context, unique_field,
                    unique_field_value):
                memorized_choice_no, memorized_total_choices_nb = \
                    unique_choice_memory[context][unique_field][unique_field_value]
                if memorized_total_choices_nb == len(rows):
                    result.append(rows[memorized_choice_no])
                    continue
            active_rows = get_active_rows(rows)
            if len(active_rows) == 1:
                result.append(active_rows[0])
                continue
            # si pas trouvé en mémoire
            choice_no = ask_unique_choice(unique_field, rows)
            memorize_unique_choice(
                unique_choice_memory, context, unique_field,
                unique_field_value, choice_no, len(rows))
            result.append(rows[choice_no])

    return result


def index_list_by(data, field):
    return {row[field]: row for row in data}


# +---------------------------------------------------------------------------+
# |                              Airport parsers                              |
# +---------------------------------------------------------------------------+

airport_icao = code_builder(AIRPORT_ICAO_REC)

airport_iata = code_builder(AIRPORT_IATA_REC)


def airport_type(text):
    text = text.strip().lower()
    if text in ["airport", "station", "port"]:
        return text
    return None


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
    {"parser": drop, "name": "source", "opt": "True"}
]

# +---------------------------------------------------------------------------+
# |                              Airline parsers                              |
# +---------------------------------------------------------------------------+

airline_iata = code_builder(AIRLINE_IATA_REC)

airline_icao = code_builder(AIRLINE_ICAO_REC)


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
# |                               Plane parsers                               |
# +---------------------------------------------------------------------------+

plane_iata = code_builder(PLANE_IATA_REC)

plane_icao = code_builder(PLANE_ICAO_REC)


PLANE_PARSING_RULES = lambda *memory: [
    {"parser": field_as_is_builder("plane", "name", *memory), "name": "name", "opt": False},
    {"parser": plane_iata, "name": "iata", "opt": False},
    {"parser": plane_icao, "name": "icao", "opt": True}
]


# +---------------------------------------------------------------------------+
# |                                  Testing                                  |
# +---------------------------------------------------------------------------+

def display_alert(severity, i_row, row, text):
    b, e = color_escapes(SEVERITY_TO_COLOR[severity])
    print("{}[{}] {}: {}\n    {}{}\n".format(b, severity, i_row, row, text, e))


def display_alert_field(severity, i_row, row, i_field, field_name):
    b, e = color_escapes(SEVERITY_TO_COLOR[severity])
    print("{}[{}] {}: {}\n    on {}: {}{}\n"
          .format(b, severity, i_row, row, i_field, field_name, e))


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

    with JsonPersistance(PERSISTANCE_ROOT_DIR, [
                ("unique_choice.json", dict)
            ], ask_confirmation=False) as memory:
        memory = memory[0]

        # Identification pour Plane : IATA en premier, ICAO en secours
        planes_iata_unique = make_unique(planes, "Plane", "iata", memory)
        planes_iata_to_plane = index_list_by(planes_iata_unique, "iata")
        _planes_icao_unique = make_unique(
            planes_iata_unique, "_Plane", "icao", memory)
        planes_icao_to_plane = index_list_by(_planes_icao_unique, "icao")

        # Identification pour Airport : ICAO en premier, IATA en secours
        airports_icao_unique = make_unique(airports, "Airport", "icao", memory)
        airports_icao_to_airport = index_list_by(airports_icao_unique, "icao")
        _airports_iata_unique = make_unique(
            airports_icao_unique, "_Airport", "iata", memory)
        airports_iata_to_airport = index_list_by(_airports_iata_unique, "iata")

        # Identification pour Airline : ICAO en premier, IATA en secours
        airlines_icao_unique = make_unique(airlines, "Airline", "icao", memory)
        airlines_icao_to_airline = index_list_by(airlines_icao_unique, "icao")
        _airlines_iata_unique = make_unique(
            airlines_icao_unique, "_Airline", "iata", memory)
        airlines_iata_to_airline = index_list_by(_airlines_iata_unique, "iata")


if __name__ == "__main__":
    main()
