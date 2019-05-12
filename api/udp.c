#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

#include "lib/easy_socket.h"
#include "string.h"

ret_t action(sock_fd_t server_sock_fd, SockAddr *p_client_sock_addr, sock_addr_size_t client_sock_addr_size, char *data, size_t data_size, bool may_overflow) {
    data[data_size - 1] = '\0';
    while (data_size > 2 && data[data_size - 2] == '\r') {
        data[(data_size--) - 2] = '\0';
    }

    printf("[I] Data from client %s: >>>%s<<<%s\n", IPSTR(p_client_sock_addr), data, may_overflow ? " cut [:1024]" : "");

    data[data_size - 1] = '\n';

    if (sendto(server_sock_fd, data, data_size, NO_FLAGS, p_client_sock_addr, client_sock_addr_size) < data_size) {
        return RET_INTERNAL_ERR + 2;
    }

    return RET_OK;
}


int main() {

    AddrInet server_addr_inet;
    port_t server_port = 8080;
    SockAddrInet server_sock_addr_inet;

    AddrInet__set_from_ipint(&server_addr_inet, INADDR_ANY);
    SockAddrInet__set(&server_sock_addr_inet, &server_addr_inet, server_port);

    sock_fd_t server_sock_fd;

    open_sock_inet_udp(&server_sock_fd, &server_sock_addr_inet);

    printf("Server exit code: %d\n", run_udp_serv(server_sock_fd, 1024, &action));

    close(server_sock_fd);

    return 0;
}
