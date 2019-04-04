#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Fonctions utilitaires pour traiter/nettoyer les bases de données rendues
disponibles par https://openflights.org/.
"""

__author__ = "Thimothée Adam, Thomas Bagrel"
__copyright__ = "Copyright 2019, PPII-A1"
__credits__ = ["Thimothée Adam", "Thomas Bagrel"]
__license__ = "Private"


# PLACEHOLDER: imports

from transliterate import translit
import csv
import re
import json
import string

# PLACEHOLDER: global variables

ENC = "utf-8"

AIRPORT_IATA_REC = re.compile(r"^[A-Z0-9]{3}$")
AIRPORT_ICAO_REC = re.compile(r"^[A-Z0-9]{4}$")

AIRLINE_IATA_REC = re.compile(r"^[A-Z0-9]{2}$")
AIRLINE_ICAO_REC = re.compile(r"^[A-Z0-9]{3}$")

PLANE_IATA_REC = re.compile(r"^[A-Z0-9]{3}$")
PLANE_ICAO_REC = re.compile(r"^[A-Z0-9]{4}$")

TZ_OLSON_NAME_REC = re.compile(r"^[-A-Za-z_]{1,14}/[-A-Za-z_]{1,14}$")

DROP = -1

FT_TO_M = 0.3048

def code_validator_builder(rec):
    def validator(text):
        text = text.strip().upper()
        if rec.search(text) is not None:
            return text
        text = translit(text, "ru", reversed=True)
        if rec.search(text) is not None:
            return text
        return None
    return validator


def save_to_live(names_types):
    for name, type_ in names_types:
        try:
            path = "resources/{}.json".format(name)
            with open(path, "r", encoding="utf-8") as save_file:
                globals()[name] = json.load(save_file)
                print("--- LOADED: {}".format(path))
        except:
            globals()[name] = type_()
            print("--- CREATED: {}".format(name))
    print("\n")


def live_to_save(names):
    choice = input("\n\n Save filtered strings? [Yes/no] ").lower()
    if choice in ["n", "no"]:
        return
    for name in names:
        path = "resources/{}.json".format(name)
        with open(path, "w", encoding="utf-8") as save_file:
            json.dump(globals()[name], save_file)
            print("--- SAVED: {}".format(path))


save_to_live([
    ("to_keep", list),
    ("to_discard", list),
    ("to_edit", dict)
])


def is_strange(text):
    if len(text) <= 1:
        return True
    count = 0
    for letter in text:
        if letter in string.ascii_letters + " ":
            count += 1
    ascii_ratio = count / len(text)
    if ascii_ratio < 0.5:
        return True
    return False


def keep_edit_discard(field, value):
    choice = input("{}: >>>{}<<< [keep/edit/Discard]? ".format(field, value)).lower()
    if choice in ["k", "keep"]:
        to_keep.append(value)
        print()
        return value
    if choice in ["e", "edit"]:
        new_value = input("Replacement: >>>")
        choice = input("New {}: >>>{}<<< [Yes/no]? ".format(field, new_value)).lower()
        if choice in ["n", "no"]:
            return keep_edit_discard(field, value)
        to_edit[value] = new_value
        print()
        return new_value
    to_discard.append(value)
    print()
    return None


def field_as_is(field):
    def _as_is(text):
        text = text.strip()
        if text == "\\N" or not text:
            return None
        if text in to_keep:
            return text
        if text in to_edit:
            return to_edit[text]
        if text in to_discard:
            return None
        if is_strange(text):
            return keep_edit_discard(field, text)
        return text
    return _as_is


def parse_float(text):
    text = text.strip()
    try:
        return float(text)
    except:
        return None


def drop(text):
    return None


city = field_as_is("city")

country = field_as_is("country")


def long(text):
    val = parse_float(text)
    if val is not None and -180.0 <= val < 180.0:
        return val
    return None


def lat(text):
    val = parse_float(text)
    if val is not None and -90.0 <= val < 90.0:
        return val
    return None


def altitude_with_ft_to_m_conversion(text):
    val = parse_float(text)
    if val is not None:
        val *= FT_TO_M
        if -1000 <= val <= 9000:
            return val
    return None


def utc_offset(text):
    val = parse_float(text)
    if val is not None and -12.0 <= val <= 14.0:
        return val
    return None


def daylight_saving_group(text):
    text = text.strip().upper()
    if text in ["E", "A", "S", "O", "Z", "N"]:
        return text
    return None


def tz_name(text):
    text = text.strip()
    if TZ_OLSON_NAME_REC.search(text) is not None:
        return text
    return None


def yes_no(text):
    text = text.strip().lower()
    if text == "y":
        return True
    if text == "n":
        return False
    return None


# +---------------------------------------------------------------------------+
# |                              Airport parsers                              |
# +---------------------------------------------------------------------------+

airport_icao = code_validator_builder(AIRPORT_ICAO_REC)

airport_iata = code_validator_builder(AIRPORT_IATA_REC)

airport_name = field_as_is("name")


def airport_type(text):
    text = text.strip().lower()
    if text in ["airport", "station", "port"]:
        return text
    return None


AIRPORT_OUTPUT_RULES = {
    "length": 12,
    "format": [
        {"parser": drop, "pos": DROP, "name": "id", "opt": True},
        {"parser": airport_name, "pos": 2, "name": "name", "opt": False},
        {"parser": city, "pos": 4, "name": "city", "opt": True},
        {"parser": country, "pos": 5, "name": "country", "opt": False},
        {"parser": airport_iata, "pos": 1, "name": "iata", "opt": True},
        {"parser": airport_icao, "pos": 0, "name": "icao", "opt": False},
        {"parser": lat, "pos": 7, "name": "lat", "opt": False},
        {"parser": long, "pos": 6, "name": "long", "opt": False},
        {"parser": altitude_with_ft_to_m_conversion, "pos": 8, "name": "altitude", "opt": True},
        {"parser": utc_offset, "pos": 9, "name": "utc_offset", "opt": True},
        {"parser": daylight_saving_group, "pos": 10, "name": "daylight_saving_group", "opt": True},
        {"parser": tz_name, "pos": 11, "name": "tz_name", "opt": True},
        {"parser": airport_type, "pos": 3, "name": "type", "opt": True},
        {"parser": drop, "pos": DROP, "name": "source", "opt": "True"}
    ]
}

# +---------------------------------------------------------------------------+
# |                              Airline parsers                              |
# +---------------------------------------------------------------------------+

airline_iata = code_validator_builder(AIRLINE_IATA_REC)

airline_icao = code_validator_builder(AIRLINE_ICAO_REC)

airline_name = field_as_is("name")

airline_alias = field_as_is("alias")

airline_callsign = field_as_is("callsign")

AIRLINE_OUTPUT_RULES = {
    "length": 7,
    "format": [
        {"parser": drop, "pos": DROP, "name": "id", "opt": True},
        {"parser": airline_name, "pos": 2, "name": "name", "opt": False},
        {"parser": airline_alias, "pos": 3, "name": "alias", "opt": True},
        {"parser": airline_iata, "pos": 1, "name": "iata", "opt": True},
        {"parser": airline_icao, "pos": 0, "name": "icao", "opt": False},
        {"parser": airline_callsign, "pos": 4, "name": "callsign", "opt": True},
        {"parser": country, "pos": 5, "name": "country", "opt": True},
        {"parser": yes_no, "pos": 6, "name": "is_active", "opt": True}
    ]
}

# +---------------------------------------------------------------------------+
# |                               Plane parsers                               |
# +---------------------------------------------------------------------------+

plane_iata = code_validator_builder(PLANE_IATA_REC)

plane_icao = code_validator_builder(PLANE_ICAO_REC)

plane_name = field_as_is("name")

PLANE_OUTPUT_RULES = {
    "length": 3,
    "format": [
        {"parser": plane_name, "pos": 2, "name": "name", "opt": False},
        {"parser": plane_iata, "pos": 0, "name": "iata", "opt": False},
        {"parser": plane_icao, "pos": 1, "name": "icao", "opt": True}
    ]
}

# +---------------------------------------------------------------------------+
# |                                  Testing                                  |
# +---------------------------------------------------------------------------+

def display_alert(severity, i_row, row, text):
    print("[{}] {}: {}\n    {}".format(severity, i_row, row, text))


def display_alert_field(severity, i_row, row, i_field, field_name):
    print("[{}] {}: {}\n    on {}: {}".format(severity, i_row, row, i_field, field_name))


def parse_table(input_path, table_name, table_output_rules, output_as_lists=False):
    print("======== {} ========\n".format(table_name))

    with open(input_path, "r", encoding=ENC) as input_file:
        csv_reader = csv.reader(input_file, delimiter=",", quotechar="\"")
        data = [list(row) for row in csv_reader]

    output_length = table_output_rules["length"]
    output_parsers = table_output_rules["format"]

    output_data = []

    valid_rows = 0

    for i_row, row in enumerate(data):
        if len(row) > len(output_parsers):
            display_alert("W", i_row, row, "len(row): {} > len(parsers): {}"
                          .format(len(row), len(output_parsers)))
        if len(row) < len(output_parsers):
            display_alert("E", i_row, row, "len(row): {} < len(parsers): {}"
                          .format(len(row), len(output_parsers)))
            continue

        output_row = {}
        valid = True

        for i_field, (field_format, field) in enumerate(zip(output_parsers, row)):
            if field_format["parser"] == drop:
                continue
            result = field_format["parser"](field)
            if result is None and not field_format["opt"]:
                display_alert_field("E", i_row, row, i_field, field_format["name"])
                valid = False
                break
            output_row[field_format["name"]] = result

        if valid:
            output_data.append(output_row)
            valid_rows += 1

    print("\n--- Valid rows: {} / {} ({:.2f} %)".format(valid_rows, len(data), valid_rows * 100 / len(data)))

    if output_as_lists:
        output_lists = []
        for output_row in output_data:
            output_list = [None] * output_length
            for field_format in output_parsers:
                if field_format["parser"] == drop:
                    continue
                output_list[field_format["pos"]] = output_row[field_format["name"]]
            output_lists.append(output_list)
        return output_lists

    return output_data


def code_validator(type_, name, text):
    text = text.strip().upper()
    rec_name = "{}_{}_REC".format(name.upper(), type_.upper())
    if globals()[rec_name].search(text) is not None:
        return text
    text = translit(text, "ru", reversed=True)
    if globals()[rec_name].search(text) is not None:
        return text
    return None


def test_codes(name, extract_iata_icao):
    print("===== {}S =====\n".format(name.upper()))

    with open("resources/{}s.dat".format(name), "r", encoding=ENC) as file:
        parser = csv.reader(file, delimiter=",", quotechar="\"")
        data = [list(row) for row in parser]

    iata_errors, icao_errors = set(), set()
    valid_iata_count, valid_icao_count = 0, 0

    for iata, icao in map(extract_iata_icao, data):
        if code_validator("iata", name, iata) is None:
            iata_errors.add(iata)
        else:
            valid_iata_count += 1

        if code_validator("icao", name, icao) is None:
            icao_errors.add(icao)
        else:
            valid_icao_count += 1

    print("valid IATAs: {} / {} ({:.2f} %)".format(valid_iata_count, len(data), 100 * valid_iata_count / len(data)))
    print("valid ICAOs: {} / {} ({:.2f} %)".format(valid_icao_count, len(data), 100 * valid_icao_count / len(data)))
    print()
    print("erroneous IATAs: {}".format(iata_errors))
    print("erroneous ICAOs: {}".format(icao_errors))
    print("\n")


def main():
    """Si le module est lancé directement (ie n'est pas un import)."""
    # test_codes("airport", lambda x: (x[4], x[5]))
    # test_codes("airline", lambda x: (x[3], x[4]))
    # test_codes("plane", lambda x: (x[1], x[2]))

    res = parse_table("resources/planes.dat", "Plane", PLANE_OUTPUT_RULES, True)
    # res = parse_table("resources/airports.dat", "Airport", AIRPORT_OUTPUT_RULES, True)
    # res = parse_table("resources/airlines.dat", "Airline", AIRLINE_OUTPUT_RULES, True)
    print(res[:min(len(res), 200)])


if __name__ == "__main__":
    main()

live_to_save([
    "to_keep",
    "to_discard",
    "to_edit"
])
