# Trigger

Trigger controllers can be anything that is capable of sending an http request to a main server.

When its conditions are met, it sents a request to `http://home-alert.location/trigger` for the main server to possibly send a notification or capture video.

Outlined here is example code for an ESP8266 module compiled using the arduino IDE with a single switch.
