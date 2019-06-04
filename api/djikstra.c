#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

#include "lib/http_router.h"
#include "lib/easy_socket.h"
#include "lib/http_parser.h"

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

    close(client_sock_fd);
    return 0;
}
