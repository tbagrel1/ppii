#include <string.h>
#include <stdio.h>

#include "easy_socket.h"
#include "http_parser.h"
#include "http_router.h"

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

    char *body_limit = strstr(target_end, "\r\n\r\n");
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

#define PEEK_BUFFER_SIZE 256

ret_t peek_and_read_http_response(sock_fd_t sock_fd, char **p_data, size_t *p_data_size) {
    static char peek_buffer[PEEK_BUFFER_SIZE];
    ssize_t read_size = recv(sock_fd, peek_buffer, PEEK_BUFFER_SIZE, MSG_PEEK);
    if (read_size < 0) {
        return RET_ARG_ERR + 10 + 1;
    }
    if (read_size == 0) {
        return RET_ARG_ERR + 10 + 2;
    }
    char *content_length_limit = strstr(peek_buffer, "Content-Length: ");
    if (content_length_limit == NULL) {
        return RET_ARG_ERR + 20 + 1;
    }
    const char *length_start = content_length_limit + 16;
    const char *length_end = content_length_limit + 16;
    while (*length_end != '\0' && *length_end != ' ' && *length_end != '\r' && *length_end != '\n' && *length_end != '\0') {
        length_end++;
    }
    char *end;
    size_t length = strtoul(length_start, &end, 10);
    if (end != length_end) {
        return RET_ARG_ERR + 20 + 2;
    }
    size_t data_space = length + 200;
    *p_data = malloc(data_space * sizeof(char));
    read_size = recv(sock_fd, *p_data, data_space - 1, NO_FLAGS);
    if (read_size < 0) {
        free(*p_data);
        return RET_ARG_ERR + 10 + 3;
    }
    if (read_size == 0) {
        free(*p_data);
        return RET_ARG_ERR + 10 + 4;
    }
    if (read_size == data_space - 1) {
        free(*p_data);
        return RET_INTERNAL_ERR + 1;
    }
    if ((*p_data)[read_size - 1] != '\0') {
        (*p_data)[read_size++] = '\0';
    }
    *p_data_size = (size_t) (read_size);
    return RET_OK;
}

ret_t parse_http_response(const char *data, size_t data_size, http_status_t *p_status, char **p_res, size_t *p_res_size) {
    if (strstr(data, "HTTP/1.1 ") != data) {
        return RET_ARG_ERR + 10 + 1;
    }
    const char *status_start = data + 9;
    const char *status_end = data + 9;
    while (*status_end != '\0' && *status_end != ' ' && *status_end != '\r' && *status_end != '\n' && *status_end != '\0') {
        status_end++;
    }
    char *end;
    *p_status = (http_status_t) (strtol(status_start, &end, 10));
    if (end != status_end) {
        return RET_ARG_ERR + 10 + 2;
    }
    char *res_limit = strstr(status_end, "\r\n\r\n");
    if (res_limit == NULL) {
        *p_res = owned_string("", p_res_size);
    } else {
        res_limit += 4;
        *p_res_size = data_size - (res_limit - data);
        if (res_limit[*p_res_size - 1] != '\0') {
            (*p_res_size)++;
        }
        *p_res = malloc(*p_res_size * sizeof(char));
        memcpy(*p_res, res_limit, (*p_res_size) - 1);
        (*p_res)[(*p_res_size) - 1] = '\0';
    }
    return RET_OK;
}

ret_t make_http_request(http_verb_t http_verb, char *target, size_t target_size, char *body, size_t body_size, char **p_http_request, size_t *p_http_request_size) {
    *p_http_request = malloc((target_size + body_size + 100) * sizeof(char));
    char *request_format = "%s %s HTTP/1.1\r\n"
                           "\r\n"
                           "%s\r\n"
                           "\r\n";
    sprintf(*p_http_request, request_format, http_verb_to_string(http_verb), target, body);
    free(target);
    free(body);

    *p_http_request_size = strlen(*p_http_request) + 1;
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

