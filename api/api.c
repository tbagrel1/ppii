#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

#include "lib/http_router.h"
#include "lib/easy_dpi.h"
#include "lib/easy_socket.h"
#include "lib/http_parser.h"

static Route *p_api = NULL;
static Connection *p_connection = NULL;
static const char *null_string = "\\N";

#define READ_BUFFER_SIZE 1024

#define PUT(string, string_length) \
    if (string != NULL && string_length > 0) { \
        memcpy(buffer_current_pos, string, string_length); \
        buffer_current_pos += string_length; \
    } \
    _nothing = 0
#define PUT_TERMINATOR *(buffer_current_pos++) = '\0'

#define WITH_NULL_HANDLED \
    if (p_data->isNull) { \
        strncpy(buffer_current_pos, null_string, strlen(null_string)); \
        buffer_current_pos += strlen(null_string); \
        PUT(sep_string, sep_string_length); \
    } else

#define HANDLE_STRING(pos) \
    DO_OR_RET(dpiStmt_getQueryValue(p_statement, pos, &data_type, &p_data), pos); \
    WITH_NULL_HANDLED {;\
        p_bytes = dpiData_getBytes(p_data); \
        PUT(p_bytes->ptr, p_bytes->length); \
        PUT(sep_string, sep_string_length); \
    } \
    _nothing = 0

#define HANDLE_DECIMAL(pos) \
    DO_OR_RET(dpiStmt_getQueryValue(p_statement, pos, &data_type, &p_data), pos); \
    WITH_NULL_HANDLED { \
        decimal = dpiData_getDouble(p_data); \
        snprintf(number_to_string_buffer, 25, "%f", decimal); \
        number_to_string_buffer[24] = '\0'; \
        number_length = strlen(number_to_string_buffer);\
        PUT(number_to_string_buffer, number_length); \
        PUT(sep_string, sep_string_length); \
    } \
    _nothing = 0

#define HANDLE_INTEGER(pos) \
    DO_OR_RET(dpiStmt_getQueryValue(p_statement, pos, &data_type, &p_data), pos); \
    WITH_NULL_HANDLED { \
        integer = dpiData_getInt64(p_data); \
        snprintf(number_to_string_buffer, 25, "%ld", integer); \
        number_to_string_buffer[24] = '\0'; \
        number_length = strlen(number_to_string_buffer);\
        PUT(number_to_string_buffer, number_length); \
        PUT(sep_string, sep_string_length); \
    } \
    _nothing = 0

ret_t airport_row_to_string(Statement *p_statement, char **p_res, size_t *p_res_size, const char *sep_string, const char *end_string) {
    Data *p_data;
    data_type_t data_type;
    Bytes *p_bytes;
    double decimal;
    int64_t integer;
    size_t number_length;
    static char number_to_string_buffer[25];

    size_t sep_string_length = strlen(sep_string);
    size_t end_string_length = strlen(end_string);

    size_t buffer_size =
        4 + 4 + 256 + 256 + 256 + 24 + 24 + 24 + 24 + 1 + 64 + 64 + 64 + 1 + 13 * sep_string_length + end_string_length;
    //                                                                   \0
    char *buffer = ((char *) (malloc(buffer_size * sizeof(*buffer))));
    buffer[buffer_size - 1] = '\0';
    char *buffer_current_pos = buffer;

    // icao
    HANDLE_STRING(1);
    // iata
    HANDLE_STRING(2);
    // name
    HANDLE_STRING(3);
    // city
    HANDLE_STRING(4);
    // country
    HANDLE_STRING(5);
    // latitude
    HANDLE_DECIMAL(6);
    // longitude
    HANDLE_DECIMAL(7);
    // altitude
    HANDLE_DECIMAL(8);
    // utc_offset
    HANDLE_DECIMAL(9);
    // daylight_saving_group
    HANDLE_STRING(10);
    // tz_name
    HANDLE_STRING(11);
    // type
    HANDLE_STRING(12);
    // data_source
    HANDLE_STRING(13);

    PUT(end_string, end_string_length);
    PUT_TERMINATOR;

    *p_res_size = buffer_current_pos - buffer;
    *p_res = buffer;

    return RET_OK;
}

int max(int a, int b) {
        return a > b ? a : b;
}

