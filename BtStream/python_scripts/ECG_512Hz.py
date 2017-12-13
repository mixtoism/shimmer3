#!/usr/bin/python
###################################################################
## Working example of shimmer ECG as of Dec 2017
## Pablo Arnau-Gonzalez                                            
## University of the West of Scotland
## Artifical Intelligence Visual Communacation and Networks Group
###################################################################
## Implemented in Python 3.5 win10 x64
## The program records 1000 samples and saves it with matlab format
####################################################################
import sys, struct, serial
import scipy.io as sio
import numpy as np

def wait_for_ack():
   ddata = ""
   ack = struct.pack('B', 0xff)
   while ddata != ack:
      ddata = ser.read(1)
   return

if len(sys.argv) < 2:
   print "no device specified"
   print "You need to specify the serial port of the device you wish to connect to"
   print "example:"
   print "   exgSquareWave512Hz.py Com12"
   print "or"
   print "   exgSquareWave512Hz.py /dev/rfcomm0"
else

   ser = serial.Serial(sys.argv[1], 115200)
   ser.flushInput()
# send the set sensors command
   ser.write(struct.pack('BBBB', 0x08, 0x18, 0x00, 0x00))  #exg1 and exg2 (24 bit data)
   wait_for_ack()
# send the set sampling rate command
   ser.write(struct.pack('BBB', 0x05, 0x40, 0x00)) #512Hz (64 (0x0040)). Has to be done like this for alignment reasons
   wait_for_ack()
# configure both ADS1292R chips: SET TO  WORK LIKE ECG - DEFAULT OPTIONS (see http://www.shimmersensing.com/images/uploads/docs/ECG_User_Guide_Rev1.11.pdf)
# SET_EXG REGISTERS CHIP1 START NUMBER_PARAMS PARAMS....
   ser.write(struct.pack('BBBBBBBBBBBBBB', 0x61, 0x00, 0x00, 0x0a, 0x02, 0xa0, 0x10, 0x40, 0x40, 0x20, 0x00, 0x00, 0x02, 0x03))
   wait_for_ack()
# SET_EXG REGISTERS CHIP2 START NUMBER_PARAMS PARAMS....
   ser.write(struct.pack('BBBBBBBBBBBBBB', 0x61, 0x01, 0x00, 0x0a, 0x02, 0xa0, 0x10, 0x40, 0x43, 0x00, 0x00, 0x00, 0x02, 0x02))
   wait_for_ack()

# send start streaming command
   ser.write(struct.pack('B', 0x07))
   wait_for_ack()

# read incoming data
   ddata = bytearray()
   numbytes = 0
   framesize = 18 # 1byte packet type + 3byte timestamp +  1 status + 3*2 chip1 + 1 status +3*2 chip2
   print("HOLA MUNDO")
   plt.show()
   cont = 0
   buff = []
   print( "Packet Type,Timestamp,Chip1 Status,Chip1 Channel1,Chip1 Channel2,Chip2 Status,Chip2 Channel1,Chip2 Channel2")
   try:
      while cont<5000:
         while numbytes < framesize:
            received = bytearray(ser.read(framesize))
            ddata = ddata+received
            numbytes = len(ddata)
         
         data = ddata[0:framesize]
         ddata = ddata[framesize:]
         numbytes = len(ddata)

         (packettype,) = struct.unpack('B', data[0:1])

         timestamp = struct.unpack('<i', ((data[1:4]) + b'\0'))[0] #>> 8
         (c1status,) = struct.unpack('B', data[4:5])

# 24-bit signed values MSB values are tricky, as struct only supports 16-bit or 32-bit
# pad with zeroes at LSB end and then shift the result
         c1ch1 = struct.unpack('>i', ((data[5:8]+ b'\0') ))[0] >> 8
         c1ch2 = struct.unpack('i', ((data[8:11])+ b'\0'))[0] >> 8
         (c2status,) = struct.unpack('B', data[11:12])
         c2ch1 = struct.unpack('i', (data[12:15] + b'\0'))[0] >> 8
         c2ch2 = struct.unpack('i', (data[15:18] + b'\0'))[0] >> 8
         #print( "0x%02x,%5d,\t0x%02x,%8d,%8d,\t0x%02x,%8d,%8d" % (packettype, timestamp, c1status, c1ch1, c1ch2, c2status, c2ch1, c2ch2))
         cont +=1
         buff.append(data)#(packettype, timestamp, c1status, c1ch1, c1ch2, c2status, c2ch1, c2ch2))
      x = 2

      sio.savemat('output',{'data':buff})
   #except KeyboardInterrupt:
#send stop streaming command
      ser.write(struct.pack('B', 0x20))
      wait_for_ack()
#close serial port
      ser.close()
      print('')
print( "All done")
