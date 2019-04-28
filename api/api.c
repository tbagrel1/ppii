#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "lib/http_router.h"

#define DEMO_SIZE 1024

char *char_repeat(char c, size_t n) {
    char *result = (char *) malloc((n + 1) * sizeof(*result));
    for (size_t i = 0; i < n; ++i) {
        result[i] = c;
    }
    result[n] = '\0';

    return result;
}

char *make_demo_str(const char *title, const char *target, const char *body) {
    char *result = (char *) malloc(DEMO_SIZE * sizeof(*result));
    char *underline = char_repeat('=', strlen(title));
    snprintf(result, DEMO_SIZE, "%s\n%s\n\nTarget: %s\n\nBody:\n%s\n", title, underline, target, body);
    free(underline);
    return result;
}

ret_t get_plane(http_status_t *p_status, char **p_res, const char *target, const char *body) {
    *p_status = HTTP_OK;
    *p_res = make_demo_str("GET: Plane", target, body);
    return RET_OK;
}
ret_t post_plane(http_status_t *p_status, char **p_res, const char *target, const char *body) {
    *p_status = HTTP_OK;
    *p_res = make_demo_str("POST: Plane", target, body);
    return RET_OK;
}

ret_t get_airport(http_status_t *p_status, char **p_res, const char *target, const char *body) {
    *p_status = HTTP_OK;
    *p_res = make_demo_str("GET: Airport", target, body);
    return RET_OK;
}
ret_t post_airport(http_status_t *p_status, char **p_res, const char *target, const char *body) {
    *p_status = HTTP_OK;
    *p_res = make_demo_str("POST: Airport", target, body);
    return RET_OK;
}
ret_t patch_airport(http_status_t *p_status, char **p_res, const char *target, const char *body) {
    *p_status = HTTP_OK;
    *p_res = make_demo_str("PATCH: Airport", target, body);
    return RET_OK;
}

ret_t get_airline(http_status_t *p_status, char **p_res, const char *target, const char *body) {
    *p_status = HTTP_OK;
    *p_res = make_demo_str("GET: Airline", target, body);
    return RET_OK;
}

ret_t get_home(http_status_t *p_status, char **p_res, const char *target, const char *body) {
    *p_status = HTTP_OK;
    *p_res = make_demo_str("GET: Home", target, body);
    return RET_OK;
}

http_verb_t str_to_http_verb(const char *str) {
    if (strcmp(str, "get") == 0) {
        return GET;
    }
    if (strcmp(str, "post") == 0) {
        return POST;
    }
    if (strcmp(str, "patch") == 0) {
        return PATCH;
    }
    printf("[W] Not a recognized verb (%s). Using default: GET\n", str);
    return GET;
}

int main(int argc, char **argv) {
    HttpCallback plane_methods[] = {
        { GET, get_plane },
        { POST, post_plane },
        HTTP_CALLBACK_END
    };
    Route plane = {
        "plane",
        plane_methods,
        &ROUTE_END
    };

    HttpCallback airport_methods[] = {
        { GET, get_airport },
        { POST, post_airport },
        { PATCH, patch_airport },
        HTTP_CALLBACK_END
    };
    Route airport = {
        "airport",
        airport_methods,
        &ROUTE_END
    };

    HttpCallback airline_methods[] = {
        { GET, get_airline },
        HTTP_CALLBACK_END
    };
    Route airline = {
        "airline",
        airline_methods,
        &ROUTE_END
    };

    HttpCallback api_methods[] = {
        { GET, get_home },
        HTTP_CALLBACK_END
    };
    Route api_subroutes[] = {
        plane,
        airport,
        airline,
        ROUTE_END
    };
    Route api = {
        ROUTE_ORIGIN,
        api_methods,
        api_subroutes
    };

    char *target = NULL;
    ssize_t target_len;
    size_t target_size = 0;
    char *body = NULL;
    ssize_t body_len;
    size_t body_size = 0;
    http_verb_t http_verb;

    http_status_t status;
    char *res;
    ret_t ret_value;

    while (true) {
        // verb
        printf("Verb [get/post/patch/exit]: ");
        target_len = getline(&target, &target_size, stdin);
        target[--target_len] = '\0';
        if (strcmp(target, "exit") == 0) {
            break;
        }
        http_verb = str_to_http_verb(target);
        // target
        printf("Target (must start with a /): ");
        target_len = getline(&target, &target_size, stdin);
        target[--target_len] = '\0';
        // body
        printf("Body: \n");
        body_len = getline(&body, &body_size, stdin);
        body[--body_len] = '\0';

        ret_value = route(&api, &status, &res, http_verb, target, body);
        printf("\n========\nret: %d\nstatus: %d\nres:\n%s\n========\n\n", ret_value, status, res);
        free(res);
    }

    free(target);
    free(body);

    return 0;
}
