cmake_minimum_required(VERSION 3.10)

project(led_service CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add the rpi ws281x subproject (submodule expected at service/rpi_281x)
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/rpi_281x)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/rpi_281x)

add_executable(service
	main.cpp
	PixelStrip.cpp
	themes/Fire2012.cpp
	themes/Rainbow.cpp
    themes/Pacifica.cpp
)

target_include_directories(service PRIVATE ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/themes)
target_link_libraries(service PRIVATE ws2811 m pthread)
