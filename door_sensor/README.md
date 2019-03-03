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
on the microcontroller with a magnet attached to the door. The switch is
normally open when no magnetic field is present, and closes when a magnetic
field is introduced. When the door opens, the magnet on the door moves away
from the switch, so it opens. A pull up resistor will pull a pin high on the
microcontroller.

