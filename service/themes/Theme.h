#pragma once

#include <atomic>
#include <string>

class PixelStrip; // forward-declare

class Theme {
public:
    explicit Theme(PixelStrip& strip) : strip(strip) {}
    virtual ~Theme() = default;

    // lifecycle
    virtual void init() final {
        returnSig = false;
        themeInit();
    };
    virtual void run() = 0;

    virtual void setAttribute(const std::string &key, const std::string &value) {};

    inline virtual void sendStopSignal() final {
        returnSig = true;
    }

protected:
    inline bool shouldReturn() const {
        return returnSig;
    }

    virtual void themeInit() = 0;

    PixelStrip& strip;
    std::atomic<bool> returnSig;
};