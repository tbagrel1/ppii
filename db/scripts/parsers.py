#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Parsers pour traiter/nettoyer les bases de données rendues disponibles par
https://openflights.org/.
"""

__author__ = "Timothée Adam, Thomas Bagrel"
__copyright__ = "Copyright 2019, PPII-A1"
__credits__ = ["Thimothée Adam", "Thomas Bagrel"]
__license__ = "Private"


from transliterate import translit

import re
import string


AIRPORT_IATA_REC = re.compile(r"^[A-Z0-9]{3}$")
AIRPORT_ICAO_REC = re.compile(r"^[A-Z0-9]{4}$")

AIRLINE_IATA_REC = re.compile(r"^[A-Z0-9]{2}$")
AIRLINE_ICAO_REC = re.compile(r"^[A-Z0-9]{3}$")

PLANE_IATA_REC = re.compile(r"^[A-Z0-9]{3}$")
PLANE_ICAO_REC = re.compile(r"^[A-Z0-9]{4}$")

FLIGHT_NO_REC = re.compile(r"^[A-Z0-9]{1,8}$")

TZ_OLSON_NAME_REC = re.compile(r"^[-A-Za-z_]{1,14}/[-A-Za-z_]{1,14}$")

FT_TO_M = 0.3048


def is_strange(text):
    """
    Détecte si le texte passé en paramètre ne semble pas être un nom valide.

    :param text: le nom/texte à tester

    :return: True ssi le texte semble être un nom invalide
    """
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


def memorize_keep(to_keep, context, field, text):
    if context not in to_keep:
        to_keep[context] = {}
    if field not in to_keep[context]:
        to_keep[context][field] = []
    to_keep[context][field].append(text)


def memorize_edit(to_edit, context, field, text, new_text):
    if context not in to_edit:
        to_edit[context] = {}
    if field not in to_edit[context]:
        to_edit[context][field] = {}
    to_edit[context][field][text] = new_text


def memorize_discard(to_discard, context, field, text):
    if context not in to_discard:
        to_discard[context] = {}
    if field not in to_discard[context]:
        to_discard[context][field] = []
    to_discard[context][field].append(text)


def is_memorized(to_, context, field, text):
    if context not in to_:
        return False
    if field not in to_[context]:
        return False
    return text in to_[context][field]


def ask_user_about(context, field, text, to_keep, to_edit, to_discard):
    """
    Demande à l'utilisateur que faire à propos d'une valeur détectée comme
    étrange (garder intact, modifier, invalider).
    Retourne la valeur finale correspondant au choix de l'utilisateur, et
    enregistre ce choix si la valeur réapparaît dans le même contexte

    :param field: nom du champ dont la valeur est soumise à un contrôle de
                  l'utilisateur
    :param text: valeur soumise au contrôle de l'utilisateur
    :param context: nom de la table (contexte) à laquelle la valeur appartient
    :param to_keep: dictionnaire par contexte des valeurs enregistrées comme
                    étant à garder
    :param to_edit: dictionnaire par contexte des valeurs enregistrées comme
                    étant à modifier, avec leur nouvelle valeur
    :param to_discard: dictionnaire par contexte des valeurs enregistrées comme
                       étant à jeter

    :return: - la valeur originale si l'utilisateur choisit de la conserver
             - la valeur modifiée si l'utilisateur choisit de modifier la
               valeur originale
             - None si l'utilisateur choisit de ne pas conserver cette valeur
    """
    choice = input((
        "[{} {}]: {}\n"
        "    [K]eep\n"
        "    [E]dit\n"
        "    [D]iscard (default)\n"
        ">>> "
    ).format(context, field, text)).strip().lower()
    print()

    if choice in ["k", "keep"]:
        memorize_keep(to_keep, context, field, text)
        return text

    if choice in ["e", "edit"]:
        new_text = input("[{} {} (new)]: ".format(context, field))
        choice = input(
            "Is the new text ok?\n"
            "    [Y]es (default)\n"
            "    [N]o\n"
            ">>> "
        ).strip().lower()
        if choice in ["n", "no"]:
            # On rappelle la méthode pour laisser une seconde chance à
            # l'utilisateur
            print()
            return ask_user_about(
                field, text, context, to_keep, to_edit, to_discard)
        # On enregistre la nouvelle valeur
        memorize_edit(to_edit, context, field, text, new_text)
        return new_text

    # On jette la valeur
    memorize_discard(to_discard, context, field, text)
    return None


def code_builder(rec):
    """
    Construit une fonction de validation (parser) pour un code type IATA,
    ICAO... à partir d'une regex compilée

    :param rec: la regex compilée servant de base au parser

    :return: le parser construit à partir de la regex
    """
    def code(text):
        """
        Parser pour un code type IATA, ICAO construit à partir d'une regex

        :param text: le texte à tester/valider

        :return: le texte (éventuellement normalisé) si celui-ci correspond à
                 ce qui est attendu, None sinon
        """
        text = text.strip().upper()
        if rec.search(text) is not None:
            return text
        text = translit(text, "ru", reversed=True)
        if rec.search(text) is not None:
            return text
        return None

    return code


def field_as_is_builder(context, field, to_keep, to_edit, to_discard):
    """
    Construit un parser pour un champ d'une table représentant un nom ou une
    chaîne ne pouvant être validée par une regex.

    :param context: nom de la table
    :param field: nom du champ dans la table
    :param to_keep: dictionnaire par contexte des valeurs enregistrées comme
                    étant à garder
    :param to_edit: dictionnaire par contexte des valeurs enregistrées comme
                    étant à modifier, avec leur nouvelle valeur
    :param to_discard: dictionnaire par contexte des valeurs enregistrées comme
                       étant à jeter

    :return: un parser pour ce champ particulier
    """

    def field_as_is(text):
        """
        Parser pour un nom ou une chaîne d'une table ne pouvant être validée
        par une regex

        :param text: le texte à tester/valider
        :return: le texte (éventuellement normalisé) si celui-ci est jugé
                 valide, None sinon
        """
        text = text.strip()
        if not text or text == "\\N":
            return None
        if is_memorized(to_keep, context, field, text):
            return text
        if is_memorized(to_edit, context, field, text):
            # Renvoie la valeur de remplacement
            return to_edit[context][field][text]
        if is_memorized(to_discard, context, field, text):
            return None
        if is_strange(text):
            return ask_user_about(
                context, field, text, to_keep, to_edit, to_discard)

        # Si rien d'anormal n'a été détecté, et que cette valeur n'a pas été
        # vue auparavant
        return text

    return field_as_is


def get_primary_key_builder(default_index, default_map, fallback_map):

    def get_primary_key(text):
        text = text.strip()
        if text in default_map:
            return text
        if text in fallback_map:
            return fallback_map[text][default_index]

        return None

    return get_primary_key


def parse_float(text):
    """
    Parser pour un flottant

    :param text: le texte à tester/valider

    :return: la valeur numérique correspondante si le texte est valide,
             None sinon
    """
    text = text.strip()
    try:
        return float(text)
    except Exception as _:
        return None


def parse_int(text):
    """
    Parser pour un entier

    :param text: le texte à tester/valider

    :return: la valeur numérique correspondante si le texte est valide,
             None sinon
    """
    text = text.strip()
    try:
        return int(text)
    except Exception as _:
        return None


def drop(text):
    """
    Parser retournant None peu importe la valeur passée en paramètre

    :param text: le texte à tester/valider

    :return: None (toujours)
    """
    return None


def long(text):
    """
    Parser pour la longitude

    :param text: le texte à tester/valider

    :return: la valeur numérique correspondante si valide
    """
    val = parse_float(text)
    if val is not None and -180.0 <= val < 180.0:
        return val
    return None


def lat(text):
    """
    Parser pour la latitude

    :param text: le texte à tester/valider

    :return: la valeur numérique correspondante si valide
    """
    val = parse_float(text)
    if val is not None and -90.0 <= val < 90.0:
        return val
    return None


def altitude_with_ft_to_m_conversion(text):
    """
    Parser pour l'altitude, avec conversion des pieds (ft) en mètres

    :param text: le texte à tester/valider

    :return: la valeur numérique correspondante et convertie si valide
    """
    val = parse_float(text)
    if val is not None:
        val *= FT_TO_M
        if -1000 <= val <= 9000:
            return val
    return None


def utc_offset(text):
    """
    Parser pour le décalage horaire

    :param text: le texte à tester/valider

    :return: la valeur numérique correspondante si valide
    """
    val = parse_float(text)
    if val is not None and -12.0 <= val <= 14.0:
        return val
    return None


def daylight_saving_group(text):
    """
    Parser pour le mode de fonctionnement heure d'été/hiver

    :param text: le texte à tester/valider

    :return: l'identifiant du mode si ce dernier est valide
    """
    text = text.strip().upper()
    if text in ["E", "A", "S", "O", "Z", "N"]:
        return text
    return None


def tz_name(text):
    """
    Parser pour le nom du fuseau horaire

    :param text: le texte à tester/valider

    :return: le nom (éventuellement normalisé) du fuseau horaire si valide
    """
    text = text.strip()
    if TZ_OLSON_NAME_REC.search(text) is not None:
        return text
    return None


def yes_no(text):
    """
    Parser pour un champ du type Yes/No

    :param text: le texte à tester/valider

    :return: True pour yes, False pour no
    """
    text = text.strip().lower()
    if text == "y":
        return True
    if text == "n":
        return False
    return None


def sorted_tuple(parser, separator=" ", strict=False, min=1, max=None):
    def _sorted_tuple(text):
        text = text.strip()
        result = []
        for elt in text.split(separator):
            elt = elt.strip()
            parsed_elt = parser(elt)
            if parsed_elt is None:
                if strict:
                    return None
            else:
                result.append(parsed_elt)
        if (min is not None and len(result) < min) or (max is not None and len(result) > max):
            return None

        return tuple(sorted(result))

    return _sorted_tuple


def ordered_tuple(parser, separator=" ", strict=False, min=1, max=None):
    def _ordered_tuple(text):
        text = text.strip()
        result = []
        for elt in text.split(separator):
            elt = elt.strip()
            parsed_elt = parser(elt)
            if parsed_elt is None:
                if strict:
                    return None
            else:
                result.append(parsed_elt)
        if (min is not None and len(result) < min) or (max is not None and len(result) > max):
            return None

        return tuple(result)

    return _ordered_tuple


# +---------------------------------------------------------------------------+


airport_icao = code_builder(AIRPORT_ICAO_REC)

airport_iata = code_builder(AIRPORT_IATA_REC)


def airport_type(text):
    text = text.strip().lower()
    if text in ["airport", "station", "port"]:
        return text
    return None


def airport_data_source(text):
    text = text.strip()
    if text in ["OurAirports", "Legacy", "User"]:
        return text
    return None


# +---------------------------------------------------------------------------+

airline_iata = code_builder(AIRLINE_IATA_REC)

airline_icao = code_builder(AIRLINE_ICAO_REC)


# +---------------------------------------------------------------------------+

plane_iata = code_builder(PLANE_IATA_REC)

plane_icao = code_builder(PLANE_ICAO_REC)


# +---------------------------------------------------------------------------+

flight_no = code_builder(FLIGHT_NO_REC)


def main():
    """En cas de lancement standalone, on ne fait rien."""
    pass


if __name__ == "__main__":
    main()
