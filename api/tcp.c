#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

#include "lib/easy_socket.h"
#include "string.h"

#define NO_FLAGS 0
#define READ_BUFFER_SIZE 1024

ret_t action_on_connect(sock_fd_t new_client_sock_fd, SockAddr *p_client_sock_addr, sock_addr_size_t client_sock_addr_size) {
    printf("[I] Connection of client %d\n", new_client_sock_fd);
    char message[] = "bonjour !\n";
    size_t message_size = strlen(message) + 1;
    if (send(new_client_sock_fd, message, message_size, NO_FLAGS) < message_size) {
        return RET_INTERNAL_ERR + 1;
    }
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
    if (read_size == READ_BUFFER_SIZE) {
        printf("[W] Data from client %d cut [:1024]\n", client_sock_fd);
    }

    read_buffer[read_size - 1] = '\0';
    while (read_size > 2 && read_buffer[read_size - 2] == '\r') {
        read_buffer[(read_size--) - 2] = '\0';
    }

    printf("[I] Data from client %d: >>>%s<<<\n", client_sock_fd, read_buffer);

    read_buffer[read_size - 1] = '\n';
    if (send(client_sock_fd, read_buffer, read_size, NO_FLAGS) < read_size) {
        return RET_INTERNAL_ERR + 2;
    }

    return RET_OK;
}

ret_t action_on_disconnect(sock_fd_t client_sock_fd) {
    printf("[I] Disconnection of client %d\n", client_sock_fd);
    return RET_OK;
}

int main() {

    AddrInet server_addr_inet;
    port_t server_port = 8080;
    SockAddrInet server_sock_addr_inet;

    AddrInet__set_from_ipint(&server_addr_inet, INADDR_ANY);
    SockAddrInet__set(&server_sock_addr_inet, &server_addr_inet, server_port);

    sock_fd_t server_sock_fd;

    open_sock_inet_tcp_serv(&server_sock_fd, &server_sock_addr_inet, 10);

    printf("%d\n", run_multiplexed_tcp_serv(server_sock_fd, 1.0, &action_on_connect, &action,
                             &action_on_disconnect, false));

    close(server_sock_fd);

    return 0;
}