ret_t append_and_free(char **p_dest, size_t *p_dest_size, size_t *p_dest_space, char *part, size_t part_size) {
    if (*p_dest_size - 1 + part_size > *p_dest_space) {
        size_t new_dest_space = max(2 * (*p_dest_space), (*p_dest_space) + 2 * part_size);
        char *new_dest = realloc(*p_dest, new_dest_space);
        if (new_dest == NULL) {
            free(part);
            free(*p_dest);
            return RET_INTERNAL_ERR + 1;
        }
        *p_dest = new_dest;
        *p_dest_space = new_dest_space;
    }
    memcpy(*p_dest + *p_dest_size - 1, part, part_size);
    (*p_dest_size) += (part_size - 1);
    free(part);
    return RET_OK;
}


ret_t get_all_airports(http_status_t *p_status, char **p_res, size_t *p_res_size, const char *target, const char *body) {
    char *res = owned_string("", NULL);
    size_t res_size = 1;
    size_t res_space = 1;
    ret_t ret_value;

    char *part;
    size_t part_size;

    BEGIN_QUERY(p_connection, "SELECT icao, iata, name, city, country, latitude, longitude, altitude, utc_offset, daylight_saving_group, tz_name, type, data_source FROM Airport")
    ITER_FETCH
        if (!is_ret_ok((ret_value = airport_row_to_string(p_statement, &part, &part_size, "\n", "\n")))) {
            return ret_value;
        }
        if (!is_ret_ok((ret_value = append_and_free(&res, &res_size, &res_space, part, part_size)))) {
            return ret_value + 20;
        }
    END_QUERY

    *p_status = HTTP_OK;
    *p_res = res;
    *p_res_size = res_size;
    return RET_OK;
}

ret_t get_all_reachable_airports(http_status_t *p_status, char **p_res, size_t *p_res_size, const char *target, const char *body) {
    char *res = owned_string("", NULL);
    size_t res_size = 1;
    size_t res_space = 1;
    ret_t ret_value;

    char *part;
    size_t part_size;

    char *query = "SELECT DISTINCT a.icao, a.iata, a.name, a.city, a.country, a.latitude, a.longitude, a.altitude, a.utc_offset, a.daylight_saving_group, a.tz_name, a.type, a.data_source "
                  "FROM Path p "
                  "JOIN AirportPath s ON p.id = s.path_id "
                  "JOIN Airport a ON s.airport_icao = a.icao "
                  "WHERE s.step_no = 0 OR s.step_no = p.db_step_nb - 1";

    BEGIN_QUERY(p_connection, query)
    ITER_FETCH
        if (!is_ret_ok((ret_value = airport_row_to_string(p_statement, &part, &part_size, "\n", "\n")))) {
            return ret_value;
        }
        if (!is_ret_ok((ret_value = append_and_free(&res, &res_size, &res_space, part, part_size)))) {
            return ret_value + 20;
        }
    END_QUERY

    *p_status = HTTP_OK;
    *p_res = res;
    *p_res_size = res_size;
    return RET_OK;
}

bool is_upper_alphanum(char c) {
    return (c >= 65 && c <= 90) || (c >= 48 && c <= 57);
}

bool is_num(char c) {
    return (c >= 48 && c <= 57);
}

bool is_snum(char c) {
    return (c >= 49 && c <= 57);
}

ret_t get_airport_by_icao(http_status_t *p_status, char **p_res, size_t *p_res_size, const char *target, const char *body) {
    ret_t ret_value;
    bool valid = true;
    if (strnlen(target, 6) != 4) {
        valid = false;
    }
    size_t i = 0;
    if (valid) {
        while (is_upper_alphanum(target[i]) && i < 4) {
            i++;
        }
        if (i < 4) {
            valid = false;
        }
    }
    if (!valid) {
        *p_res = owned_string("Invalid airport icao\r\n", p_res_size);
        *p_status = HTTP_BAD_REQUEST;
        return RET_OK;
    }

    static char query[1024];
    sprintf(query, "SELECT icao, iata, name, city, country, latitude, longitude, altitude, utc_offset, daylight_saving_group, tz_name, type, data_source FROM Airport WHERE icao = '%s'", target);
    /*
     * Oui je sais, je ne mérite pas de vivre pour avoir écrit une telle monstruosité. Ceci est un nid à injection SQL, et ne dois PAS être utilisé.
     * Cependant, compte-tenu du manque de temps, il m'est impossible de faire autrement. Et puis, j'ai ajouté des protections quand même.
     * Du coup déso pas déso ;)
     */

    BEGIN_QUERY(p_connection, query)
    ITER_FETCH
        if (!is_ret_ok((ret_value = airport_row_to_string(p_statement, p_res, p_res_size, "\n", "")))) {
            return ret_value;
        }
        *p_status = HTTP_OK;
    END_QUERY
    if (row_nb < 1) {
        *p_res = owned_string("Unknow airport icao\r\n", p_res_size);
        *p_status = HTTP_RESOURCE_NOT_FOUND;
        return RET_OK;
    }

    return RET_OK;
}

