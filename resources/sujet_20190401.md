# PPII "Projet Pluridisciplinaire d'Informatique Intégrative" (2018-2019)


## Préliminaires 

Ce projet est divisé en 3 phases. Le descriptif précis de chaque phase vous sera communiqué de manière incrémentale au fur et à mesure du déroulé du projet.

### Objectifs et Attendus

- Réalisation d'une étude bibliographique
- Conception et mise en d’œuvre d’une base de données
- Réalisations de plusieurs composants logiciels informatiques dans
les langages de programmation C et Java
- Évaluation de la qualité de la solution proposée et des résultats
obtenus 

### Modalités

Ce projet est à réaliser en groupe (la constitution du groupe étant imposée). 

Vos livrables seront composés :
- des codes sources de vos développements logiciels ; 
- des documentations nécessaires à la compréhension (conception, notes de développement), l'installation, la compilation, l'exécution, la validations de vos réalisations ;
- de **tous les éléments de gestion de projet** que vous aurez produits (comptes-rendus de réunion, planification et répartition des tâches, analyse post-mortem des efforts individuels et de l'atteinte des objectifs, etc.)

L'ensemble de ces livrables seront déposés sur le dépôt git qui sera dédie à votre groupe de travail (sous-projet du projet https://gitlab.telecomnancy.univ-lorraine.fr/ppii-2k19) 


**Nota Bene.** Ne trichez pas ! Ne copiez pas ! Ne plagiez pas ! Si vous le faites, vous serez lourdement sanctionnés. Nous ne ferons pas de distinction entre copieur et copié. Vous n’avez pas de (bonnes) raisons de copier. De même, vous ne devez pas utiliser un produit clé en main trouvé sur internet.


### Livraison continue du sujet

Le sujet *le plus à jour* sera disponible dans la branche `DoW` (*description of work*) de votre dépôt git hébergé sur la plateforme GitLab de l'école (https://gitlab.telecomnancy.univ-lorraine.fr/) sous la forme du fichier `DOW.md`.

Vous devrez donc régulièrement (vous en serez informé avant) fusionner la branche `DoW` avec votre branche principale `master` afin de disposer du sujet à jour dans votre branche principale de travail.

**Attention.** Vous ne devrez jamais commiter de modifications dans la branche `DoW`. Cette branche étant automatiquement écrasée lors de la mise à jour du sujet, vous risqueriez de perdre vos modifications.


## Thématique du projet

Ce projet conserve le même thème d'étude que le projet du module TOP du premier semestre : Le transport aérien et les données de vols.

Les données du projet repose en majeure partie (mais pas seulement) sur les données ouvertes du site https://openflights.org/data.html.

## Étape 1 : Gestion de données [SQL]

**Date de communication** : 28 Mars 2019

**Date de rendu** : 6 Avril 2019

### Objectifs généraux

- Concevoir un schéma de base de données relationnelle stockant des données de transport aérien variées
- Implémenter ce schéma relationnel dans le SGBD Oracle
- Élaborer des requêtes SQL sur le schéma relationnel 

### Données à intégrer

Le répertoire `provided_data/` contient plusieurs fichiers de données :
- [airport.dat](./provided_data/airports.dat)
  - provenance :  OpenFlights.org - https://openflights.org/data.html#airport
  - description : Liste de 7543 aéroports (nom, ville, pays, code IATA, code ICAO, longitude, latitude, etc.)

- [airlines.date](./provided_data/airlines.dat)
  - provenance :  OpenFlights.org - https://openflights.org/data.html#airline
  - description : Liste de 6162 compagnies aériennes (nom, code IATA, code ICAO, Pays, Indicatif, etc.)

- [planes.dat](./provided_data/planes.dat)
  - provenance : OpenFlights.org - https://openflights.org/data.html#plane
  - description : Liste de 174 avions (nom, code IATA, code ICAO)

- [routes.dat](./provided_data/routes.dat)
  - provenance : OpenFlights.org - https://openflights.org/data.html#route
  - description : Liste de 67663 vols (code la compagnie aérienne, numéro du vol, aéroport de départ, aéroport d'arrivée, avions utilisés)

- [flightnumbers.csv](./provided_data/flightnumbers.csv)
  - provenance: Virtual Server Radar - http://www.virtualradarserver.co.uk/FlightRoutes.aspx
  - description : Liste de 303,799 vols aériens (code la compagnie aérienne, numéro du vol, description de la route)

Vous serez ammené à nettoyer ces données afin de pouvoir les intégrer.

Il vous est demandé de compléter ces données, dans la mesure du possible, par des données (que vous rechercherez par vous-même) sur les alliances entre les compagnies aériennes (https://fr.wikipedia.org/wiki/Alliance_de_compagnies_a%C3%A9riennes) et sur les caractéristiques des avions utilisées (nombre de passagers, autonomie, vitesse, consommation de carburant, etc.). Ces informations complémentaires pourront être ajoutées au cours du projet (lors des étapes 2 et 3).

### Attendus

Il est attendu :
- la conception d'**un schéma relationnel** pour intégrer les données mentionnées précédemment
  - ce schéma devra dans un premier temps être en **3ème forme normale**, vous pourrez dénormaliser ce schéma si nécessaire et argumentant sur ce point
  - vous identifierez les **contraintes d'intégrité** du modèle de données
- la transposition de ce modèle dans **une base de données relationnelle** sur le SGBD Oracle
- l'**importation (automatisée) des données** dans la base proposée (un nettoyage des données sera sûrement nécessaire)
- la fourniture d'un certain nombre de **requêtes SQL** démontrant la viabilité du modèle proposé.

### Base de données à votre disposition

Chaque groupe de projet dispose d'une base de données sur le serveur Oracle de l'école. Vous devez **impérativement** utiliser ce serveur.

Les informations de connexion à cette base sont :
- nom d'hôte : `oracle.telecomnancy.univ-lorraine.fr`
- port : `1521` 
- nom de service : `TNCY`
- login : `<identifiant_de_votre_groupe>` 
- mot de passe : `TPOracle` 

L'identifiant de votre groupe correspond au suffixe du nom de votre projet GitLab. Par exemple, le projet GitLab `project-grp47` a pour identifiant `grp47`. À noter que pour les élèves en formation sous statut apprentis, l'identifiant est en minuscule, ainsi le projet `project-grpA7` a pour identifiant `grpa7`.


## Étape 2 : Recherche de chemins [C]

**Date de communication** : [TBA]

**Date de rendu** : [TBA]