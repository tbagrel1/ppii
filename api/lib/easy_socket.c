#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <string.h>

#include "easy_socket.h"

/**
 * Remplit une structure AddrInet à partir d'un nom d'hôte (en faisant la résolution DNS)
 * @param p_addr_inet pointeur vers la struct SockAddrInet à remplir
 * @param hostname nom d'hôte à résoudre
 * @return une valeur RET
 */
ret_t AddrInet__set_from_hostname(AddrInet *p_addr_inet, const char *hostname) {
    // Récupère les informations sur l'hôte sous forme d'une structure HostEntry
    // Pas besoin de malloc/free, cas particulier (voir doc)
    HostEntry *host_entry = gethostbyname(hostname);
    if (host_entry == NULL) {
        return RET_INTERNAL_ERR + 1;
    }
    // Convertit la première adresse trouvée pour l'hôte de char * à in_addr_t
    // et stocke le résultat dans la structure addr_inet. En cas d'erreur,
    // inet_aton renvoie 0
    if (inet_aton(host_entry->h_addr, p_addr_inet) == 0) {
        return RET_INTERNAL_ERR + 2;
    }

    return RET_OK;
}

/**
 * Remplit une structure AddrInet à partir d'une IPv4 sous forme de chaîne
 * @param p_addr_inet pointeur vers la struct SockAddrInet à remplir
 * @param ipstr IPv4 sous forme de chaîne à convertir
 * @return une valeur RET
 */
ret_t AddrInet__set_from_ipstr(AddrInet *p_addr_inet, const char *ipstr) {
    // Convertit l'ip sous forme de chaîne en entier et stocke le résultat dans
    // la structure addr_inet. En cas d'erreur, inet_aton renvoie 0
    if (inet_aton(ipstr, p_addr_inet) == 0) {
        return RET_INTERNAL_ERR + 1;
    }

    return RET_OK;
}

/**
 * Remplit une structure AddrInet à partir d'une IPv4 sous forme d'entier
 * (par exemple, constante comme INADDR_ANY, INADDR_LOOPBACK...)
 * @param p_addr_inet pointeur vers la struct SockAddrInet à remplir
 * @param addr_inet_int IPv4 sous forme d'entier à convertir
 * @return une valeur RET
 */
ret_t AddrInet__set_from_ipint(AddrInet *p_addr_inet, addr_inet_t addr_inet_int) {
    p_addr_inet->s_addr = htonl(addr_inet_int);

    return RET_OK;
}

/**
 * Remplit une structure SockAddrInet à partir d'une struct
 * AddrInet et d'un port
 * @param p_sock_addr_inet pointeur vers la structure SockAddrInet à remplir
 * @param addr_inet pointeur vers la structure AddrInet à utiliser
 * @param port port à utiliser
 * @return une valeur RET
 */
ret_t SockAddrInet__set(SockAddrInet *p_sock_addr_inet, AddrInet *p_addr_inet, port_t port) {
    p_sock_addr_inet->sin_family = AF_INET;
    p_sock_addr_inet->sin_port = htons(port);
    p_sock_addr_inet->sin_addr = *p_addr_inet;

    return RET_OK;
}

/**
 * Créé/ouvre un socket internet TCP (SOCK_STREAM)
 * @param p_sock_fd pointeur vers la variable dans laquelle placer le descripteur de socket résultat
 * @param p_sock_addr_inet pointeur vers la struct SockAddrInet à utiliser pour le socket
 * @return une valeur RET
 */
ret_t open_sock_inet_tcp(sock_fd_t *p_sock_fd, SockAddrInet *p_sock_addr_inet) {
    *p_sock_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (*p_sock_fd == -1) {
        return RET_ERRNO_ERR;
    }
    if (bind(*p_sock_fd, (SockAddr *) (p_sock_addr_inet), SOCK_ADDR_INET_LEN) == -1) {
        return RET_ERRNO_ERR;
    }

    return RET_OK;
}

/**
 * Crée/ouvre un socket internet TCP (SOCK_STREAM), et exécute listen pour en faire un socket serveur acceptant des connexions clients
 * @param p_sock_fd pointeur vers la variable dans laquelle placer le descripteur de socket résultat
 * @param p_sock_addr_inet pointeur vers la struct SockAddrInet à utiliser pour le socket (serveur)
 * @param queue_max_size taille maximale de la file de clients en attente de connexion
 * @return une valeur RET
 */
ret_t open_sock_inet_tcp_serv(sock_fd_t *p_sock_fd, SockAddrInet *p_sock_addr_inet, size_t queue_max_size) {
    ret_t return_value = open_sock_inet_tcp(p_sock_fd, p_sock_addr_inet);
    if (!is_ret_ok(return_value)) {
        return return_value;
    }

    if (listen(*p_sock_fd, (int) queue_max_size) == -1) {
        return RET_ERRNO_ERR;
    }

    return RET_OK;
}

void _reset_sets(sock_fd_t serv_sock_fd, const fd_set *p_client_set,
                 fd_set *p_read_set, fd_set *p_write_set, fd_set *p_except_set) {
    memcpy(p_read_set, p_client_set, sizeof(fd_set));
    memcpy(p_write_set, p_client_set, sizeof(fd_set));
    memcpy(p_except_set, p_client_set, sizeof(fd_set));

    FD_SET(serv_sock_fd, p_read_set);
    FD_CLR(serv_sock_fd, p_write_set);
    FD_CLR(serv_sock_fd, p_except_set);
}

ret_t run_multiplexed_serv(sock_fd_t serv_sock_fd, double timeout) {
    fd_set client_set, read_set, write_set, except_set;
    FD_ZERO(&client_set);
    Timeval timeval_timeout;

    int ready_sock_fd_nb;
    int new_client_sock_fd;
    SockAddr client_sock_addr;
    sock_addr_size_t client_sock_addr_size;

    while (true) {
        _reset_sets(serv_sock_fd, &client_set, &read_set, &write_set, &except_set);
        timeval_timeout.tv_sec = (long) (timeout);
        timeval_timeout.tv_usec = (long) (timeout * 1000000) % 1000000;

        ready_sock_fd_nb =
            select(FD_SETSIZE, &read_set, &write_set, &except_set, &timeval_timeout);
        if (ready_sock_fd_nb == -1) {
            return RET_ERRNO_ERR;
        };
        if (ready_sock_fd_nb == 0) {
            continue;
        }

        // Si un client est en attente de connexion
        if (FD_ISSET(serv_sock_fd, &read_set)) {
            new_client_sock_fd = accept(serv_sock_fd, &client_sock_addr, &client_sock_addr_size);
            if (new_client_sock_fd == -1) {
                return RET_ERRNO_ERR;
            }
            FD_SET(new_client_sock_fd, &client_set);

            continue;
        }
    }

    return RET_OK;
}
