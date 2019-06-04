#ifndef DEF_HTTP_PARSER
#define DEF_HTTP_PARSER

#include <stdlib.h>
#include "ret.h"
#include "http_router.h"
#include "http_status.h"

ret_t parse_http_request(const char *data, size_t data_size, http_verb_t *p_http_verb, char **p_target, size_t *p_target_size, char **p_body, size_t *p_body_size);

ret_t parse_http_response(const char *data, size_t data_size, http_status_t *p_status, char **p_res, size_t *p_res_size);

ret_t make_http_response(http_status_t status, char *res, size_t res_size, char **p_http_response, size_t *p_http_response_size);

ret_t make_http_request(http_verb_t http_verb, char *target, size_t target_size, char *body, size_t body_size, char **p_http_request, size_t *p_http_request_size);

ret_t peek_and_read_http_response(sock_fd_t sock_fd, char **p_data, size_t *p_data_size);

#endif  // DEF_HTTP_PARSER
