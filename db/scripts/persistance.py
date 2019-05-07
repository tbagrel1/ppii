#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Permet d'utiliser des données persistants (par fichier JSON)."""

__author__ = "Thomas Bagrel"
__copyright__ = "Copyright 2019, Thomas Bagrel"
__credits__ = ["Thomas Bagrel"]
__license__ = "Apache 2.0"


from os import path

import json


ENC = "utf-8"


def _should_(prompt_part, path_):
    """
    Demande à l'utilisateur si on doit {prompt_part} {path_}
    (par exemple,           si on doit  charger       fichier.txt).
    :param prompt_part: verbe à l'infinitif
    :param path_: chemin
    :return: True ou False suivant le choix de l'utilisateur
    """
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
    """
    Demande à l'utilisateur si l'on doit charger le fichier spécifié par path_.
    :param path_: chemin
    :return: True ou False suivant le choix de l'utilisateur
    """
    return _should_("load from", path_)


def should_save(path_):
    """
    Demande à l'utilisateur si l'on doit sauver les données chargées à partir
    du fichier spécifié par path_(qui ont été modifiées) dans ce même fichier
    :param path_: chemin
    :return: True ou False suivant le choix de l'utilisateur
    """
    return _should_("save to", path_)


class JsonPersistence:
    """
    Context-manager permettant d'utiliser des données persistantes, chargées
    puis sauvées dans des fichiers JSON.
    """
    def __init__(self, root_dir, names_types, ask_confirmation=False):
        """
        Constructeur
        :param root_dir: chemin du dossier dans lequel seront créés les
                         fichiers de persistance
        :param names_types: liste de tuples de la forme
               (nom du fichier de persistance, type de l'élément persistant)
        :param ask_confirmation: doit-on demander confirmation à l'utilisateur
               avant de charger ou de sauver les données ?
        """
        self.root_dir = root_dir
        self.names_types = names_types
        self.ask_confirmation = ask_confirmation

    def __enter__(self):
        """
        Correspond à la valeur récupérée avec le "as" qui suit le "with"
        :return: une liste contenant chacun des éléments persistants
                 chargés/créés suivant les paramètres passés au constructeur
        """
        self.contents = []
        for name, type_ in self.names_types:
            path_ = path.join(self.root_dir, name)
            try:
                if self.ask_confirmation and not should_load(path_):
                    raise Exception("Should create instead")
                with open(path_, "r", encoding=ENC) as file:
                    content = json.load(file)
                print("    [JsonPersistence] --- loaded from \"{}\""
                      .format(path_))
            except Exception as _:
                content = type_()
                print("    [JsonPersistence] --- created    (\"{}\")"
                      .format(path_))
            self.contents.append(content)
        print()

        return self.contents

    def __exit__(self, type_, value, traceback):
        """
        Lorsque l'on quitte le scope du context-manager, les données sont
        enregistrées dans les fichiers de persistance
        :param type_: <ne concerne pas l'utilisateur>
        :param value: <ne concerne pas l'utilisateur>
        :param traceback: <ne concerne pas l'utilisateur>
        :return: rien (None)
        """
        print()
        for ((name, type_), content) in zip(self.names_types, self.contents):
            path_ = path.join(self.root_dir, name)
            try:
                if self.ask_confirmation and not should_save(path_):
                    raise Exception("Should not save")
                with open(path_, "w", encoding=ENC) as file:
                    json.dump(content, file, indent=2, sort_keys=True)
                print("    [JsonPersistence] --- saved to    \"{}\""
                      .format(path_))
            except Exception as _:
                print("    [JsonPersistence] --- not saved  (\"{}\")"
                      .format(path_))
        print()


def main():
    """Si le module est lancé directement (ie n'est pas un import)."""
    pass


if __name__ == "__main__":
    main()