ret_t path_row_to_string(Statement *p_statement, char **p_res, size_t *p_res_size, const char *sep_string, const char *end_string, bool store) {
    Data *p_data;
    data_type_t data_type;
    Bytes *p_bytes;
    double decimal;
    int64_t integer;
    size_t number_length;
    static char number_to_string_buffer[25];
    static char first_icao_storage[5];

    size_t sep_string_length = strlen(sep_string);
    size_t end_string_length = strlen(end_string);

    if (store) {
        DO_OR_RET(dpiStmt_getQueryValue(p_statement, 3, &data_type, &p_data), 33);
        p_bytes = dpiData_getBytes(p_data);
        memcpy(first_icao_storage, p_bytes->ptr, p_bytes->length);
        first_icao_storage[4] = '\0';
        return RET_OK;
    }

    size_t buffer_size =
        24 + 24 + 4 + 4 + 1 + 13 * sep_string_length + end_string_length;
    char *buffer = ((char *) (malloc(buffer_size * sizeof(*buffer))));
    buffer[buffer_size - 1] = '\0';
    char *buffer_current_pos = buffer;

    // id
    HANDLE_INTEGER(1);
    // straight_distance
    HANDLE_DECIMAL(2);
    // source
    PUT(first_icao_storage, 4);
    PUT(sep_string, sep_string_length);
    // destination
    HANDLE_STRING(3);

    PUT(end_string, end_string_length);
    PUT_TERMINATOR;

    *p_res_size = buffer_current_pos - buffer;
    *p_res = buffer;

    return RET_OK;
}

ret_t get_all_paths(http_status_t *p_status, char **p_res, size_t *p_res_size, const char *target, const char *body) {
    char *res = owned_string("", NULL);
    size_t res_size = 1;
    size_t res_space = 1;
    ret_t ret_value;

    char *part;
    size_t part_size;

    char *query = "SELECT p.id, p.straight_distance, s.airport_icao "
                  "FROM Path p JOIN AirportPath s ON p.id = s.path_id "
                  "WHERE s.step_no = 0 OR s.step_no = p.db_step_nb - 1 "
                  "ORDER BY p.id ASC, s.step_no ASC";


    BEGIN_QUERY(p_connection, query)
    ITER_FETCH
        if (!is_ret_ok((ret_value = path_row_to_string(p_statement, &part, &part_size, "\n", "\n", true)))) {
            return ret_value + 70;
        }
        DO_OR_RET(dpiStmt_fetch(p_statement, &found, &buffer_row_index), 5);
        if (!found) {
            return RET_INTERNAL_ERR + 6;
        }
        if (!is_ret_ok((ret_value = path_row_to_string(p_statement, &part, &part_size, "\n", "\n", false)))) {
            return ret_value + 80;
        }
        if (!is_ret_ok((ret_value = append_and_free(&res, &res_size, &res_space, part, part_size)))) {
            return ret_value + 20;
        }
    END_QUERY

    *p_status = HTTP_OK;
    *p_res = res;
    *p_res_size = res_size;

    return RET_OK;
}

