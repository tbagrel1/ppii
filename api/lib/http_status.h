#ifndef DEF_HTTP_STATUS
#define DEF_HTTP_STATUS

#include <stdbool.h>

typedef enum {
    HTTP_OK = 200,
    HTTP_RESOURCE_CREATED = 201,
    HTTP_REQUEST_ACCEPTED = 202,
    HTTP_OK_NO_RETURN = 204,
    HTTP_BAD_REQUEST = 400,
    HTTP_NEED_AUTHENTICATION = 401,
    HTTP_NEED_PAYMENT = 402,
    HTTP_ACCESS_FORBIDDEN = 403,
    HTTP_RESOURCE_NOT_FOUND = 404,
    HTTP_INVALID_HTTP_VERB = 405,
    HTTP_REQUEST_TIMEOUT = 408,
    HTTP_RESOURCE_CURRENTLY_UNAVAILABLE = 409,
    HTTP_RESOURCE_NO_LONGER_AVAILABLE = 410,
    HTTP_INTERNAL_ERROR = 500,
    HTTP_NOT_IMPLEMENTED = 501,
    HTTP_UPSTREAM_SERVER_ERROR = 502,
    HTTP_SERVICE_CURRENTLY_UNAVAILABLE = 503,
    HTTP_UPSTREAM_SERVER_TIMEOUT = 504
} http_status_t;

bool is_http_success(http_status_t status);
bool is_http_client_error(http_status_t status);
bool is_http_server_error(http_status_t status);
bool is_http_error(http_status_t status);

char *http_status_reason(http_status_t status);

#endif  // DEF_HTTP_STATUS
