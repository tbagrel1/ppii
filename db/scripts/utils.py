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

import json


ENC = "utf-8"


WARNING = "W"
ERROR = "E"

SEVERITY_TO_COLOR = {
    WARNING: 221,
    ERROR: 196
}


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


def color_escapes(color_code):
    return "\u001b[38;5;{}m".format(color_code), "\u001b[0m"


def display_alert(severity, i_row, row, text):
    b, e = color_escapes(SEVERITY_TO_COLOR[severity])
    print("{}[{}] {}: {}\n    {}{}\n".format(b, severity, i_row, row, text, e))


def display_alert_field(severity, i_row, row, i_field, field_name):
    b, e = color_escapes(SEVERITY_TO_COLOR[severity])
    print("{}[{}] {}: {}\n    on {}: {}{}\n"
          .format(b, severity, i_row, row, i_field, field_name, e))


def main():
    """Si le module est lancé directement (ie n'est pas un import)."""
    pass


if __name__ == "__main__":
    main()
