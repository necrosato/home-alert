# Home Alert

This repo holds code for an automated home security/IOT system. There will be
a central event processing server, something like a raspberry pi. Then several
IOT boards, for example the esp8266 or esp32, will be used to process sensor
data and send information back to the server.

# Git Submodules

Note that this repo uses git submodules. Cloning all components will require
```
git clone --recurse-submodules https://github.com/necrosato/home-alert
```
or if already cloned
```
git submodule init
git submodule update
```
