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
    BEGIN_QUERY(p_connection, "SELECT fleet_id FROM Exploitation")
        Data *p_data;
        data_type_t data_type;
    ITER_FETCH
        DO_OR_RET(dpiStmt_getQueryValue(p_statement, 1, &data_type, &p_data), 11);
        switch (data_type) {
            case DPI_NATIVE_TYPE_DOUBLE:
                printf("double\n");
                break;
            case DPI_NATIVE_TYPE_FLOAT:
                printf("float\n");
                break;
            case DPI_NATIVE_TYPE_INT64:
                printf("int64\n");
                break;
            case DPI_NATIVE_TYPE_UINT64:
                printf("uint64\n");
                break;
            case DPI_NATIVE_TYPE_BYTES:
                printf("bytes\n");
                break;
            default:
                printf("Unknow: %d\n", data_type);
        }
    END_QUERY
    *p_airport_nb = row_nb;

    return RET_OK;
}
