#!/usr/bin/python
import os
import serial
import crcmod
import time
import time as time_
import smbus
import picamera

# Byte array for a UBX command CFG-NAV5 with parameters to set flight mode
setNav = bytearray.fromhex("B5 62 06 24 24 00 FF FF 06 03 00 00 00 00 10 27 00 00 05 00 FA 00 FA 00 64 00 2C 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 16 DC")
# Byte array for UBX command CFG-PRT with parameters to disable automatic NMEA response from GPS
setNMEA_off = bytearray.fromhex("B5 62 06 00 14 00 01 00 00 00 D0 08 00 00 80 25 00 00 07 00 01 00 00 00 00 00 A0 A9")
# Function for CRC-CCITT checksum
crc16f = crcmod.predefined.mkCrcFun('crc-ccitt-false')
# RIP, best show ever
callsign = "Serenity"

class DummyCam(object):
    def __init__(self):
        pass

    def capture(self, imgName):
        print 'Unable to capture image ' + str(imgName)

# Disable specified NMEA sentences in GPS
def gps_disable_sentences():
    GPS = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
    GPS.write("$PUBX,40,GLL,0,0,0,0*5C\r\n")
    GPS.write("$PUBX,40,GSA,0,0,0,0*4E\r\n")
    #GPS.write("$PUBX,40,RMC,0,0,0,0*47\r\n")
    GPS.write("$PUBX,40,GSV,0,0,0,0*59\r\n")
    GPS.write("$PUBX,40,VTG,0,0,0,0*5E\r\n")
    #GPS.write("$PUBX,40,GGA,0,0,0,0*5A\r\n")
    GPS.close()

# Sends vendor-specific commands to the GPS 
def sendUBX(ubx_msg):
    length = len(ubx_msg)
    GPS = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
    ubxcmds = ""
    for i in range(0, length):
        GPS.write(chr(ubx_msg[i])) # Write each byte of ubx cmd to serial port
        ubxcmds = ubxcmds + str(ubx_msg[i]) + " " # Build up sent message debug output string
    GPS.write("\r\n")
    print "Sent UBX Command: ", ubxcmds
    GPS.close()

# Send ASCII over serial port to radio transmitter
def sendRF(data):
    NTX2 = serial.Serial('/dev/ttyAMA0', 50, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_TWO)
    NTX2.write(data)
    print "Sent over RF: ", data
    NTX2.close()

# Read the gps and return data processed for sending over radio
def getGpsPosAndTime():
    global counter
    try:
        satellites = 0
        lats = 0
        northsouth = 0
        lngs = 0
        westeast = 0
        altitude = 0
        time = 0
        latitude = 0
        longitude = 0
        NMEA_sentence = ""
        GPS = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
        #GPS.write("$PUBX,00*33\n") # request a PUBX sentence
        while NMEA_sentence.startswith("$GPRMC") == False:
            NMEA_sentence = GPS.readline()
        print "RMC sentence read:", NMEA_sentence
        rmc_data = NMEA_sentence.split(",") # split sentence into individual fields
        while NMEA_sentence.startswith("$GPGGA") == False: #GGA message holds altitude
            NMEA_sentence = GPS.readline()
        print "GGA sentence read:", NMEA_sentence
        gga_data = NMEA_sentence.split(",") # split sentence into individual fields
        GPS.close() # close serial
        # parsing required telemetry fields
        lats = rmc_data[3]
        northsouth = rmc_data[4]
        lngs = rmc_data[5]
        westeast = rmc_data[6]
        time = rmc_data[1]
	if time != "":
        	time = float(time) # I have no idea why this works
        	time = "%06i" % time # Convert to string and ensure 0 is included at start if any
        	hours = time[0:2]
        	minutes = time[2:4]
        	seconds = time[4:6]
        	time = str(str(hours) + ':' + str(minutes) + ':' + str(seconds)) # 'hh:mm:ss'
        latitude = convert(lats, northsouth)
        longitude = convert(lngs, westeast)
        if len(gga_data[9]) > 0:
            altitude = int(float(gga_data[9]))
        satellites = gga_data[7]
        if rmc_data[2] == "A":
            print "GPS position fixed!"
        else:
            print "No GPS position fix."
            return str(time) + ',' + str(latitude) + ',' + str(longitude) + ',' + str(altitude) + ',' + str(satellites) + ',NOFIX'
        return str(time) + ',' + str(latitude) + ',' + str(longitude) + ',' + str(altitude) + ',' + str(satellites)
    except Exception:
	raise
        return 'GPSCRASH:' + NMEA_sentence # Hopefully transmit something useful

# Convert latitude and longitude into the right format for dl-fldigi (used on the ground)
def convert(position_data, orientation):
        if len(position_data) == 0 or len(orientation) == 0:
            return ""
        decs = "" 
        decs2 = "" 
        for i in range(0, position_data.index('.') - 2): 
            decs = decs + position_data[i]
        for i in range(position_data.index('.') - 2, len(position_data) - 1):
            decs2 = decs2 + position_data[i]
        position = float(decs) + float(str((float(decs2)/60))[:8])
        if orientation == ("S") or orientation == ("W"): 
            position = 0 - position 
        return position

# Returns temperature value in celsius on the format "25.1", or "0.0" if there is an error
def getTemperature():
    try:
        bus = smbus.SMBus(1)
        data = bus.read_i2c_block_data(0x48, 0)
        msb = data[0]
        lsb = data[1]
        temp1dec = (((msb << 8) | lsb) >> 4) * 0.0625
        return "%.1f" % temp1dec
    except Exception:
	print "Error reading temperature"
        return "0.0"

# Calculate CRC-CCITT checksum
def getCrc(datastr):
    csum = str(hex(crc16f(datastr))).upper()[2:]
    csum = csum.zfill(4)
    return csum

if __name__ == "__main__":
    counter = 0
    # Don't crash if camera breaks
    try:
        camera = picamera.PiCamera()
    except Exception as e:
        print e
        camera = DummyCam()
    while True:
        gps_disable_sentences()
        sendUBX(setNav)
        time.sleep(0.5)
        rfdatastr = callsign
        rfdatastr += "," + str(counter)
        rfdatastr += "," + getGpsPosAndTime()
        rfdatastr += "," + getTemperature()
        rfdatastr += "*" + getCrc(rfdatastr) + "\n"
        rfdatastr = "$$" + rfdatastr
        sendRF(rfdatastr)
        imgName = '/home/pi/Serenity/image-'+str(counter)+'.jpg'
        while os.path.isfile(imgName):
            counter += 5
            imgName = 'image-'+str(counter)+'.jpg'
        if counter % 5 == 0:
            print 'Saving camera image ' + imgName
            try:
                camera.capture(imgName, resize=[1920,1080])
            except Exception as e:
                print e
        counter += 1 # Increment sentence ID for next transmission
        time.sleep(1)
