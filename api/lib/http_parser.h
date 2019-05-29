#ifndef DEF_HTTP_PARSER
#define DEF_HTTP_PARSER

ret_t parse_http_request(const char *data, size_t data_size, http_verb_t *p_http_verb, char **p_target, size_t *p_target_size, char **p_body, size_t *p_body_size);

ret_t make_http_response(http_status_t status, cont char *res, size_t res_size, char **p_http_response, size_t *p_http_response_size);

#endif  // DEF_HTTP_PARSER