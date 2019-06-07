#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <math.h>

#include "lib/http_router.h"
#include "lib/easy_socket.h"
#include "lib/http_parser.h"

static int _nothing = 0;

#define NO_NEXT NULL
#define NOT_ASSOCIATED_YET (-1)

#define FAIL_ON_RET_ERR(func_call, msg) \
    if (!is_ret_ok(func_call)) { \
        perror(msg); \
        exit(1); \
    } _nothing = 0

#define IS_WHITE_CHAR(x) \
    (*(x) == ' ' || *(x) == '\r' || *(x) == '\n')

#define STARTS_WITH(a, b) \
    (strncmp(a, b, strlen(b)) == 0)

#define IS_ALPHA_NUM(x) \
    ((*(x) >= 48 && *(x) <= 57) || (*(x) >= 65 && *(x) <= 90))

struct PathNode {
    struct PathNode *p_next;
    int id;
    double distance;
    int source_nicao;
    int destination_nicao;
};
typedef struct PathNode PathNode;

PathNode *PathNode__new(int id, double distance, int source_nicao, int destination_nicao) {
    PathNode *p_node = malloc(sizeof(*p_node));
    p_node->id = id;
    p_node->distance = distance;
    p_node->source_nicao = source_nicao;
    p_node->destination_nicao = destination_nicao;
    return p_node;
}
PathNode *PathNode__append(PathNode **pp_node, PathNode *p_node) {
    p_node->p_next = *pp_node;
    *pp_node = p_node;
    return p_node;
}
void PathNode__free(PathNode *p_node) {
    PathNode *p_next;
    while (p_node != NO_NEXT) {
        p_next = p_node->p_next;
        free(p_node);
        p_node = p_next;
    }
}

struct AdjacencyNode {
    struct AdjacencyNode *p_next;
    int path_id;
    double distance;
    int destination_no;
};
typedef struct AdjacencyNode AdjacencyNode;

AdjacencyNode *AdjacencyNode__append(AdjacencyNode **pp_node, int path_id, double distance,
                                     int destination_no) {
    AdjacencyNode *p_node = malloc(sizeof(*p_node));
    p_node->path_id = path_id;
    p_node->distance = distance;
    p_node->destination_no = destination_no;
    p_node->p_next = *pp_node;
    *pp_node = p_node;
    return p_node;
}
void AdjacencyNode__free(AdjacencyNode *p_node) {
    AdjacencyNode *p_next;
    while (p_node != NO_NEXT) {
        p_next = p_node->p_next;
        free(p_node);
        p_node = p_next;
    }
}

struct IntNode {
    struct IntNode *p_next;
    int value;
};
typedef struct IntNode IntNode;

IntNode *IntNode__append(IntNode **pp_node, int value) {
    IntNode *p_node = malloc(sizeof(*p_node));
    p_node->value = value;
    p_node->p_next = *pp_node;
    *pp_node = p_node;
    return p_node;
}
void IntNode__free(IntNode *p_node) {
    IntNode *p_next;
    while (p_node != NO_NEXT) {
        p_next = p_node->p_next;
        free(p_node);
        p_node = p_next;
    }
}
bool IntNode__contains(IntNode *p_node, int value) {
    while (p_node != NO_NEXT) {
        if (p_node->value == value) {
            return true;
        }
        p_node = p_node->p_next;
    }
    return false;
}
void IntNode__print(IntNode *p_node) {
    printf("[");
    bool first = true;
    while (p_node != NO_NEXT) {
        if (!first) {
            printf(", %d", p_node->value);
        } else {
            printf("%d", p_node->value);
            first = false;
        }
        p_node = p_node->p_next;
    }
    printf("]");
}

#define CHAR_TO_B36_DIGIT(x) \
    (((x) >= 48 && (x) <= 57) ? (x) - 48 : ((x) >= 65 && (x) <= 90) ? (x) - 55 : -1)
#define B36_DIGIT_TO_CHAR(x) \
    ((x) < 10 ? (x) + 48 : x < 36 ? ((x) - 10) + 65 : 0)

int icao_to_nicao(const char *icao) {
    return 46656 * CHAR_TO_B36_DIGIT(icao[0]) + 1296 * CHAR_TO_B36_DIGIT(icao[1]) + 36 * CHAR_TO_B36_DIGIT(icao[2]) + CHAR_TO_B36_DIGIT(icao[3]);
}

