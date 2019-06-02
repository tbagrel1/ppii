#include <string.h>
#include <stdio.h>

#include "http_parser.h"

ret_t parse_http_request(const char *data, size_t data_size, http_verb_t *p_http_verb, char **p_target, size_t *p_target_size, char **p_body, size_t *p_body_size) {
    if (strstr(data, "GET ") != data) {
        return RET_ARG_ERR + 10 + 1;
    }

    *p_http_verb = GET;

    const char *target_start = data + 4;
    const char *target_end = data + 4;
    while (*target_end != '\0' && *target_end != ' ' && *target_end != '\r' && *target_end != '\n' && *target_end != '\0') {
        target_end++;
    }
    size_t target_length = target_end - target_start;

    if (target_length == 0 || target_start[0] != '/') {
        return RET_ARG_ERR + 10 + 2;
    }

    *p_target = malloc((target_length + 1) * sizeof(char));
    memcpy(*p_target, target_start, target_length);
    (*p_target)[target_length] = '\0';
    *p_target_size = target_length + 1;

    char *body_limit = strstr(data, "\r\n\r\n");
    if (body_limit == NULL) {
        *p_body = owned_string("", p_body_size);
    } else {
        body_limit += 4;
        *p_body_size = data_size - (body_limit - data);
        if (body_limit[*p_body_size - 1] != '\0') {
            (*p_body_size)++;
        }
        *p_body = malloc(*p_body_size * sizeof(char));
        memcpy(*p_body, body_limit, (*p_body_size) - 1);
        (*p_body)[(*p_body_size) - 1] = '\0';
    }
    return RET_OK;
}

ret_t make_http_response(http_status_t status, char *res, size_t res_size, char **p_http_response, size_t *p_http_response_size) {
    *p_http_response = malloc((res_size + 100) * sizeof(char));
    char *response_format = "HTTP/1.1 %d %s\r\n"
                            "Content-Type: text/plain\r\n"
                            "Content-Length: %lu\r\n"
                            "\r\n"
                            "%s\r\n"
                            "\r\n";
    sprintf(*p_http_response, response_format, status, http_status_reason(status), res_size, res);
    free(res);

    *p_http_response_size = strlen(*p_http_response) + 1;
    return RET_OK;
}

