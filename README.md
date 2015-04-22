Serenity
====

This is a fork of https://github.com/ibanezmatt13/NORB

WARNING - This code is designed to run from startup on the Pi. This is done by running the bash scripts as executables
from the Raspberry Pi's startup folder (/etc/rc.local). For more information on this, please consult Google.


Except for the bash scripts, the code for this payload is written in Python and is run by a Pi with a few components:

- Radiometrix NTX2 radio transmitter
- Ublox Max 6 GPS chip
- Raspberry Pi Camera (Pi Cam)
- TMP102 I2C temperature sensor

The aim of this payload is to achieve a height of ~30km in a relatively short space of time with a large Helium balloon
and parachute. 

If you would like more information on this, please visit the UKHAS website: www.ukhas.org.uk 
and come talk to us on our IRC channel: #highaltitude

Thanks
