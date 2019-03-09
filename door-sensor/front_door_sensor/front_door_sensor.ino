//
// front_door_sensor.ino
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

// Wifi Info
const char* ssid      = "";
const char* password  = "";

// Main Server Info
String server_ip      = "10.0.0.138";
String server_port    = "5000";
String endpoint       = "/front_door_open";
String request_string = "http://" + server_ip + ":" + server_port + endpoint;
const char* request   = request_string.c_str();

int wifi_status;

// Pull up resistor on switch pin
// LOW for a closed switch, HIGH for open.
int switch_pin = D6;
int switch_status;
// Status led, LOW when switch closed, high when open
// TODO: I should probably wire an external led into my circuit which lights up
// when the switch closes. In reality that is what it is used for, but the blocking nature of
// http requests tend to hold the led in a state even when the switch is in fact in another state.
// But the onboard led is easy and clean, no extra wires. In reality the delay is much shorter than the
// time to open a door, so it will stay for now.
int led_pin = BUILTIN_LED;

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

void OnDoorOpen() {
  Serial.println("Door opened");
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

void OnDoorClose() {
  Serial.println("Door closed");
}

// This detects change in switch state
void CheckDoorOpen() {
  int switch_status_last = switch_status;
  switch_status = digitalRead(switch_pin);
  if (switch_status != switch_status_last) {
    // TODO: This is a hack because my dev board's builtin led is connected to vcc,
    // so LOW turns it on and HIGH turns it off.
    // See https://github.com/nodemcu/nodemcu-devkit-v1.0/issues/16
    digitalWrite(led_pin, !switch_status);
    if (switch_status == HIGH) {
      OnDoorOpen();
    } else {
      OnDoorClose();
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
    CheckDoorOpen();
  }
  delay(100); // check for connection every once a second
}
