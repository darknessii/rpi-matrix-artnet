# Art-Net protocol for rpi-rgb-led-matrix
# https://github.com/hzeller/rpi-rgb-led-matrix
# License: MIT
from twisted.internet import protocol, endpoints
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from struct import pack, unpack
from PIL import Image
from PIL import ImageDraw
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from operator import itemgetter
from collections import deque
from array import array


### Variabeln
# RGBMatrix Panel Variabeln

number_of_rows_per_panel = 32 
number_of_columns_per_panel = 32
number_of_panels = 2
parallel = 2

# Art-Net Variabeln

display_size_x = 64
display_size_y = 65
universum_start = 0
universum_count = 26
channel_per_univers = 510

# FrameBuffer

frameBuffer = None
frameBufferCounter = 0
rgbframeLength = 0
# Wie viele Sequencen sollen im Buffer gespeichert werden
seqBufferSize = 10 # Min 4 Buffer
seqBufferOffset = 2
lastSequence = 0

frameArray = [[0, 0, 0, [0]]]


### RGBMatrixSetting

def rgbmatrix_options():
  options = RGBMatrixOptions()
  options.multiplexing = 6
  options.row_address_type = 0
  options.brightness = 80 
  options.rows = number_of_rows_per_panel
  options.cols = number_of_columns_per_panel
  options.chain_length = number_of_panels
  options.parallel = parallel
  options.hardware_mapping = 'regular'
  options.inverse_colors = False
  options.led_rgb_sequence = "BGR"
  options.gpio_slowdown = 1 
  options.pwm_lsb_nanoseconds = 150
  options.show_refresh_rate = 0 
  options.disable_hardware_pulsing = True
  options.scan_mode = 0 
  options.pwm_bits = 11
  options.daemon = 0
  options.drop_privileges = 0
  return options;

options = rgbmatrix_options()
display = RGBMatrix(options=options)


class ArtNet(DatagramProtocol):


    def addToFrameBufferArray(self, sequence, universe, rgb_length, data):
        global frameArray
        if (sequence > 0):
#           Die Sequence Nummer wird aus dem Array gelesen
            frameSequenceInt = int(float(str(frameArray [0][0])))
#           Ist die Sequence Nummer 0, so wurde der Initial Array String erkannt
#           nach dem befuellen muss der Initail Array entfernt werden
            if (frameSequenceInt == 0):
                frameArray.append([sequence, universe, rgb_length, data])
                frameArray.pop(0)
            else:
                frameArray.append([sequence, universe, rgb_length, data])

    def cleanUpFrameBuffer(self, sequenceNr):
        global frameArray
        bufferCounter = 0
        bufferSize = seqBufferSize * universum_count
        while(bufferCounter < bufferSize):
            if (bufferCounter < len(frameArray)):
                if (sequenceNr >= int(float(str(frameArray [bufferCounter][0])))):
                    frameArray.pop(bufferCounter)
            bufferCounter += 1

# Diese Funktion gibt eine gesamte Sequenz auch alle Universum in einem Array zusammengezogen
    def getSequenceFromFrameBuffer(self, sequenceNr):
        global frameArray
        finalFrameArray = []
        rgbframeLength = 0
        #Sequence korrektur da es nur Sequenzen zwischen 1 und 255 geben darf
        if (sequenceNr == -1 or sequenceNr == 0):
            sequenceNr = sequenceNr + 255
        if (sequenceNr > 0):
# Sortieren des Array nach Sequence
#            frameArray = sorted(frameArray, key=lambda x: x[1])
            frameArray = sorted(frameArray,key=itemgetter(1))
            bufferCounter = 0
# der Frame Counter zaehlt die Datenpakete (Universum Pakete) in einer Sequenc
# ist ein Datenpaket verleren gegangen wird die gesamte Sequenz verworfen.
            frameCounter = 0
            bufferSize = seqBufferSize * universum_count
            while(bufferCounter < bufferSize):
                if (bufferCounter < len(frameArray)):
                    if (sequenceNr == int(float(str(frameArray [bufferCounter][0])))):
                        if (frameCounter == int(float(str(frameArray [bufferCounter][1])))):
                            frameCounter += 1
                        else:
                            self.cleanUpFrameBuffer(sequenceNr)
# Wenn daten im FrameBuffer fehlen, wird ein leerer Buffer zurueck gegeben
                            finalFrameArray = []
                            return (finalFrameArray, 0)
                        finalFrameArray = finalFrameArray + frameArray [bufferCounter][3]
                        rgbframeLength = rgbframeLength + int(float(str(frameArray [bufferCounter][2])))
                        frameArray.pop(bufferCounter)
                bufferCounter += 1
                if (len(frameArray) > bufferSize):
                    frameArray = [[0, 0, 0, [0]]]
            return (finalFrameArray, rgbframeLength)

    def datagramReceived(self, data, (host, port)):
        global lastSequence
        if ((len(data) > 18) and (data[0:8] == "Art-Net\x00")):
            rawbytes = map(ord, data)
            opcode = rawbytes[8] + (rawbytes[9] << 8)
            protocolVersion = (rawbytes[10] << 8) + rawbytes[11]
            if ((opcode == 0x5000) and (protocolVersion >= 14)):
                sequence = rawbytes[12]
                physical = rawbytes[13]
                sub_net = (rawbytes[14] & 0xF0) >> 4
                universe = rawbytes[14] & 0x0F
                net = rawbytes[15]
                rgb_length = (rawbytes[16] << 8) + rawbytes[17]
                (sequence, physical, sub_net, universe, net, rgb_length)
                rgbdata = rawbytes[18:(rgb_length+18)]
#                self.addToFrameBufferArray(sequence,universe,rgb_length,rgbdata)
# Subnet and Universum in einer Variable somit sind 256 Universum moerglich
                self.addToFrameBufferArray(sequence,rawbytes[14],rgb_length,rgbdata)
                if(lastSequence != sequence):
                    frameBuffer, rgbframeLength = self.getSequenceFromFrameBuffer(sequence - seqBufferOffset)
                    self.showDisplay(display_size_x,display_size_y,frameBuffer,rgbframeLength)
                lastSequence = sequence

    def showDisplay(self, display_size_x, display_size_y, datastream, rgb_length):
         idx = 0
         x = 0
         y = 0
         while ((idx < (rgb_length)) and (y < (display_size_y - 1))):
             r = datastream[idx]
             idx += 1
             g = datastream[idx]
             idx += 1
             b = datastream[idx]
             idx += 1
             display.SetPixel(x, y, r, g, b)
             x += 1
             if (x > (display_size_x - 1)):
                 x = 0
                 y += 1


reactor.listenUDP(6454, ArtNet())
reactor.run()
