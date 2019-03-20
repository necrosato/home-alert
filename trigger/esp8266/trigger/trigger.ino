//
// trigger.ino
// Naookie Sato
//
// Created by Naookie Sato on 03/02/2019
// Copyright © 2018 Naookie Sato. All rights reserved.
//

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <stdlib.h>
// This might need to be included when using some esp8266 arduino cores.
//#include "pins_arduino.h"
#include "config.h"

int wifi_status;

void setup() {
  delay(1000);
  Serial.begin(115200);         // Start the Serial communication to send messages to the computer
  delay(1000);
  Serial.println('\n');

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);             // Connect to the network
  Serial.print("Connecting to ");
  Serial.print(ssid);
  Serial.println(" ...");

  int i = 0;
  while ((wifi_status = WiFi.status()) != WL_CONNECTED) { // Wait for the Wi-Fi to connect
    delay(1000);
    Serial.print(++i);
    Serial.print(' ');
  }

  Serial.println('\n');
  Serial.println("Connection established!");
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());         // Send the IP address of the ESP8266 to the computer
  pinMode(switch_pin, INPUT_PULLUP);
  pinMode(led_pin, OUTPUT);
  switch_status = digitalRead(switch_pin);
  digitalWrite(led_pin, !switch_status);
}

void OnSwitchOpen() {
  Serial.println("Switch opened");
  Serial.print("Sending request to main server: ");
  Serial.println(request);
  HTTPClient http;
  http.begin(request);
  int ret_code = http.GET();
  if (ret_code < 0) {
    // TODO: Don't ignore failures.
    Serial.println("Endpoint request failed");
  }
}

void OnSwitchClose() {
  Serial.println("Switch closed");
}

// This detects change in switch state
void CheckSwitchOpen() {
  int switch_status_last = switch_status;
  switch_status = digitalRead(switch_pin);
  if (switch_status != switch_status_last) {
    // TODO: This is a hack because my dev board's builtin led is connected to vcc,
    // so LOW turns it on and HIGH turns it off.
    // See https://github.com/nodemcu/nodemcu-devkit-v1.0/issues/16
    digitalWrite(led_pin, !switch_status);
    if (switch_status == HIGH) {
      OnSwitchOpen();
    } else {
      OnSwitchClose();
    }
  }
}

void loop() {
  int wifi_status_last = wifi_status;
  int wifi_status = WiFi.status();

  if (wifi_status != wifi_status_last) {
    if(wifi_status == WL_CONNECTED){
      Serial.println("");
      Serial.println("Your ESP is connected!");
      Serial.println("Your IP address is: ");
      Serial.println(WiFi.localIP());
    } else {
      Serial.println("");
      Serial.println("WiFi not connected");
    }
  }
  if(wifi_status == WL_CONNECTED){
    CheckSwitchOpen();
  }
  delay(100); // check for connection every once a second
}
