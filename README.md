# rpi-matrix-artnet
Controlling of 32x32 or 16x32 RGB LED displays using Raspberry Pi rpi-rgb-led-matrix with Art-Net 

Art-Net is a protocol for controlling lights over a network. Glediator / Jinx
controls LEDs on one or more Art-Net nodes. An Art-Net node drives the
LEDs. In this example, Glediator / Jinx runs on a laptop and controls a Pi with
a rpi-rgb-led-matrix RGB LED displays using Raspberry Pi. The Pi is the Art-Net node.
A RGB LED displays 32x32 / 32x16 / 64x64 is an add-on board connected for a Raspberry Pi+/3

http://www.solderlab.de/index.php/software/glediator

https://en.wikipedia.org/wiki/Art-Net

## Preliminary

RGB LED displays rpi-rgb-led-matrix Program for Raspberry Pi must be installed and working on the Pi
supplied Python software. Make sure this works before graduating to Art-Net.

https://github.com/hzeller/rpi-rgb-led-matrix

or

https://github.com/darknessii/rpi-rgb-led-matrix

## Install libraries on the Pi

Do this only once to install the Python twisted libraries.

```
sudo apt-get install python-twisted
```

## Run Art-Net server rpi-matrix-artnet on the Pi
The following command runs the Art-Net server turning the Pi into an Art-Net node. 
Many programs can send LED values to an Art-Net node. Glediator and Jinx is such a
program.

```
sudo python rpi-matrix-artnet.py
```


## NOT working
* Art-Net Net & Subnet

## TO DO
* Code Clean Up

## Jinx!

http://www.live-leds.de/

Jinx! – LED Matrix Control

Jinx!, is a free available software for controlling LED matrices.

## Glediator

See the Glediator download page to download and install Glediator.


## PixelController

https://github.com/neophob/PixelController/releases

PixelController is another LED pattern generator with Art-Net output. After
unzipping pixelcontroller-distribution-2.1.0-RC1.zip change into the directory
pixelcontroller-distribution-2.1.0-RC. Copy config.properties from this
repo to the directory data.

Edit data/config.properties to set the IP address of the Pi.

```
# Change the following line to match the IP of your Pi
artnet.ip=192.168.1.231
```

Next run the program. The Unicorn Hat should immediately show pixel patterns.

```
unzip pixelcontroller-distribution-2.1.0-RC1.zip
cd pixelcontroller-distribution-2.1.0-RC
cp ~/artnet-unicorn-hat/config.properties data/
nano data/config.properties
java -jar PixelController.jar
```

