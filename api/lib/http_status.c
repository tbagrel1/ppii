#include "http_status.h"

bool is_http_success(http_status_t status) {
    return status / 100 == 2;
}

bool is_http_client_error(http_status_t status) {
    return status / 100 == 4;
}

bool is_http_server_error(http_status_t status) {
    return status / 100 == 5;
}

bool is_http_error(http_status_t status) {
    return is_http_client_error(status) || is_http_server_error(status);
}

char *http_status_reason(http_status_t status) {
    switch (status) {
        case HTTP_OK:
            return "OK";
        case HTTP_BAD_REQUEST:
            return "Bad Request";
        case HTTP_RESOURCE_NOT_FOUND:
            return "Not Found";
        case HTTP_INTERNAL_ERROR:
            return "Internal Server Error";
        default:
            // TODO
            return "Too Lazy";
    }
}