void nicao_to_icao(int nicao, char *icao) {
    int b36_digit;

    b36_digit = nicao / 46656;
    icao[0] = B36_DIGIT_TO_CHAR(b36_digit);
    nicao = nicao % 46656;

    b36_digit = nicao / 1296;
    icao[1] = B36_DIGIT_TO_CHAR(b36_digit);
    nicao = nicao % 1296;

    b36_digit = nicao / 36;
    icao[2] = B36_DIGIT_TO_CHAR(b36_digit);
    nicao = nicao % 36;

    b36_digit = nicao;
    icao[3] = B36_DIGIT_TO_CHAR(b36_digit);

    icao[4] = '\0';
}

ret_t PathNode__append_from_string(PathNode **pp_node, const char **p_data, size_t *p_data_size,
                            const char *sep_string, const char *end_string) {
    const char *field_end;
    char *parse_end;
    size_t n = strlen(sep_string);
    const char *start_data = *p_data;

    field_end = strstr(start_data, sep_string);
    if (field_end == NULL) {
        return RET_ARG_ERR + 10 + 1;
    }
    int id = (int) (strtol(start_data, &parse_end, 10));
    if (field_end != parse_end) {
        return RET_ARG_ERR + 10 + 2;
    }
    start_data = field_end + n;

    field_end = strstr(start_data, sep_string);
    if (field_end == NULL) {
        return RET_ARG_ERR + 10 + 3;
    }
    double distance = strtod(start_data, &parse_end);
    if (field_end != parse_end) {
        return RET_ARG_ERR + 10 + 4;
    }
    start_data = field_end + n;

    field_end = strstr(start_data, sep_string);
    if (field_end == NULL) {
        return RET_ARG_ERR + 10 + 5;
    }
    if (field_end - start_data != 4) {
        return RET_ARG_ERR + 10 + 6;
    }
    int source_nicao = icao_to_nicao(start_data);
    start_data = field_end + n;

    field_end = strstr(start_data, sep_string);
    if (field_end == NULL) {
        return RET_ARG_ERR + 10 + 5;
    }
    if (field_end - start_data != 4) {
        return RET_ARG_ERR + 10 + 6;
    }
    int destination_nicao = icao_to_nicao(start_data);
    start_data = field_end + n;

    PathNode *p_node = PathNode__new(id, distance, source_nicao, destination_nicao);
    PathNode__append(pp_node, p_node);

    (*p_data_size) -= (start_data - *p_data);
    *p_data = start_data;

    return RET_OK;
}

ret_t PathNode__list_from_string(PathNode **pp_node, size_t *p_list_length, const char *data, size_t data_size, const char *sep_string, const char *end_string) {
    const char *end_data = data + data_size;
    while (data < end_data && IS_WHITE_CHAR(data)) {
        data++;
    }
    *pp_node = NO_NEXT;
    *p_list_length = 0;
    size_t n = strlen(end_string);
    ret_t ret_value = PathNode__append_from_string(pp_node, &data, &data_size, sep_string, end_string);
    if (!is_ret_ok(ret_value)) {
        return ret_value;
    }
    while (is_ret_ok(ret_value)) {
        (*p_list_length)++;
        if (!STARTS_WITH(data, end_string)) {
            return RET_INTERNAL_ERR + 1;
        }
        data += n;
        data_size -= n;

        ret_value = PathNode__append_from_string(pp_node, &data, &data_size, sep_string, end_string);
    }

    return RET_OK;
}

ret_t icao_to_no(const char *icao, int *p_no, int *nicao_to_no, int *no_to_nicao, size_t vertex_nb) {
    const char *end = icao;
    while (IS_ALPHA_NUM(end)) {
        end++;
    }
    if (end - icao != 4) {
        return RET_ARG_ERR + 10 + 1;
    }
    int nicao = icao_to_nicao(icao);
    *p_no = nicao_to_no[nicao];
    if (*p_no == NOT_ASSOCIATED_YET) {
        return RET_ARG_ERR + 10 + 2;
    }
    return RET_OK;
}

ret_t no_to_icao(int no, char *icao, int *nicao_to_no, int *no_to_nicao, size_t vertex_nb) {
    if (no < 0 || no >= vertex_nb) {
        return RET_ARG_ERR + 10 + 1;
    }
    int nicao = no_to_nicao[no];
    if (nicao == NOT_ASSOCIATED_YET) {
        return RET_ARG_ERR + 10 + 2;
    }
    nicao_to_icao(nicao, icao);
    return RET_OK;
}

