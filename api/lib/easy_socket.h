#ifndef DEF_EASY_SOCKET
#define DEF_EASY_SOCKET

#include <stdlib.h>
#include <stdio.h>

#include "ret.h"

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

/**
 * Longeur en byte de la partie utile de la struct SockAddrInet. Utilisée principalement dans bind (socket) pour le paramètre sock_len_t __len
 */
#define SOCK_ADDR_INET_LEN (sizeof(sa_family_t) + sizeof(port_t) + sizeof(AddrInet))

//==============================================================================

ret_t AddrInet__set_from_hostname(AddrInet *p_addr_inet, const char *hostname);

ret_t AddrInet__set_from_ipstr(AddrInet *p_addr_inet, const char *ipstr);

ret_t AddrInet__set_from_ipint(AddrInet *p_addr_inet, addr_inet_t addr_inet_int);

ret_t SockAddrInet__set(SockAddrInet *p_sock_addr_inet, AddrInet *p_addr_inet, port_t port);

ret_t open_sock_inet_tcp(sock_fd_t *p_sock_fd, SockAddrInet *p_sock_addr_inet);

#endif  // DEF_EASY_SOCKET
