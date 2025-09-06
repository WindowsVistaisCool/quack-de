#include <iostream>
#include <thread>
#include <chrono>
#include "PixelStrip.h"
#include "themes/Fire2012.h"
#include "themes/Jerry.h"
#include "themes/Pacifica.h"
#include "themes/Rainbow.h"
#include "themes/Twinkle.h"
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
ThemeRegistry *registry = nullptr;
int connection = -1;

void parseMessage(const std::string &message);

int main()
{
    std::cout << "Starting LED Service..." << std::endl;

    // Initialize the LEDS
    PixelStrip strip(LED_COUNT, LED_PIN, LED_DMA);
    if (!strip.begin())
    {
        std::cerr << "Failed to initialize PixelStrip" << std::endl;
        return 1;
    }

    // Appoint registry
    registry = new ThemeRegistry(strip);
    registry->add("fire2012", new Fire2012(strip));
    registry->add("rgbSnake", new Jerry(strip));
    registry->add("pacifica", new Pacifica(strip));
    registry->add("rainbow", new Rainbow(strip));
    registry->add("twinkle", new Twinkle(strip));
    strip.setBrightness(150);
    themeThread = registry->setCurrentTheme("twinkle");

    // Initialize the server socket
    int server = socket(AF_INET, SOCK_STREAM, 0);
    if (server < 0)
    {
        std::cerr << "Failed to create socket" << std::endl;
        return 1;
    }
    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(5000);
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    bind(server, (sockaddr *)&server_addr, sizeof(server_addr));
    listen(server, 5);

    // Main loop
    static const std::string endMessage = "end";
    bool mainLoopActive = true;
    // loop to accept connections
    while (mainLoopActive)
    {
        connection = accept(server, nullptr, nullptr);
        if (connection < 0)
        {
            std::cerr << "Failed to accept connection" << std::endl;
            return 1;
        }

        // data receiving loop
        while (true)
        {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
            char buffer[1024] = {0};
            int bytesReceived = recv(connection, buffer, sizeof(buffer) - 1, 0);
            if (bytesReceived <= 0)
            {
                // Connection closed or error
                break;
            }
            buffer[bytesReceived] = '\0'; // Ensure null-terminated string

            if (std::string(buffer) == endMessage)
            {
                connection = -1;
#if defined(_WIN32) || defined(_WIN64)
                closesocket(server);
                WSACleanup();
#else
                close(server);
#endif
                mainLoopActive = false;
                break;
            }

            parseMessage(buffer);
        }
    }

    std::cout << "Shutting down..." << std::endl;

    return 0;
}

void parseMessage(const std::string &message)
{
    if (message.compare(0, 4, "set:") == 0) // starts with "set:"
    {
        std::string themeName = message.substr(4); // get the part after "set:"
        if (!registry->exists(themeName))
        {
            if (connection >= 0) {
                const std::string errorMsg = "Theme '" + themeName + "' does not exist.\n";
                send(connection, errorMsg.c_str(), errorMsg.size(), 0);
            }
            return;
        }
        themeThread = registry->setCurrentTheme(themeName);
    }
    else if (message.compare(0, 7, "bright:") == 0)
    {
        std::string brightness = message.substr(7); // get the part after "bright:"
        uint8_t brightnessValue = std::stoi(brightness);
        registry->m_strip.setBrightness(brightnessValue);
    }
    else if (message.compare(0, 9, "colorrgb:") == 0) {
        std::string color = message.substr(9); // get the part after "color:"
        int r = 0, g = 0, b = 0;
        sscanf(color.c_str(), "%d,%d,%d", &r, &g, &b);
        Color colorRaw(r, g, b);
        registry->m_strip.setColor(Color(colorRaw));
    }
    else if (message.compare(0, 5, "clear") == 0)
    {
        registry->m_strip.clear();
    }
    else if (message.compare(0, 6, "noloop") == 0)
    {
        registry->clearCurrentTheme();
        registry->m_strip.clear();
    }
    else if (message.compare(0, 3, "get") == 0)
    {
        std::string currentThemeKey = registry->getCurrentThemeKey();
        std::string response = "current:" + currentThemeKey + "\n";
        if (connection >= 0) {
            send(connection, response.c_str(), response.size(), 0);
        }
    }
    else if (message.compare(0, 4, "list") == 0)
    {
        std::string themeList = "themes:";
        for (const std::string key : registry->list())
        {
            themeList += key + ",";
        }
        if (!themeList.empty() && themeList.back() == ',')
        {
            themeList.pop_back(); // Remove trailing comma
        }
        themeList += "\n";
        if (connection >= 0) {
            send(connection, themeList.c_str(), themeList.size(), 0);
        }
    }
    else if (message != "")
    {
        std::cout << "> " << message << std::endl;
    }
}
