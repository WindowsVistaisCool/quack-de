#include "ThemeRegistry.h"
#include <atomic>
#include <vector>

ThemeRegistry::~ThemeRegistry()
{
    m_themes.clear();
    m_themeStates.clear();
}

void ThemeRegistry::add(const std::string &key, Theme *theme)
{
    if (m_themes.find(key) != m_themes.end())
    {
        throw std::runtime_error("Theme with key '" + key + "' already exists.");
    }
    m_themes[key] = theme;
    m_themeStates.emplace(key, false);
}

Theme *ThemeRegistry::get(const std::string &key)
{
    auto it = m_themes.find(key);
    if (it != m_themes.end())
    {
        return it->second;
    }
    throw std::runtime_error("Theme with key '" + key + "' not found.");
}

std::vector<std::string> ThemeRegistry::list() const
{
    std::vector<std::string> themeList;
    for (const auto &pair : m_themes)
    {
        themeList.push_back(pair.first);
    }
    return themeList;
}

bool ThemeRegistry::exists(const std::string &key) const
{
    return m_themes.find(key) != m_themes.end();
}

void ThemeRegistry::clearCurrentTheme()
{
    if (currentThemeKey != "")
    {
        m_themeStates[currentThemeKey] = false;
        currentTheme->sendStopSignal();
        if (m_themeThread != nullptr)
        {
            m_themeThread->join();
            delete m_themeThread;
            m_themeThread = nullptr;
        }
    }
}

std::thread *ThemeRegistry::setCurrentTheme(const std::string &key)
{
    if (currentThemeKey != "")
    {
        m_themeStates[currentThemeKey] = false;
        // signal the running theme to stop as well so its run() can
        // exit early if it checks shouldReturn()
        if (currentTheme != nullptr) {
            currentTheme->sendStopSignal();
        }
        if (m_themeThread != nullptr)
        {
            m_themeThread->join();
            delete m_themeThread;
            m_themeThread = nullptr;
        }
    }

    currentTheme = get(key);
    currentThemeKey = key;

    m_themeStates[key] = true;

    currentTheme->init();

    m_themeThread = new std::thread([this]()
                                    {
        std::string currentThemeKeySnapshot = currentThemeKey;
        while (m_themeStates[currentThemeKeySnapshot]) {
            currentTheme->run();
        } });
    return m_themeThread;
}

Theme *ThemeRegistry::getCurrentTheme()
{
    return currentTheme;
}

std::string ThemeRegistry::getCurrentThemeKey()
{
    return currentThemeKey;
}

std::atomic<bool> &ThemeRegistry::getThemeState(const std::string &key)
{
    return m_themeStates[key];
}
