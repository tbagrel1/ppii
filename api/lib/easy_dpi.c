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
    BEGIN_QUERY(p_connection, "SELECT icao FROM Airport")
        Data *p_data;
        data_type_t data_type;
        Bytes *p_bytes;
        char icao[5];
    ITER_FETCH
        DO_OR_RET(dpiStmt_getQueryValue(p_statement, 1, &data_type, &p_data), 11);
        p_bytes = dpiData_getBytes(p_data);
        strncpy(icao, p_bytes->ptr, 4);
        icao[4] = '\0';
        printf("ICAO: %s\n", icao);
    END_QUERY
    *p_airport_nb = row_nb;

    return RET_OK;
}
