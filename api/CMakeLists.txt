cmake_minimum_required(VERSION 3.13)
project(project_grpa1)

set(CMAKE_C_STANDARD 99)

add_executable(api
        api.c
        lib/easy_socket.c lib/easy_socket.h
        lib/ret.c lib/ret.h
        lib/http_router.c lib/http_router.h
        lib/http_status.c lib/http_status.h
        lib/easy_dpi.c lib/easy_dpi.h
        lib/http_parser.c lib/http_parser.h)

add_executable(djikstra
        djikstra.c
        lib/easy_socket.c lib/easy_socket.h
        lib/ret.c lib/ret.h
        lib/http_status.c lib/http_status.h
        lib/http_parser.c lib/http_parser.h)

add_executable(tcp
        tcp.c
        lib/easy_socket.c lib/easy_socket.h
        lib/ret.c lib/ret.h
        lib/http_status.c lib/http_status.h)

add_executable(udp
        udp.c
        lib/easy_socket.c lib/easy_socket.h
        lib/ret.c lib/ret.h
        lib/http_status.c lib/http_status.h)

find_library(ODPIC_PATH odpic)
target_link_libraries(api "${ODPIC_PATH}")
