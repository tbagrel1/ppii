#ifndef DEF_RET
#define DEF_RET

#include <stdbool.h>

/**
 * Type de retour pour nos fonctions
 */
typedef int ret_t;

/**
 * Tout s'est bien passé
 */
#define RET_OK 0

/**
 * Une erreur a été rencontrée, et errno a été défini
 */
#define RET_ERRNO_ERR -1

/**
 * Les paramètres étaient invalides, le traitement n'a donc pas pu être effectué
 *
 * Forme : 4xx
 *     - 2e chiffre : numéro de l'argument fautif
 *     - 3e chiffre : id de l'erreur (pour le debug)
 */
#define RET_ARG_ERR 400

/**
 * Une erreur s'est produite dans un des appels internes de la fonction.
 * La fonction incriminée n'a pas donné d'informations permettant de distinguer
 * l'erreur rencontrée, ou ces dernières n'ont pas été traitées
 *
 * Forme : 5xx
 *     - 2e et 3e chiffre : id de l'erreur
 */
#define RET_INTERNAL_ERR 500

/**
 * Valeur de retour personnalisée
 */
#define RET_CUSTOM 900

bool is_ret_ok(ret_t ret_value);
bool is_ret_arg_err(ret_t ret_value);
bool is_ret_internal_err(ret_t ret_value);
bool is_ret_errno_err(ret_t ret_value);
bool is_ret_err(ret_t ret_value);
bool is_ret_custom(ret_t ret_value);

#endif  // DEF_RET
