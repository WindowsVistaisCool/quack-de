#pragma once

#include <unordered_map>
#include "Theme.h"
#include <string>
#include <stdexcept>
#include <thread>
#include <atomic>

class ThemeRegistry {
    public:
        ThemeRegistry(PixelStrip& pixelStrip) : m_strip(pixelStrip) {
            currentTheme = nullptr;
            currentThemeKey = "";
            m_themeThread = nullptr;
        }
        ~ThemeRegistry();

        void add(const std::string& key, Theme* theme);
        Theme* get(const std::string& key);
        bool exists(const std::string& key) const;

        void clearCurrentTheme();
        std::thread* setCurrentTheme(const std::string& key);
        Theme* getCurrentTheme();
        std::string getCurrentThemeKey();

        std::atomic<bool>& getThemeState(const std::string& key);

        PixelStrip& m_strip;
    private:
        std::unordered_map<std::string, Theme*> m_themes;
        std::unordered_map<std::string, std::atomic<bool>> m_themeStates;
        Theme* currentTheme;
        std::string currentThemeKey;
        std::thread* m_themeThread;
};