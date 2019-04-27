#include "http_status.h"

bool is_http_success(http_status_t status) {
    return status >= 0 && status < 1000 && status % 100 == 2;
}

bool is_http_client_error(http_status_t status) {
    return status >= 0 && status < 1000 && status % 100 == 4;
}

bool is_http_server_error(http_status_t status) {
    return status >= 0 && status < 1000 && status % 100 == 5;
}

bool is_http_error(http_status_t status) {
    return is_http_client_error(status) || is_http_server_error(status);
}
