# Door Sensor

Each door sensor will be very simple. Just a microcontroller with TCP/IP
capabilities and a sensor to detect when the door has been opened. The
microcontroller should process the sensor data and then make a web request to
an endpoint of the main server to notify it.

# Microcontroller
I have chosen to use an (ESP8266)[https://en.wikipedia.org/wiki/ESP8266]. They
are low cost, less than 7 USD on amazon for the development board. These chips
are much faster than an arduino and have a full TCP/IP stack.

# Sensor
In practice I will use a (reed switch)[https://en.wikipedia.org/wiki/Reed_switch]
on the microcontroller with a magnet attached to the door. Assuming the switch
is normally open when no magnetic field is present, when the door opens, the
reed switch will be opened and pull a pin low on the microcontroller.