PathNode *PathNode__findById(PathNode *p_node, int id) {
    while (p_node != NO_NEXT) {
        if (p_node->id == id) {
            return p_node;
        }
        p_node = p_node->p_next;
    }
    return NULL;
}

void PathNode__to_adj_lists(PathNode *p_node, AdjacencyNode ***p_adj_lists, int **p_nicao_to_no, int **p_no_to_nicao, size_t *p_vertex_nb) {
    size_t vertex_nb = 0;
    IntNode *known_vertices = NO_NEXT;
    PathNode *_p_node = p_node;
    // On commence par compter le nombre de sommets différents pour la suite
    while (_p_node != NO_NEXT) {
        if (!IntNode__contains(known_vertices, _p_node->source_nicao)) {
            IntNode__append(&known_vertices, _p_node->source_nicao);
            vertex_nb++;
        }
        if (!IntNode__contains(known_vertices, _p_node->destination_nicao)) {
            IntNode__append(&known_vertices, _p_node->destination_nicao);
            vertex_nb++;
        }
        //------------------------
        _p_node = _p_node->p_next;
    }
    IntNode__free(known_vertices);

    *p_vertex_nb = vertex_nb;

    *p_nicao_to_no = malloc(1679616 * sizeof(int));  // 36^4
    for (size_t i = 0; i < 1679616; ++i) {
        (*p_nicao_to_no)[i] = NOT_ASSOCIATED_YET;
    }

    *p_no_to_nicao = malloc(vertex_nb * sizeof(int));
    for (size_t i = 0; i < vertex_nb; ++i) {
        (*p_no_to_nicao)[i] = NOT_ASSOCIATED_YET;
    }

    *p_adj_lists = malloc(vertex_nb * sizeof(AdjacencyNode *));
    for (size_t i = 0; i < vertex_nb; ++i) {
        (*p_adj_lists)[i] = NO_NEXT;
    }

    size_t next_no = 0;
    int source_no;
    int destination_no;

    while (p_node != NO_NEXT) {
        source_no = (*p_nicao_to_no)[p_node->source_nicao];
        if (source_no == NOT_ASSOCIATED_YET) {
            source_no = next_no++;
            (*p_nicao_to_no)[p_node->source_nicao] = source_no;
            (*p_no_to_nicao)[source_no] = p_node->source_nicao;
        }
        destination_no = (*p_nicao_to_no)[p_node->destination_nicao];
        if (destination_no == NOT_ASSOCIATED_YET) {
            destination_no = next_no++;
            (*p_nicao_to_no)[p_node->destination_nicao] = destination_no;
            (*p_no_to_nicao)[destination_no] = p_node->destination_nicao;
        }

        AdjacencyNode__append(&((*p_adj_lists)[source_no]), p_node->id,  p_node->distance,
                              destination_no);
        //------------------------
        p_node = p_node->p_next;
    }
}

void djikstra(int source_no, int destination_no, AdjacencyNode **adj_lists, size_t vertex_nb, double *p_min_distance, IntNode **p_id_list) {
    double *times = malloc(vertex_nb * sizeof(*times));
    int *announcers = malloc(vertex_nb * sizeof(*announcers));
    int *path_ids = malloc(vertex_nb * sizeof(*path_ids));
    bool *is_drowned = malloc(vertex_nb * sizeof(*is_drowned));

    int no;

    for (no = 0; no < vertex_nb; ++no) {
        times[no] = INFINITY;
        announcers[no] = NOT_ASSOCIATED_YET;
        path_ids[no] = NOT_ASSOCIATED_YET;
        is_drowned[no] = false;
    }
    times[source_no] = 0.0;

    int drowned_no;
    double min_time;
    double alert_time;

    for (;;) {
        drowned_no = -1;
        min_time = INFINITY;
        for (no = 0; no < vertex_nb; ++no) {
            if (!is_drowned[no] && times[no] < min_time) {
                drowned_no = no;
                min_time = times[no];
            }
        }
        if (drowned_no == destination_no) {
            break;
        }

        AdjacencyNode *p_node = adj_lists[drowned_no];
        while (p_node != NO_NEXT) {
            // On alerte les voisins
            alert_time = min_time + p_node->distance;
            if (alert_time < times[p_node->destination_no]) {
                announcers[p_node->destination_no] = drowned_no;
                path_ids[p_node->destination_no] = p_node->path_id;
                times[p_node->destination_no] = alert_time;
            }

            //----------------------
            p_node = p_node->p_next;
        }

        is_drowned[drowned_no] = true;
    }

    *p_min_distance = times[destination_no];

    *p_id_list = NO_NEXT;
    no = destination_no;
    while (no != source_no) {
        IntNode__append(p_id_list, path_ids[no]);
        no = announcers[no];
    }

    free(times);
    free(announcers);
    free(path_ids);
}

