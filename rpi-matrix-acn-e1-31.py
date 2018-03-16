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
display_size_y = 64
universum_start = 1
universum_count = 25
channel_per_univers = 510

# FrameBuffer

frameBuffer = None
frameBufferCounter = 0
rgbframeLength = 0
# Wie viele Sequencen sollen im Buffer gespeichert werden min. 4
seqBufferSize = 10
lastSequence = 0

frameArray = [[0, 0, 0, [0]]]


### RGBMatrixSetting

def rgbmatrix_options():
  options = RGBMatrixOptions()
  options.multiplexing = 5
  options.row_address_type = 0
  options.brightness = 80
  options.rows = number_of_rows_per_panel
  options.cols = number_of_columns_per_panel
  options.chain_length = number_of_panels
  options.parallel = parallel
  options.hardware_mapping = 'regular'
  options.inverse_colors = False
  options.led_rgb_sequence = "BGR"
  options.gpio_slowdown = 4
  options.pwm_lsb_nanoseconds = 130
  options.show_refresh_rate = 0
  options.disable_hardware_pulsing = True
  options.scan_mode = 1
  options.pwm_bits = 11
  options.daemon = 0
  options.drop_privileges = 0
  return options;

options = rgbmatrix_options()
display = RGBMatrix(options=options)


class sACN_E1_31(DatagramProtocol):


#    def __init__(self):
#        self.frameBuffer = None

#    def __str__(self):
#        return ("sACN_E1-31 package:\n - op_code: {0}").format(self.frameBuffer)


    def addToFrameBufferArray(self, sequence, universe, rgb_length, data):
        global frameArray
        if (sequence > -1):
#           Die Sequence Nummer wird aus dem Array gelesen
            frameSequenceInt = int(float(str(frameArray [0][0])))
#           Ist die Sequence Nummer 0, so wurde der Initial Array String erkannt
#           nach dem befuellen muss der Initail Array entfernt werden
            if (frameSequenceInt == 0):
                frameArray.append([sequence, universe, rgb_length, data])
                frameArray.pop(0)
            else:
                frameArray.append([sequence, universe, rgb_length, data])

# Diese Funktion gibt eine gesamte Sequenz auch alle Universum in einem Array zusammengezogen
    def getSequenceFromFrameBuffer(self, sequenceNr):
        global frameArray
        finalFrameArray = []
        rgbframeLength = 0
        #Sequence korrektur da es nur Sequenzen zwischen 0 und 255 geben darf
        if (sequenceNr == -1 or sequenceNr == -2):
            sequenceNr = sequenceNr + 255
        if (sequenceNr > -1):
# Sortieren des Array nach Sequence
            frameArray = sorted(frameArray,key=itemgetter(1))
            counter = 0
            bufferSize = seqBufferSize * universum_count
            while(counter < bufferSize):
                if (counter < len(frameArray)):
                    if (sequenceNr == int(float(str(frameArray [counter][0])))):
                        finalFrameArray = finalFrameArray + frameArray [counter][3]
                        rgbframeLength = rgbframeLength + int(float(str(frameArray [counter][2])))
                        frameArray.pop(counter)
                counter += 1
                if (len(frameArray) > bufferSize):
                    frameArray = [[0, 0, 0, [0]]]
            return (finalFrameArray, rgbframeLength)

    def datagramReceived(self, data, (host, port)):
        global lastSequence
        if ((len(data) > 18) and (data[4:16] == "ASC-E1.17\x00\x00\x00")):
            rawbytes = map(ord, data)
            if (len(data) > 18):
                sequence = rawbytes[111]
                universe = rawbytes[114]
                rgb_length = (rawbytes[115] << 8) + rawbytes[116]
                rgb_length = 510
                rgbdata = rawbytes[126:(rgb_length+126)]
                self.addToFrameBufferArray(sequence,universe,rgb_length,rgbdata)
                if(lastSequence != sequence):
                    frameBuffer, rgbframeLength = self.getSequenceFromFrameBuffer(sequence - 2)
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

reactor.listenUDP(5568, sACN_E1_31())
reactor.run()
