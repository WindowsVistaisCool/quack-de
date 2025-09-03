cmake_minimum_required(VERSION 3.12)

project(led_service CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add the rpi ws281x subproject (submodule expected at service/rpi_281x)
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/rpi_281x)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/rpi_281x)

# Automatically gather all .cpp sources in this directory. Using CONFIGURE_DEPENDS
# causes CMake to re-run when files are added/removed (requires CMake >= 3.12).
file(GLOB SERVICE_SOURCES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp")

add_executable(service ${SERVICE_SOURCES})

target_include_directories(service PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(service PRIVATE ws2811 m pthread)
