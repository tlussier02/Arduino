# Arduino
Portable Thermal Imaging Platform

This repository contains the hardware designs and firmware for a portable thermal imaging platform using the Adafruit MLX90640 infrared sensor and Teensy 4.0 microcontroller. It captures 32×24 thermal frames, logs raw temperature data to microSD as CSV, and generates grayscale heatmap images in PPM format.

Features

Real-time capture of 768-pixel infrared frames (32×24) via MLX90640 over I²C

High-speed processing on Teensy 4.0 (600 MHz, 1 MB SRAM) to avoid memory limits

Data logging to microSD in CSV (thermal.csv) with frame, row, column, temperature

Automatic heatmap image creation (heatmap.ppm) via custom HeatMap class

USB serial status and debug output at 115200 baud

Hardware Components

Teensy 4.0 microcontroller (600 MHz ARM Cortex‑M7, 1 MB SRAM)

Adafruit MLX90640 32×24-pixel thermal sensor (I²C)

microSD card module (SPI interface)

33-pin screw-terminal expansion board for Teensy 4.0 (breaks out power and I/O)

Female–female and male–female jumper wires for sensor and SD connections

Micro‑USB cable for power and programming

Wiring

MLX90640 (I²C)

Sensor Wire

Color

Teensy 4.0 Pin

VCC

Red

3.3 V

GND

Black

GND

SDA

Yellow

18 (SDA)

SCL

Blue

19 (SCL)

microSD Module (SPI)

SD Pin

Teensy 4.0 Pin

VCC

3.3 V

GND

GND

MOSI

11 (MOSI)

MISO

12 (MISO)

SCK

13 (SCK)

CS

10 (CS)

Firmware Setup

Prerequisites

Arduino IDE (≥1.8.13)

Teensyduino

Adafruit_MLX90640 library

SD library (bundled with Arduino IDE)

Installation

Install Arduino IDE and Teensyduino.

In the IDE, go to Sketch → Include Library → Manage Libraries, search for MLX90640, and install.

Clone this repository and open the thermal_imaging.ino sketch.

Select Tools → Board → Teensy 4.0 and your USB port.

Upload the sketch.

Usage

Insert a FAT32-formatted microSD card.

Power the Teensy via USB.

Open the Serial Monitor at 115200 baud to view status messages.

After a few seconds, files thermal.csv and heatmap.ppm will be created on the SD card.

Eject the SD card and view:

thermal.csv: raw per-pixel data

heatmap.ppm: grayscale image (view in any PPM-compatible image viewer)

File Structure

/thermal_imaging/
├── thermal_imaging.ino    # Main Arduino sketch
├── README.md              # This readme file
└── examples/              # Example analysis scripts or images

Future Research Directions

Integrate on-board machine learning for real-time anomaly detection

Support higher-resolution IR arrays for finer detail

Add wireless streaming (Wi-Fi/BLE) for remote monitoring

Implement advanced calibration and thermal correction routines

Miniaturize into a low-power IoT or wearable form factor
