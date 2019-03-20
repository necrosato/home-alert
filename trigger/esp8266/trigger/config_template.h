//
// config_template.h
// Revl
//
// Created by Naookie Sato on 03/20/2019
// Copyright © 2018 Revl. All rights reserved.
//

#ifndef _HOME_ALERT_TRIGGER_ESP8266_TRIGGER_CONFIG_TEMPLATE_H_
#define _HOME_ALERT_TRIGGER_ESP8266_TRIGGER_CONFIG_TEMPLATE_H_

// Values populated using generate_config.sh

// Wifi Info
const char* ssid      = "SSID";
const char* password  = "PASSWORD";

// Main Server Info
String server_address = "SERVER_ADDRESS";
String server_port    = "SERVER_PORT";
String endpoint       = "/trigger";
String request_string = "http://" + server_address + ":" + server_port + endpoint;
const char* request   = request_string.c_str();

// Pull up resistor on switch pin
// LOW for a closed switch, HIGH for open.
int switch_pin = PIN;
int switch_status;
// Status led, LOW when switch closed, high when open
// TODO: I should probably wire an external led into my circuit which lights up
// when the switch closes. In reality that is what it is used for, but the blocking nature of
// http requests tend to hold the led in a state even when the switch is in fact in another state.
// But the onboard led is easy and clean, no extra wires. In reality the delay is much shorter than the
// time to open and close the switch, so it will stay for now.
int led_pin = BUILTIN_LED;

#endif  // _HOME_ALERT_TRIGGER_ESP8266_TRIGGER_CONFIG_TEMPLATE_H_
