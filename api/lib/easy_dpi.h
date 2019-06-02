#ifndef DEF_EASY_DPI
#define DEF_EASY_DPI

#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <inttypes.h>
#include <stdbool.h>
#include <dpi.h>

#include "ret.h"

#define DEFAULT_COMMON_PARAMS NULL  // https://oracle.github.io/odpi/doc/structs/dpiCommonCreateParams.html#dpicommoncreateparams
#define DEFAULT_CONNECTION_PARAMS NULL  // https://oracle.github.io/odpi/doc/structs/dpiConnCreateParams.html#dpiconncreateparams

int _nothing;

#define DO_OR_RAISE(func_call, error_message) \
    if ((func_call) != DPI_SUCCESS) { \
        perror((error_message)); \
        exit(1); \
    } _nothing = 0

#define DO_OR_RET(func_call, error_id) \
    if ((func_call) != DPI_SUCCESS) { \
        return RET_INTERNAL_ERR + (error_id); \
    } _nothing = 0

#define DO_OR_RET0(func_call, error_id) \
    if ((func_call) != DPI_SUCCESS) { \
        return RET_INTERNAL_ERR; \
    } _nothing = 0

#define BEGIN_QUERY(p_connection, query) \
    Statement *p_statement; \
    uint64_t row_nb; \
    uint32_t column_nb; \
    DO_OR_RET(dpiConn_prepareStmt(p_connection, false, query, strlen(query), NULL, 0, &p_statement), 1); \
    DO_OR_RET(dpiStmt_execute(p_statement, DPI_MODE_EXEC_DEFAULT, &column_nb), 2); \
    DO_OR_RET(dpiStmt_getRowCount(p_statement, &row_nb), 3);
#define ITER_FETCH \
    int found; \
    uint32_t buffer_row_index; \
    DO_OR_RET(dpiStmt_fetch(p_statement, &found, &buffer_row_index), 4); \
    while (found) {
#define END_QUERY \
        DO_OR_RET(dpiStmt_fetch(p_statement, &found, &buffer_row_index), 5); \
    } \
    dpiStmt_release(p_statement);

typedef struct dpiConn Connection;
typedef struct dpiContext Context;
typedef struct dpiCommonCreateParams CommonParams;
typedef struct dpiErrorInfo ErrorInfo;
typedef struct dpiVersionInfo VersionInfo;
typedef struct dpiStmt Statement;

bool is_connection_ok(Connection *p_connection);
ret_t get_airport_nb(Connection *p_connection, uint64_t *p_airport_nb);

#endif  // DEF_EASY_DPI
