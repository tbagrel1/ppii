#include <stdio.h>
#include <stdlib.h>

#include "lib/ret.h"

#include "lib/easy_dpi.h"

int main(int argc, char **argv) {
    printf("BEGIN\n");

    Context *p_context;
    ErrorInfo error_info;

    DO_OR_RAISE(dpiContext_create(DPI_MAJOR_VERSION, DPI_MINOR_VERSION, &p_context, &error_info), "Context creation");

    CommonParams common_params;

    DO_OR_RAISE(dpiContext_initCommonCreateParams(p_context, &common_params), "CommonParams struct initialization (with default value)");
    common_params.nencoding = "UTF-8";

    const char *username = "grpa1";
    const char *password = "TPOracle";
    const char *db_uri = "oracle.telecomnancy.univ-lorraine.fr:1521/TNCY";

    Connection *p_connection;

    DO_OR_RAISE(dpiConn_create(p_context, username, strlen(username), password, strlen(password), db_uri, strlen(db_uri), &common_params, DEFAULT_CONNECTION_PARAMS, &p_connection), "Connection creation");

    if (!is_connection_ok(p_connection)) {
        perror("Connection failed");
        exit(1);
    }

    uint64_t airport_nb = -1;
    ret_t ret_value;
    if (is_ret_ok(ret_value = get_airport_nb(p_connection, &airport_nb))) {
        printf("%lu airports found!\n", airport_nb);
    } else {
        printf("Unable to perform the request: %d error code\n", ret_value);
    }

    dpiConn_release(p_connection);
    dpiContext_destroy(p_context);

    printf("END\n");
    return 0;
}