void print_djikstra_result(const char *source_icao, const char *destination_icao, PathNode *path_list, double min_distance, IntNode *id_list) {
    static char a_icao[5];
    static char b_icao[5];
    PathNode *p_path;
    IntNode *p_node;

    printf("\nShortest path for %s -> %s: %.2f km via\n", source_icao, destination_icao, min_distance);
    p_node = id_list;
    while (p_node != NO_NEXT) {
        p_path = PathNode__findById(path_list, p_node->value);
        if (p_path == NULL) {
            printf("Should not happen :/\n");
        } else {
            if (p_node != id_list) {
                printf("|");
            }
            nicao_to_icao(p_path->source_nicao, a_icao);
            nicao_to_icao(p_path->destination_nicao, b_icao);
            printf("%s ---[%d]--> %s", a_icao, p_path->id, b_icao);
        }

        //----------------------
        p_node = p_node->p_next;
    }
    printf("\n");
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
    char *target = owned_string("/path/*", &target_size);
    size_t body_size;
    char *body = owned_string("", &body_size);

    FAIL_ON_RET_ERR(make_http_request(http_verb, target, target_size, body, body_size, &http_request, &http_request_size), "make request");
    FAIL_ON_RET_ERR(send_and_free(client_sock_fd, http_request, http_request_size), "send");

    printf("[I] Waiting data from the server...\n");

    char *http_response;
    size_t http_response_size;
    FAIL_ON_RET_ERR(peek_and_read_http_response(client_sock_fd, &http_response, &http_response_size), "recv");

    printf("[I] Data received from the server\n");

    http_status_t http_status;
    char *res;
    size_t res_size;
    FAIL_ON_RET_ERR(parse_http_response(http_response, http_response_size, &http_status, &res, &res_size), "parse response");

    PathNode *path_list;
    size_t path_list_length;

    FAIL_ON_RET_ERR(PathNode__list_from_string(&path_list, &path_list_length, res, res_size, "\n", "\n"), "parse path");
    printf("[I] Found %lu paths\n", path_list_length);

    AdjacencyNode **adj_lists;
    int *nicao_to_no;
    int *no_to_nicao;
    size_t vertex_nb;

    PathNode__to_adj_lists(path_list, &adj_lists, &nicao_to_no, &no_to_nicao, &vertex_nb);

    printf("[I] Data parsed and adjacency lists built (%lu vertices found)\n", vertex_nb);

    char source_icao[5] = "nxit";
    char destination_icao[5] = "nxit";

    int source_no;
    int destination_no;
    IntNode *id_list;
    double min_distance;

    for (;;) {
        printf("\nInput (format: SRC_ICAO DST_ICAO):\n");
        scanf("%4s %4s", source_icao, destination_icao);

        if (strcmp(source_icao, "exit") == 0 || strcmp(destination_icao, "exit") == 0) {
            break;
        }

        if (is_ret_err(icao_to_no(source_icao, &source_no, nicao_to_no, no_to_nicao, vertex_nb))) {
            printf("SRC_ICAO not associated with at least one path. Sorry.\n");
            continue;
        }
        if (is_ret_err(icao_to_no(destination_icao, &destination_no, nicao_to_no, no_to_nicao, vertex_nb))) {
            printf("DST_ICAO not associated with at least one path. Sorry.\n");
            continue;
        }

        djikstra(source_no, destination_no, adj_lists, vertex_nb, &min_distance, &id_list);
        print_djikstra_result(source_icao, destination_icao, path_list, min_distance, id_list);

        IntNode__free(id_list);
    }

    // Cleanup

    PathNode__free(path_list);
    for (size_t i = 0; i < vertex_nb; ++i) {
        AdjacencyNode__free(adj_lists[i]);
    }
    free(adj_lists);
    free(nicao_to_no);
    free(no_to_nicao);

    free(http_response);
    free(res);

    close(client_sock_fd);
    return 0;
}
