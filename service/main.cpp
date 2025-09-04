#include <iostream>
#include <thread>
#include <chrono>
#include "PixelStrip.h"
#include "themes/Pacifica.h"
#include "LEDMath8.h"
#include "ThemeRegistry.h"
#if defined(_WIN32) || defined(_WIN64)
#include <winsock2.h>
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#endif
#include <atomic>

#define LED_COUNT 822
#define LED_PIN 18
#define LED_DMA 10

std::thread *themeThread = nullptr;

void parseMessage(const std::string& message);

int main() {
    // Initialize the LEDS
    PixelStrip strip(LED_COUNT, LED_PIN, LED_DMA);
    if (!strip.begin()) {
        std::cerr << "Failed to initialize PixelStrip" << std::endl;
        return 1;
    }
    strip.setBrightness(100);
    ThemeRegistry registry(strip);
    Pacifica theme(strip);
    registry.add("Pacifica", &theme);
    
    themeThread = registry.setCurrentTheme("Pacifica");

    std::this_thread::sleep_for(std::chrono::seconds(2));

    registry.clearCurrentTheme();

    strip.clear();

    std::cout << "end" << std::endl;

    // Initialize the server socket
    // int server = socket(AF_INET, SOCK_STREAM, 0);
    // if (server < 0) {
    //     std::cerr << "Failed to create socket" << std::endl;
    //     return 1;
    // }
    // sockaddr_in server_addr;
    // server_addr.sin_family = AF_INET;
    // server_addr.sin_port = htons(5000);
    // server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");

    // bind(server, (sockaddr*)&server_addr, sizeof(server_addr));
    // listen(server, 5);

    // int connection = accept(server, nullptr, nullptr);
    // if (connection < 0) {
    //     std::cerr << "Failed to accept connection" << std::endl;
    //     return 1;
    // }

    // // Main loop
    // static const std::string endMessage = "end";
    // while (true) {
    //     char buffer[1024] = { 0 };
    //     recv(connection, buffer, sizeof(buffer), 0);

    //     if (buffer == endMessage) {
    //         #if defined(_WIN32) || defined(_WIN64)
    //             closesocket(server);
    //             WSACleanup();
    //         #else
    //             close(server);
    //         #endif
    //         break;
    //     }

    //     parseMessage(buffer);
    // }

    return 0;
}

void parseMessage(const std::string& message) {
    if (message == std::string("ben")) {
        std::cout << "Hello Ben!" << std::endl;
    } else {
        std::cout << "> " << message << std::endl;
    }
}
