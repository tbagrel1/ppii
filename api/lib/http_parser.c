#include "http_parser.h"

ret_t parse_http_request(const char *data, size_t data_size, http_verb_t *p_http_verb, char **p_target, size_t *p_target_size, char **p_body, size_t *p_body_size) {
    // TODO
    return RET_OK;
}

/*
Cette fonction a pour but de compiler l'expression régulière regex fournie sous forme de chaîne de caractères pour la transformer en structure de type dont l'adresse est passée en premier argument. Il est possible de modifier le comportement de cette fonction par l'intermédiaire de cflags qui peut être un OU binaire de l'une des constantes suivantes :

REG_EXTENDED : permet d'utiliser le modèle d'expression régulière étendu plutôt que le mode basique qui est l'option par défaut
REG_ICASE : permet d'ignorer la casse (minuscules/majuscules)
REG_NOSUB : compile pour vérifier uniquement la concordance (vrai ou faux)
REG_NEWLINE : Par défaut, le caractère de fin de ligne est un caractère normal. Avec cette option, les expressions '[^', '.' et '$' (nous reviendrons plus tard sur la signification de ces expressions) incluent le caractère de fin de ligne implicitement. L'ancre '^' reconnaît une chaîne vide après un caractère de fin de ligne.
En cas de succès, la fonction retourne 0. En cas d'échec de la compilation, retourne un code d'erreur non nul.
*/

// int regcomp (regex_t *preg, const char *regex, int cflags);

/*
Une fois notre expression compilée, on va pouvoir la comparer à la chaîne de caractères string à l'aide de cette fonction. Le résultat de la comparaison sera stocké dans le tableau pmatch alloué à nmatch éléments par nos soins. Il est possible de modifier le comportement de grâce à eflags :

REG_NOTBOL : le premier caractère de la chaîne échoue toujours. Ceci n'a pas d'effet s'il s'agit du caractère de fin de ligne et que l'option REG_NEWLINE a été utilisée pour compiler l'expression régulière
REG_NOTEOL : idem sauf qu'il s'agit du dernier caractère. La remarque à propos de REG_NEWLINE est également valable
retourne 0 en cas de succès ou REG_NOMATCH en cas d'échec.


*/
// int regexec (const regex_t *preg, const char *string, size_t nmatch, regmatch_t pmatch[], int eflags);

ret_t make_http_response(http_status_t status, const char *res, size_t res_size, char **p_http_response, size_t *p_http_response_size) {
    // TODO
    return RET_OK;
}