ret_t get_path_by_id(http_status_t *p_status, char **p_res, size_t *p_res_size, const char *target, const char *body) {
    ret_t ret_value;
    bool valid = true;
    size_t n = strnlen(target, 10);
    if (n > 8 || n == 0) {
        valid = false;
    }
    size_t i = 0;
    if (valid) {
        while (is_num(target[i]) && i < n) {
            i++;
        }
        if (i < n) {
            valid = false;
        }
    }
    valid = valid && (n == 1 || is_snum(target[0]));
    if (!valid) {
        *p_res = owned_string("Invalid path id\r\n", p_res_size);
        *p_status = HTTP_BAD_REQUEST;
        return RET_OK;
    }

    static char query[1024];
    char *query_format = "SELECT p.id, p.straight_distance, s.airport_icao "
                         "FROM Path p JOIN AirportPath s ON p.id = s.path_id "
                         "WHERE (s.step_no = 0 OR s.step_no = p.db_step_nb - 1) "
                         "AND p.id = %s "
                         "ORDER BY p.id ASC, s.step_no ASC ";

    sprintf(query, query_format, target);
    printf("%s\n", query);

    BEGIN_QUERY(p_connection, query)
    ITER_FETCH
        if (!is_ret_ok((ret_value = path_row_to_string(p_statement, p_res, p_res_size, "\n", "", true)))) {
            return ret_value + 70;
        }
        DO_OR_RET(dpiStmt_fetch(p_statement, &found, &buffer_row_index), 5);
        if (!found) {
            return RET_INTERNAL_ERR + 6;
        }
        if (!is_ret_ok((ret_value = path_row_to_string(p_statement, p_res, p_res_size, "\n", "", false)))) {
            return ret_value + 80;
        }
        *p_status = HTTP_OK;
    END_QUERY
    if (row_nb < 2) {
        *p_res = owned_string("Unknow path id\r\n", p_res_size);
        *p_status = HTTP_RESOURCE_NOT_FOUND;
        return RET_OK;
    }

    return RET_OK;
}

ret_t get_home(http_status_t *p_status, char **p_res, size_t *p_res_size, const char *target, const char *body) {
    *p_res = owned_string("Bienvenu !", p_res_size);
    *p_status = HTTP_OK;
    return RET_OK;
}

ret_t action_on_connect(sock_fd_t new_client_sock_fd, SockAddr *p_client_sock_addr, sock_addr_size_t client_sock_addr_size) {
    printf("[I] Connection of client %s as #%d\n", IPSTR(p_client_sock_addr), new_client_sock_fd);
    return RET_OK;
}

ret_t action(sock_fd_t client_sock_fd, bool is_read_ready, bool is_write_ready,
             bool is_except_ready) {

    static char read_buffer[READ_BUFFER_SIZE];

    ssize_t read_size = recv(client_sock_fd, read_buffer, READ_BUFFER_SIZE, NO_FLAGS);
    if (read_size == 0) {
        // Disconnection
        return RET_CUSTOM;
    }
    if (read_size < 0) {
        return RET_INTERNAL_ERR + 1;
    }
    printf("[I] Data received from client #%d\n", client_sock_fd);
    if (read_size == READ_BUFFER_SIZE) {
        printf("[W] Data from client #%d cut [:1024]\n", client_sock_fd);
    }

    ret_t ret_value;

    http_verb_t http_verb;
    char *target;
    size_t target_size;
    char *body;
    size_t body_size;
    http_status_t http_status;
    char *res;
    size_t res_size;
    char *http_response;
    size_t http_response_size;

    ret_value = parse_http_request(read_buffer, read_size, &http_verb, &target, &target_size, &body, &body_size);
    if (is_ret_err(ret_value)) {
        printf("[W] Invalid HTTP request from client #%d: code %d\n", client_sock_fd, ret_value);
        res = owned_string("Invalid HTTP request\r\n", &res_size);
        if (is_ret_err(make_http_response(HTTP_BAD_REQUEST, res, res_size, &http_response, &http_response_size))) {
            return RET_INTERNAL_ERR + 51;
        }
        if (is_ret_err(send_and_free(client_sock_fd, http_response, http_response_size))) {
            return RET_INTERNAL_ERR + 52;
        }
        return RET_OK;
    }

    printf("[I] Request verb: %s, target: %s, body: >>>%s<<<\n", http_verb_to_string(http_verb), target, body);

    ret_value = route(p_api, &http_status, &res, &res_size, GET, target, body);
    if (is_ret_custom(ret_value)) {
        printf("[W] No method for target \"%s\" from client #%d\n", target, client_sock_fd);
        res = owned_string("Invalid target\r\n", &res_size);
        if (is_ret_err(make_http_response(HTTP_RESOURCE_NOT_FOUND, res, res_size, &http_response, &http_response_size))) {
            return RET_INTERNAL_ERR + 53;
        }
        if (is_ret_err(send_and_free(client_sock_fd, http_response, http_response_size))) {
            return RET_INTERNAL_ERR + 54;
        }
        return RET_OK;
    }
    if (!is_ret_ok(ret_value)) {
        // I don't know what happened
        res = owned_string("Internal error\r\n", &res_size);
        if (is_ret_err(make_http_response(HTTP_INTERNAL_ERROR, res, res_size, &http_response, &http_response_size))) {
            return RET_INTERNAL_ERR + 55;
        }
        if (is_ret_err(send_and_free(client_sock_fd, http_response, http_response_size))) {
            return RET_INTERNAL_ERR + 56;
        }
        return ret_value;
    }

    if (is_ret_err(make_http_response(http_status, res, res_size, &http_response, &http_response_size))) {
        return RET_INTERNAL_ERR + 57;
    }
    //                                                                     doesn't like \0
    if (is_ret_err(send_and_free(client_sock_fd, http_response, http_response_size - 1))) {
        return RET_INTERNAL_ERR + 58;
    }

    free(target);
    free(body);
    printf("[I] Response sent to client #%d\n", client_sock_fd);

    return RET_OK;
}

