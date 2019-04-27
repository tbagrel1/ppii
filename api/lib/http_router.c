#include <string.h>

#include "http_router.h"
#include "ret.h"

const Route ROUTE_END = { "END", NULL, NULL };
const HttpCallback HTTP_CALLBACK_END = { GET, NULL };
const char *ROUTE_ORIGIN = "%ORIGIN%";

ret_t route(Route const *p_origin, http_status_t *p_status, char **p_res,
            http_verb_t http_verb, const char *target, const char *body) {
    if (target == NULL) {
        return RET_ARG_ERR + 50 + 1;
    }
    if (body == NULL) {
        return RET_ARG_ERR + 60 + 1;
    }

    // On vérifie que target commence bien par le / typique des requêtes HTTP,
    // et on incrémente pour le "supprimer"
    if (target[0] != '/') {
        return RET_ARG_ERR + 50 + 2;
    }
    target++;

    ret_t ret_value = _route(p_origin, p_status, p_res, http_verb, target, body);
    if (ret_value == RET_CUSTOM) {
        return RET_INTERNAL_ERR + 1;
    }

    return RET_OK;
}

static char *_segment = NULL;

ret_t _route(Route const *p_route, http_status_t *p_status, char **p_res,
             http_verb_t http_verb, const char *target, const char *body) {

    char *next_slash = strchr(target, '/');
    size_t segment_len = (next_slash == NULL) ? (strlen(target)) : (next_slash - target);
    char *child_target = (next_slash == NULL) ? ("") : (next_slash + 1);

    _segment = realloc(_segment, segment_len + 1);
    memcpy(_segment, target, segment_len);
    _segment[segment_len] = '\0';

    ret_t child_ret_value;
    const Route *p_subroute = p_route->subroutes;
    while (!Route__shallow_eq(p_subroute, &ROUTE_END)) {
        if (strcmp(_segment, p_subroute->segment) == 0) {
            if ((child_ret_value = _route(p_subroute, p_status, p_res, http_verb, child_target, body)) != RET_CUSTOM) {
                return child_ret_value;
            }
        }
        p_subroute++;
    }

    const HttpCallback *p_http_callback = p_route->http_callbacks;
    while (!HttpCallback__shallow_eq(p_http_callback, &HTTP_CALLBACK_END)) {
        if (p_http_callback->http_verb == http_verb) {
            return p_http_callback->callback(p_status, p_res, target, body);
        }
        p_http_callback++;
    }

    return RET_CUSTOM;
}

bool HttpCallback__shallow_eq(HttpCallback const *p_http_callback,
                              HttpCallback const *p_other) {
    return (
        p_http_callback->http_verb == p_other->http_verb &&
        p_http_callback->callback == p_other->callback
    );
}

bool Route__shallow_eq(Route const *p_route, Route const *p_other) {
    return (
        strcmp(p_route->segment, p_other->segment) == 0 &&
        p_route->subroutes == p_other->subroutes &&
        p_route->http_callbacks == p_other->http_callbacks
    );
}
