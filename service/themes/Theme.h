#pragma once

class PixelStrip; // forward-declare

class Theme {
public:
    explicit Theme(PixelStrip& strip) : strip(strip) {}
    virtual ~Theme() = default;

    // lifecycle
    virtual void init() = 0;
    virtual void run() = 0;

protected:
    PixelStrip& strip;
};