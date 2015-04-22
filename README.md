Serenity
====

This is a fork of https://github.com/ibanezmatt13/NORB

This code is meant to run on a Raspberry Pi as part of a High-Altitude Balloon (HAB), with the primary objective of taking a picture at about 30km altitude. The payload is going to be recovered by continuously transmitting the GPS position over radio whilst the payload lands using a parachute.

The code for this payload is written in Python and is run by a Pi connected to a few components:

- Radiometrix NTX2 radio transmitter
- Ublox Max 6 GPS chip
- Raspberry Pi Camera (Pi Cam)
- TMP102 I2C temperature sensor

This code is designed to run from startup on the Pi. This is done by running the bash scripts as executables from the Raspberry Pi's startup folder (/etc/rc.local). For more information on this, please consult Google.

Since the radio is connected to the Raspberry Pi UART, it is essential that you disable all linux kernel communication with the serial port.

If you would like more information on High-Altitude Ballooning, please visit the UKHAS website: www.ukhas.org.uk and come talk to us on our IRC channel: #highaltitude
