import serial
import time

PORT = "/dev/cu.usbmodem175676601"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)
ser.reset_input_buffer()

print("Listening for 10 seconds…")
t0 = time.time()
while time.time() - t0 < 10:
    line = ser.readline()
    if not line:
        continue
    try:
        text = line.decode('ascii', errors='ignore').rstrip()
    except:
        text = repr(line)
    print(text)
ser.close()
