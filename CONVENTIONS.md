# Conventions

## Langue

+ Pour le code, les noms de fichiers...
    - Anglais **uniquement**
+ Pour les commentaires, la documentation, les commits, les fichiers `.md`
    - Français

## Formattage du code (général)

+ Longueur max des lignes : 80 caractères (79 effectif pour Python, la dernière colonne étant réservée à un éventuel caractère `\`)
+ On essaye de respecter au maximum les règles de la [*PEP8*](https://www.python.org/dev/peps/pep-0008/) peu importe le langage (tant que cela n'est pas contraire aux bonnes pratiques du langage en question)
+ Les caractères de fin de ligne autorisés sont uniquement `\n`
+ Une ligne `\n` obligatoire à la fin du fichier
+ Uniquement des espaces (pas de tabulations `\t`), et une indentation de **4 espaces** par niveau par défaut (sauf recommandation du langage en question)

## Conventions de nommage

+ Pour les dossiers, uniquement du `snake_case`
+ Pour les fichiers source, le `snake_case` est préféré, mais doit être remplacé si le langage en question recommande quelque chose d'autre
+ Pour les fichiers non source, `snake_case` également


+ Pour les variables et fonctions, `snake_case` sauf pour les langages type Java (où on utilisera alors le `mixedCase`)
+ Pour les classes, peu importe le langage, on utilisera le `CamelCase`
+ Pour les constantes, sauf recommandation contraire du langage, on utilisera la casse `UNE_CONSTANTE`

## Conventions spécifiques à Python

+ Version utilisée : Python 3 (compatible 3.5) uniquement
+ Pas de `from module import *`
+ On utilisera les *docstrings* au format [*RST*](https://www.python.org/dev/peps/pep-0287/)

## Conventions spécifiques à C

+ Version utilisée : C99
+ Les macros peuvent être utilisées ; elles respecteront alors la même casse que les constantes
+ On utilisera des *docstrings* au format [*Doxygen*](http://www.doxygen.nl/manual/docblocks.html)
+ On utilisera [*CMake*](https://cmake.org/) comme système de build
+ Convention pour les accolades : [*1TBS*](https://en.wikipedia.org/wiki/Indentation_style#Variant:_1TBS_(OTBS))
+ Les pointeurs porteront un préfixe `p_` (exemple, un pointeur vers une structure `Addr` sera déclaré : `Addr *p_addr`)
+ Les "méthodes" porteront en préfixe le nom de leur classe suivi de deux *underscore*s (exemple, pour la méthode `set` de la classe `Addr`, on aura le prototype `void Addr__set(Addr *p_addr, uint8_t my_value);`)
+ Aucune abbréviation, sauf
    - `sock` pour `socket`
    - `inet` pour `internet`
    - `addr` pour `address`
    - `recv` pour `receive`
+ Toutes les méthodes prendront comme premier argument un pointeur vers la *struct* à traiter, avec pour nom `p_nom_de_la_classe_en_snake_case`
+ Il est conseillé de *typedef* avec un nom significatif suivi du suffixe `_t` les types primitifs utilisés (exemple, pour la valeur d'un pixel stockée dans un char : `typedef char pixel_t`)
+ Il est nécessaire de *typedef* les structures utilisées, avec un nom en *CamelCase* (exemple, pour la structure `struct sockaddr_in` : `typedef struct sockaddr_in SockAddrInet`)
+ Chaque *struct* possédera une méthode obligatoire :
    - `MyStruct__set(MyStruct *p_my_struct, ...)` : une sorte de constructeur, qui fixe les valeurs des champs de la structure
+ Les `malloc`s et associés seront évités au maximum

## Conventions spécifiques à Git(Lab)

+ Il est **interdit** de *push* sur la branche `master` sauf pour les premiers commits, ou dans des circonstances extraordinaires
+ Une branche doit être créée pour chaque développement d'une nouvelle fonctionnalité. Dès que cette dernière est développée, une *merge request* doit être proposée. Au moment du *merge* sur `master`, la branche d'origine doit être supprimée. Ainsi, généralement, les branches (sauf `master`) ne vivent pas plus de quelques jours/semaines.
+ Les branches doivent être nommées en respectant la casse `lisp-case` et ne contenir aucun caractère autre que `[a-z0-9]` et éventuellement `/`
+ Si une correction doit être appliquée sur une fonctionnalité, une branche `fix/<nom-de-la-fonctionnalité>` doit être créée pour effectuer le travail
+ Le texte des *commits* doit être en **Français**

## Recommandations diverses

+ On préférera créer une fonction avec une docstring bien complète que de commenter un long bloc de code avec des commentaires "de ligne" (`#`, `//`...)
+ Bien que cela ne soit pas obligatoire, il est conseillé d'utiliser les IDE *Jetbrains* (*PyCharm*, *CLion*...) pour ce projet (*docstrings* pré-remplies, support intégré du système de build *CMake*, de *Valgrind*...)
