#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Fonctions utilitaires pour traiter/nettoyer les bases de données rendues
disponibles par https://openflights.org/.
"""

__author__ = "Timothée Adam, Thomas Bagrel"
__copyright__ = "Copyright 2019, PPII-A1"
__credits__ = ["Timothée Adam", "Thomas Bagrel"]
__license__ = "Private"


import csv
import sys

from pprint import pprint

from parsers import *
from persistance import *


QUIET = __name__ != "__main__" or len(sys.argv) > 1

ENC = "utf-8"

WARNING = "W"
ERROR = "E"

SEVERITY_TO_COLOR = {
    WARNING: 221,
    ERROR: 204
}

BOX_COLOR = 208
HEADLINE_COLOR = 222
IMPORTANT_COLOR = 220

RESOURCES_ROOT_DIR = "../../resources"
PERSISTANCE_ROOT_DIR = path.join(RESOURCES_ROOT_DIR, "json_persistance")


# +---------------------------------------------------------------------------+
# |                              Airport parsing                              |
# +---------------------------------------------------------------------------+

AIRPORT_PARSING_RULES = lambda *keep_edit_discard_memory: [
    {"name": "id", "parser": drop, "opt": True},
    {"name": "name", "parser": field_as_is_builder(
        "airport", "name", *keep_edit_discard_memory), "opt": False},
    {"name": "city", "parser": field_as_is_builder(
        "airport", "city", *keep_edit_discard_memory), "opt": True},
    {"name": "country", "parser": field_as_is_builder(
        "airport", "country", *keep_edit_discard_memory), "opt": False},
    {"name": "iata", "parser": airport_iata, "opt": True},
    {"name": "icao", "parser": airport_icao, "opt": False},
    {"name": "latitude", "parser": latitude, "opt": False},
    {"name": "longitude", "parser": longitude, "opt": False},
    {"name": "altitude", "parser": altitude_with_ft_to_m_conversion,
     "opt": True},
    {"name": "utc_offset", "parser": utc_offset, "opt": True},
    {"name": "daylight_saving_group", "parser": daylight_saving_group,
     "opt": True},
    {"name": "tz_name", "parser": tz_name, "opt": True},
    {"name": "type", "parser": airport_type, "opt": True},
    {"name": "data_source", "parser": airport_data_source, "opt": True}
]


# +---------------------------------------------------------------------------+
# |                              Airline parsing                              |
# +---------------------------------------------------------------------------+

AIRLINE_PARSING_RULES = lambda *keep_edit_discard_memory: [
    {"name": "id", "parser": drop, "opt": True},
    {"name": "name", "parser": field_as_is_builder(
        "airline", "name", *keep_edit_discard_memory), "opt": False},
    {"name": "alias", "parser": field_as_is_builder(
        "airline", "alias", *keep_edit_discard_memory), "opt": True},
    {"name": "iata", "parser": airline_iata, "opt": True},
    {"name": "icao", "parser": airline_icao, "opt": False},
    {"name": "callsign", "parser": field_as_is_builder(
        "airline", "callsign", *keep_edit_discard_memory), "opt": True},
    {"name": "country", "parser": field_as_is_builder(
        "airline", "country", *keep_edit_discard_memory), "opt": True},
    {"name": "is_active", "parser": yes_no, "opt": True}
]


# +---------------------------------------------------------------------------+
# |                               Plane parsing                               |
# +---------------------------------------------------------------------------+

PLANE_PARSING_RULES = lambda *keep_edit_discard_memory: [
    {"name": "name", "parser": field_as_is_builder(
        "plane", "name", *keep_edit_discard_memory), "opt": False},
    {"name": "iata", "parser": plane_iata, "opt": False},
    {"name": "icao", "parser": plane_icao, "opt": True}
]


# +---------------------------------------------------------------------------+
# |                               Route parsing                               |
# +---------------------------------------------------------------------------+

ROUTE_PARSING_RULES = lambda iata_to_plane, icao_to_plane, \
                             icao_to_airport, iata_to_airport, \
                             icao_to_airline, iata_to_airline: [
    {"name": "airline_icao", "parser": get_default_index_builder(
        "icao", icao_to_airline, iata_to_airline), "opt": False},
    {"name": "airline_openflights_id", "parser": drop, "opt": True},
    {"name": "source_airport_icao", "parser": get_default_index_builder(
        "icao", icao_to_airport, iata_to_airport), "opt": False},
    {"name": "source_airport_openflights_id", "parser": drop, "opt": True},
    {"name": "destination_airport_icao", "parser": get_default_index_builder(
        "icao", icao_to_airport, iata_to_airport), "opt": False},
    {"name": "destination_airport_openflights_id", "parser": drop,
     "opt": True},
    {"name": "is_codeshare", "parser": yes_no, "opt": True},
    {"name": "real_step_nb", "parser": composed_builder(
        parse_int, lambda stop_nb: stop_nb + 2), "opt": True},
    {"name": "fleet_tuple", "parser": sorted_tuple_builder(
        get_default_index_builder("iata", iata_to_plane, icao_to_plane),
        separator=" ", strict=False, min=1, max=None), "opt": True}
]


# +---------------------------------------------------------------------------+
# |                              Flight parsing                               |
# +---------------------------------------------------------------------------+

FLIGHT_PARSING_RULES = lambda iata_to_plane, icao_to_plane, \
                              icao_to_airport, iata_to_airport, \
                              icao_to_airline, iata_to_airline: [
    {"name": "airline_icao", "parser": get_default_index_builder(
        "icao", icao_to_airline, iata_to_airline), "opt": False},
    {"name": "flight_no", "parser": flight_no, "opt": True},
    {"name": "path_tuple", "parser": ordered_tuple_builder(
        get_default_index_builder("icao", icao_to_airport, iata_to_airport),
        separator="-", strict=True, min=2, max=None), "opt": False}
]


# +---------------------------------------------------------------------------+

def print_box(text, columns=80, add_new_line=True):
    f = columns - len(text) - 4
    l = f // 2
    r = f - l
    b, e = color_escapes(BOX_COLOR)
    sys.stdout.write(b)
    print("+{}+".format("-" * (columns - 2)))
    print("| {}{}{} |".format(" " * l, text, " " * r))
    print("+{}+".format("-" * (columns - 2)))
    sys.stdout.write(e)
    if add_new_line:
        print()


def print_headline(text, columns=80, add_new_line=True):
    f = columns - len(text) - 2
    l = f // 2
    r = f - l
    b, e = color_escapes(HEADLINE_COLOR)
    sys.stdout.write(b)
    print("{} {} {}".format("=" * l, text, "=" * r))
    sys.stdout.write(e)
    if add_new_line:
        print()


def color_escapes(color_code):
    return "\u001b[38;5;{}m".format(color_code), "\u001b[0m"


def display_alert(severity, i_row, row, text):
    if QUIET:
        return
    b, e = color_escapes(SEVERITY_TO_COLOR[severity])
    print("{}[{}] {}: {}\n    {}{}\n".format(b, severity, i_row, row, text, e))


def display_alert_field(severity, i_row, row, i_field, field_name):
    if QUIET:
        return
    b, e = color_escapes(SEVERITY_TO_COLOR[severity])
    print("{}[{}] {}: {}\n    on {}: {}{}\n"
          .format(b, severity, i_row, row, i_field, field_name, e))


# +---------------------------------------------------------------------------+

def parse_table(input_path, table_name, parsing_rules_func, *to_inject):
    """
    Lit le fichier identifié par input_path, et parse son contenu suivant la
    table de règles table_parsing_rules_func.
    :param input_path: chemin vers le fichier à parser
    :param table_name: nom de la table résultante
    :param parsing_rules_func: règles de parsing, chacune sous la forme
                               {"name": ???, "parser": ???, "opt": True/False}
                               - name est le nom du champ résultant,
                               - parser est la fonction traitant ce champ,
                               - opt un booléen indiquant si ce champ est
                                 optionnel ou non
    :param to_inject: paramètres à passer à la fonction-liste des règles de
                      parsage
    :return: une liste de dictionnaires, chacun correspondant à une ligne du
             fichier d'entrée
    """
    print_headline(table_name)

    with open(input_path, "r", encoding=ENC) as input_file:
        csv_reader = csv.reader(input_file, delimiter=",", quotechar="\"")
        data = [list(row) for row in csv_reader]

    parsing_rules = parsing_rules_func(*to_inject)
    n = len(parsing_rules)

    output_data = []
    valid_rows = 0

    for i_row, row in enumerate(data):
        if len(row) > len(parsing_rules):
            display_alert(
                WARNING, i_row, row, "len(row): {} > len(parsers): {}"
                                     .format(len(row), n))
        if len(row) < len(parsing_rules):
            display_alert(
                ERROR, i_row, row, "len(row): {} < len(parsers): {}"
                                   .format(len(row), n))
            continue

        output_row = {}
        valid = True

        for i_field, (field_format, field) in enumerate(
                zip(parsing_rules, row)):
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

    b, e = color_escapes(IMPORTANT_COLOR)
    print("\n{}|> Valid rows: {} / {} ({:.2f} %){}".format(
        b, valid_rows, len(data), valid_rows * 100 / len(data), e))

    return output_data


def index_table_by(
        rows, table_name, default_index, fallback_index, unique_choice_memory):
    """
    Indexe la table spécifiée selon un index primaire (qui deviendra un
    identifiant unique de chaque ligne) et un identifiant secondaire (qui peut
    lui ne pas être unique).
    :param rows: table à traiter (liste de dictionnaires)
    :param table_name: nom de la table
    :param default_index: nom du champ, présent dans chaque ligne de la table,
                          qui sera utilisé comme index primaire (unique)
    :param fallback_index: nom du champ qui sera utilisé comme index secondaire
    :param unique_choice_memory: dictionnaire de persistance utilisé pour se
                                 souvenir des choix d'unicité réalisés
    :return: un tuple contenant :
             - la table (sous forme de liste de dictionnaires), où l'unicité de
               l'index primaire est assurée
             - un dictionnaire (de dictionnaires) donnant pour chaque index
               primaire la ligne associée
             - un dictionnaire (de dictionnaires) donnant pour chaque index
               secondaire la ligne associée
    """

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
    new_routes = []

    for route in routes:
        if route["source_airport_icao"] == route["destination_airport_icao"]:
            continue

        route["path_tuple"] = (
            route["source_airport_icao"],
            route["destination_airport_icao"]
        )

        del route["source_airport_icao"]
        del route["destination_airport_icao"]

        new_routes.append(route)

    return new_routes


def path_length(icao_to_airport, path_tuple):
    """
    Calcule la longueur du chemin spécifié, défini par un tuple d'ICAO
    d'aéroports.
    :param icao_to_airport: données sur les aéroports, sous forme d'un
                            dictionnaire ICAO => aéroport
    :param path_tuple: chemin dont on veut calculer la longueur
    :return:
    """

    # TODO implémenter le calcul des distances
    return 0.0


def extract_paths(exploitations, icao_to_airport):
    """
    Modifie en place la table exploitations spécifiée afin de remplacer les
    champs path_tuple et real_step_nb par le champ path_id, et créé une table
    paths contenant les informations sur les chemins extraites de la table
    exploitations.
    :param exploitations: table exploitations à modifier
    :param icao_to_airport: données sur les aéroports, sous forme d'un
                            dictionnaire ICAO => aéroport
    :return: la nouvelle table paths
    """

    pt_rsn_to_path = {}
    next_path_id = 0
    for exploitation in exploitations:
        path_tuple, real_step_nb = \
            exploitation["path_tuple"], exploitation["real_step_nb"]
        if (path_tuple, real_step_nb) not in pt_rsn_to_path:
            path_id = next_path_id
            next_path_id += 1

            pt_rsn_to_path[(path_tuple, real_step_nb)] = {
                "id": path_id,
                "real_step_nb": real_step_nb,
                "db_step_nb": len(path_tuple),
                "real_distance": (
                    None if real_step_nb != len(path_tuple) is None
                    else path_length(icao_to_airport, path_tuple)),
                "straight_distance": path_length(
                    icao_to_airport, (path_tuple[0], path_tuple[:-1])),
                "path_tuple": path_tuple
            }
        else:
            path_id = pt_rsn_to_path[(path_tuple, real_step_nb)]["id"]
        exploitation["path_id"] = path_id
        del exploitation["path_tuple"]
        del exploitation["real_step_nb"]

    return list(pt_rsn_to_path.values())


def extract_airports_paths(paths):
    """
    Modifie en place la table paths spécifiée afin de supprimer le champ
    path_tuple, tout en créant à côté une table airports_paths représentant
    les étapes de chaque chemin de paths.
    :param paths: la table paths à modifier
    :return: la nouvelle table airports_paths
    """
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
    """
    Modifie en place la table exploitations spécifiée afin de remplacer le
    champ fleet_tuple par le champ fleet_id, et créé une table fleets contenant
    les informations sur les flottes extraites de la table exploitations.
    :param exploitations: table exploitations à modifier
    :return: la nouvelle table fleets
    """
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
    """
    Modifie en place la table fleets spécifiée afin de supprimer le champ
    fleet_tuple, tout en créant à côté une table planes_fleets représentant
    les avions de chaque flotte de fleets.
    :param fleets: la table fleets à modifier
    :return: la nouvelle table planes_fleets
    """
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


def print_summary(tables, max_displayed=10):
    for name, table in tables.items():
        print_headline("{} [{}]".format(name, len(table)))
        n = min(max_displayed, len(table))
        for row in table[:n]:
            pprint(row)
            print()


def get_final_tables():
    # On commence par parser les tables planes, airports, et airlines car elles
    # peuvent être parsées individuellement

    print_box("Parsing of Plane, Airport and Airline")

    with JsonPersistence(PERSISTANCE_ROOT_DIR, [
                ("to_keep.json", dict),
                ("to_edit.json", dict),
                ("to_discard.json", dict),
            ], ask_confirmation=False) as keep_edit_discard_memory:

        planes = parse_table(
            path.join(RESOURCES_ROOT_DIR, "planes.dat"), "Plane",
            PLANE_PARSING_RULES, *keep_edit_discard_memory)
        add_new_fields(planes, [
            ("speed", None),
            ("capacity", None),
            ("co2_emission", None)])
        print("\n")

        airports = parse_table(
            path.join(RESOURCES_ROOT_DIR, "airports.dat"), "Airport",
            AIRPORT_PARSING_RULES, *keep_edit_discard_memory)
        print("\n")

        airlines = parse_table(
            path.join(RESOURCES_ROOT_DIR, "airlines.dat"), "Airline",
            AIRLINE_PARSING_RULES, *keep_edit_discard_memory)

    print_box("Indexing of Plane, Airport and Airline (unicity)")

    # On enforce l'unicité des clés primaires de chaque table avec un appel à
    # index_table_by

    with JsonPersistence(PERSISTANCE_ROOT_DIR, [
                ("unique_choice.json", dict)
            ], ask_confirmation=False) as persistance:
        keep_edit_discard_memory = persistance[0]

        # Identification pour Plane : IATA en premier, ICAO en secours
        planes, iata_to_plane, icao_to_plane = \
            index_table_by(
                planes, "Plane", "iata", "icao", keep_edit_discard_memory)

        # Identification pour Airport : ICAO en premier, IATA en secours
        airports, icao_to_airport, iata_to_airport = \
            index_table_by(
                airports, "Airport", "icao", "iata", keep_edit_discard_memory)

        # Identification pour Airline : ICAO en premier, IATA en secours
        airlines, icao_to_airline, iata_to_airline = \
            index_table_by(
                airlines, "Airline", "icao", "iata", keep_edit_discard_memory)

    maps = (
        iata_to_plane, icao_to_plane,
        icao_to_airport, iata_to_airport,
        icao_to_airline, iata_to_airline
    )

    print_box("Parsing of Route and Flight")

    # On parse ensuite les tables routes et flights, pour lesquelles on doit
    # vérifier l'existence des IATAs et ICAOs dans les maps créées avec la
    # fonction index_table_by
    # On réajuste également le schéma de ces tables avec
    # replace_source_destination_by_path et add_new_fields

    routes = parse_table(
        path.join(RESOURCES_ROOT_DIR, "routes.dat"),
        "Route", ROUTE_PARSING_RULES, *maps)
    routes = replace_source_destination_by_path(routes)
    add_new_fields(routes, [
        ("flight_no", "UNKNOW")])
    print("\n")

    flights = parse_table(
        path.join(RESOURCES_ROOT_DIR, "flights.dat"),
        "Flight", FLIGHT_PARSING_RULES, *maps)
    add_new_fields(flights, [
        ("fleet_tuple", None),
        ("real_step_nb", lambda row: len(row["path_tuple"])),
        ("is_codeshare", None)])

    # Les tables routes et flights ont la même structure maintenant, on peut
    # les fusionner en la table exploitations
    exploitations = routes + flights

    # On extrait enfin paths, fleets de la table exploitation...
    paths = extract_paths(exploitations, icao_to_airport)
    fleets = extract_fleets(exploitations)

    # ...puis on extrait airports_paths de paths et planes_fleets de fleets
    airports_paths = extract_airports_paths(paths)
    planes_fleets = extract_planes_fleets(fleets)

    # Done !

    tables = {
        "Airport": airports,
        "Airline": airlines,
        "Plane": planes,
        "Exploitation": exploitations,
        "Path": paths,
        "AirportPath": airports_paths,
        "Fleet": fleets,
        "PlaneFleet": planes_fleets
    }

    print()
    print_box("Summary")
    print_summary(tables, max_displayed=2)

    return tables


if __name__ == "__main__":
    get_final_tables()

