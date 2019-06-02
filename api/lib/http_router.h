#ifndef DEF_HTTP_ROUTER
#define DEF_HTTP_ROUTER

#include <stdlib.h>
#include "ret.h"
#include "http_status.h"

typedef ret_t (*callback_t)(http_status_t *, char **, size_t *, const char *, const char *);

typedef enum {
    GET,
    HEAD,
    POST,
    PUT,
    DELETE,
    CONNECT,
    OPTIONS,
    TRACE,
    PATCH
} http_verb_t;

struct HttpCallback {
    http_verb_t http_verb;
    callback_t callback;
};

struct Route {
    const char *segment;
    const struct HttpCallback *http_callbacks;
    const struct Route *subroutes;
};

typedef struct HttpCallback HttpCallback;
typedef struct Route Route;

extern const Route ROUTE_END;
extern const HttpCallback HTTP_CALLBACK_END;
extern const char *ROUTE_ORIGIN;

bool Route__shallow_eq(Route const *p_route, Route const *p_other);
bool HttpCallback__shallow_eq(HttpCallback const *p_http_callback,
                              HttpCallback const *p_other);

ret_t route(Route const *p_origin, http_status_t *p_status, char **p_res, size_t *p_res_size,
            http_verb_t http_verb, const char *target, const char *body);
ret_t _route(Route const *p_route, http_status_t *p_status, char **p_res, size_t *p_res_size,
             http_verb_t http_verb, const char *target, const char *body);

char * owned_string(const char *source, size_t *p_source_size);

char * owned(const char *source, size_t source_size);

#endif  // DEF_HTTP_ROUTER
