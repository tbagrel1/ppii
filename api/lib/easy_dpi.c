#include <stdio.h>
#include "easy_dpi.h"

int _nothing = 0;

bool is_connection_ok(Connection *p_connection) {
    const char *release_string;
    uint32_t release_string_length;
    VersionInfo version_info;

    return dpiConn_getServerVersion(p_connection, &release_string, &release_string_length, &version_info) == DPI_SUCCESS;
}


ret_t get_airport_nb(Connection *p_connection, uint64_t *p_airport_nb) {
    BEGIN_QUERY(p_connection, "SELECT * FROM Airport")
        *p_airport_nb = row_nb;
    ITER_FETCH
    END_QUERY

    return RET_OK;
}
