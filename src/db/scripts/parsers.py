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

# PLACEHOLDER: global variables

ENC = "utf-8"

IATA_AIRPORT_REC = re.compile(r"^[A-Z0-9]{3}$")
ICAO_AIRPORT_REC = re.compile(r"^[A-Z0-9]{4}$")

IATA_AIRLINE_REC = re.compile(r"^[A-Z0-9]{2}$")
ICAO_AIRLINE_REC = re.compile(r"^[A-Z0-9]{3}$")

IATA_PLANE_REC = re.compile(r"^[A-Z0-9]{3}$")
ICAO_PLANE_REC = re.compile(r"^[A-Z0-9]{4}$")

# PLACEHOLDER: class declarations


# PLACEHOLDER: function declarations

def code_validator(type, name, text):
    text = text.strip().upper()
    rec_name = "{}_{}_REC".format(type.upper(), name.upper())
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
    test_codes("airport", lambda x: (x[4], x[5]))
    test_codes("airline", lambda x: (x[3], x[4]))
    test_codes("plane", lambda x: (x[1], x[2]))


if __name__ == "__main__":
    main()
