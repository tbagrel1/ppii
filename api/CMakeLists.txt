cmake_minimum_required(VERSION 3.13)
project(project_grpa1)

set(CMAKE_C_STANDARD 99)

add_executable(api
        src/api/demo_router.c src/lib/easy_socket.c src/lib/easy_socket.h src/lib/ret.c src/lib/ret.h src/lib/http_router.c src/lib/http_router.h src/lib/http_status.c src/lib/http_status.h)
