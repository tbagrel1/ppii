#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

#include "lib/http_router.h"
#include "lib/easy_socket.h"
#include "lib/http_parser.h"

static int _nothing = 0;

#define FAIL_ON_RET_ERR(func_call, msg) \
    if (!is_ret_ok(func_call)) { \
        perror(msg); \
        exit(1); \
    } _nothing = 0

#define IS_WHITE_CHAR(x) \
    (*(x) == ' ' || *(x) == '\r' || *(x) == '\n')

#define STARTS_WITH(a, b) \
    (strncmp(a, b, strlen(b)) == 0)

struct Path {
    int id;
    double distance;
    int source;
    int destination;
};
typedef struct Path Path;

ret_t parse_path(const char *data, size_t data_size, const char *sep_string, const char *end_string, Path *p_path) {
    const char *field_end;
    char *parse_end;
    size_t n = strlen(sep_string);
    field_end = strstr(data, sep_string);
    if (field_end == NULL) {
        return RET_ARG_ERR + 10 + 1;
    }
    p_path->id = (int) (strtol(data, &parse_end, 10));
    if (field_end != parse_end) {
        return RET_ARG_ERR + 10 + 2;
    }
    data = field_end + n;
    field_end = strstr(data, sep_string);
    if (field_end == NULL) {
        return RET_ARG_ERR + 10 + 3;
    }
    p_path->distance = strtod(data, &parse_end);
    if (field_end != parse_end) {
        return RET_ARG_ERR + 10 + 4;
    }
    data = field_end + n;
    field_end = strstr(data, sep_string);
    if (field_end == NULL) {
        return RET_ARG_ERR + 10 + 5;
    }
    if (data - field_end != 4) {
        return RET_ARG_ERR + 10 + 6;
    }
    p_path->source = *((int *) (data));
    data = field_end + n;
    field_end = strstr(data, sep_string);
    if (field_end == NULL) {
        return RET_ARG_ERR + 10 + 5;
    }
    if (data - field_end != 4) {
        return RET_ARG_ERR + 10 + 6;
    }
    p_path->destination = *((int *) (data));

    return RET_OK;
}

int main(int argc, char **argv) {
    AddrInet client_addr_inet;
    port_t client_port = 0;  // Random
    SockAddrInet client_sock_addr_inet;
    AddrInet__set_from_ipint(&client_addr_inet, INADDR_ANY);
    SockAddrInet__set(&client_sock_addr_inet, &client_addr_inet, client_port);

    AddrInet server_addr_inet;
    port_t server_port = 8080;
    SockAddrInet server_sock_addr_inet;
    AddrInet__set_from_ipint(&server_addr_inet, INADDR_LOOPBACK);
    SockAddrInet__set(&server_sock_addr_inet, &server_addr_inet, server_port);

    sock_fd_t client_sock_fd;

    open_sock_inet_tcp_client(&client_sock_fd, &client_sock_addr_inet, &server_sock_addr_inet);

    char *http_request;
    size_t http_request_size;

    http_verb_t http_verb = GET;
    size_t target_size;
    char *target = owned_string("/airport/*", &target_size);
    size_t body_size;
    char *body = owned_string("", &body_size);

    FAIL_ON_RET_ERR(make_http_request(http_verb, target, target_size, body, body_size, &http_request, &http_request_size), "make request");
    FAIL_ON_RET_ERR(send_and_free(client_sock_fd, http_request, http_request_size), "send");

    char *http_response;
    size_t http_response_size;
    FAIL_ON_RET_ERR(peek_and_read_http_response(client_sock_fd, &http_response, &http_response_size), "recv");

    http_status_t http_status;
    char *res;
    size_t res_size;
    FAIL_ON_RET_ERR(parse_http_response(http_response, http_response_size, &http_status, &res, &res_size), "parse response");

    printf("Response:\n%s\n", res);

    free(http_response);
    free(res);

    close(client_sock_fd);
    return 0;
}
