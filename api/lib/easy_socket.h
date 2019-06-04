#ifndef DEF_EASY_SOCKET
#define DEF_EASY_SOCKET

#include <stdlib.h>
#include <stdio.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include "ret.h"

#define IPSTR(ps) (inet_ntoa(((SockAddrInet *) (ps))->sin_addr))
#define NO_FLAGS 0

// http://manpagesfr.free.fr/man/man7/ip.7.html
typedef struct sockaddr SockAddr;
typedef socklen_t sock_addr_size_t;
typedef struct sockaddr_in SockAddrInet;
typedef struct in_addr AddrInet;
typedef in_addr_t addr_inet_t;
typedef struct hostent HostEntry;
typedef struct servent ServEntry;
typedef uint16_t port_t;
typedef int sock_fd_t;
typedef struct timeval Timeval;

typedef ret_t (*action_tcp_fp)(sock_fd_t, bool, bool, bool);
typedef ret_t (*action_tcp_on_connect_fp)(sock_fd_t, SockAddr *, sock_addr_size_t);
typedef ret_t (*action_tcp_on_disconnect_fp)(sock_fd_t);
typedef ret_t (*action_udp_fp)(sock_fd_t server_sock_fd, SockAddr *p_client_sock_addr, sock_addr_size_t client_sock_addr_size, char *data, size_t data_size, bool may_overflow);

/**
 * Longeur en byte de la partie utile de la struct SockAddrInet. Utilisée principalement dans bind (socket) pour le paramètre sock_len_t __len
 */
#define SOCK_ADDR_INET_LEN (sizeof(SockAddrInet))

//==============================================================================

ret_t AddrInet__set_from_hostname(AddrInet *p_addr_inet, const char *hostname);

ret_t AddrInet__set_from_ipstr(AddrInet *p_addr_inet, const char *ipstr);

ret_t AddrInet__set_from_ipint(AddrInet *p_addr_inet, addr_inet_t addr_inet_int);

ret_t SockAddrInet__set(SockAddrInet *p_sock_addr_inet, AddrInet *p_addr_inet, port_t port);

ret_t open_sock_inet_tcp(sock_fd_t *p_sock_fd, SockAddrInet *p_sock_addr_inet);

ret_t open_sock_inet_udp(sock_fd_t *p_sock_fd, SockAddrInet *p_sock_addr_inet);

ret_t open_sock_inet_tcp_server(sock_fd_t *p_sock_fd,
                                SockAddrInet *p_sock_addr_inet,
                                size_t queue_max_size);
ret_t open_sock_inet_tcp_client(sock_fd_t *p_sock_fd, SockAddrInet *p_sock_addr_inet, SockAddrInet *p_server_sock_addr_inet);

ret_t run_multiplexed_tcp_server(sock_fd_t serv_sock_fd, double timeout,
                                 action_tcp_on_connect_fp p_action_on_connect,
                                 action_tcp_fp p_action,
                                 action_tcp_on_disconnect_fp p_action_on_disconnect,
                                 bool trigger_without_read_ready);
ret_t run_udp_serv(sock_fd_t serv_sock_fd, size_t buffer_size, action_udp_fp p_action);

#endif  // DEF_EASY_SOCKET