ret_t action_on_disconnect(sock_fd_t client_sock_fd) {
    printf("[I] Disconnection of client #%d\n", client_sock_fd);
    return RET_OK;
}

int main(int argc, char **argv) {

    HttpCallback path_all_methods[] = {
        { GET, get_all_paths },
        HTTP_CALLBACK_END
    };
    Route path_all_route = {
        "*",
        path_all_methods,
        &ROUTE_END
    };
    HttpCallback path_methods[] = {
        { GET, get_path_by_id },
        HTTP_CALLBACK_END
    };
    Route path_subroutes[] = {
        path_all_route,
        ROUTE_END
    };
    Route path_route = {
        "path",
        path_methods,
        path_subroutes
    };

    HttpCallback airport_all_methods[] = {
        { GET, get_all_airports },
        HTTP_CALLBACK_END
    };
    Route airport_all_route = {
        "*",
        airport_all_methods,
        &ROUTE_END
    };
    HttpCallback airport_all_reachable_methods[] = {
        { GET, get_all_reachable_airports },
        HTTP_CALLBACK_END
    };
    Route airport_all_reachable_route = {
        "*?",
        airport_all_reachable_methods,
        &ROUTE_END
    };
    HttpCallback airport_methods[] = {
        { GET, get_airport_by_icao },
        HTTP_CALLBACK_END
    };
    Route airport_subroutes[] = {
        airport_all_route,
        airport_all_reachable_route,
        ROUTE_END
    };
    Route airport_route = {
        "airport",
        airport_methods,
        airport_subroutes
    };

    HttpCallback api_methods[] = {
        { GET, get_home },
        HTTP_CALLBACK_END
    };
    Route api_subroutes[] = {
        airport_route,
        path_route,
        ROUTE_END
    };
    Route api = {
        ROUTE_ORIGIN,
        api_methods,
        api_subroutes
    };

    p_api = &api;

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

    DO_OR_RAISE(dpiConn_create(p_context, username, strlen(username), password, strlen(password), db_uri, strlen(db_uri), &common_params, DEFAULT_CONNECTION_PARAMS, &p_connection), "Connection creation");

    if (!is_connection_ok(p_connection)) {
        perror("Connection failed");
        exit(1);
    }

    printf("CONNECTED\n");

    AddrInet server_addr_inet;
    port_t server_port = 8080;
    SockAddrInet server_sock_addr_inet;

    AddrInet__set_from_ipint(&server_addr_inet, INADDR_ANY);
    SockAddrInet__set(&server_sock_addr_inet, &server_addr_inet, server_port);

    sock_fd_t server_sock_fd;

    open_sock_inet_tcp_server(&server_sock_fd, &server_sock_addr_inet, 10);

    ret_t server_exit_ret_value =
        run_multiplexed_tcp_server(server_sock_fd, 1.0, &action_on_connect,
                                   &action, &action_on_disconnect, false);

    close(server_sock_fd);

    dpiConn_release(p_connection);
    dpiContext_destroy(p_context);

    printf("END\n");

    return server_exit_ret_value;
}
