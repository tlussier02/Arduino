import time, serial
import pandas as pd
import matplotlib.pyplot as plt

PORT = "/dev/cu.usbmodem175676601"
BAUD = 115200

# 1) Open serial port, wait for Teensy
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)
ser.reset_input_buffer()

# 2) Read one full frame of CSV data
data = []
first_id = None


print("Reading one frame of data…")
while True:
    raw = ser.readline().decode('ascii', errors='ignore').strip()
    if not raw:
        continue

    parts = raw.split(',')
    if len(parts) != 4:
        # not a CSV line we expect
        continue

    try:
        fid = int(parts[0])
        row = int(parts[1])
        col = int(parts[2])
        temp = float(parts[3])
    except ValueError:
        # skip any line where conversion fails
        continue

    if first_id is None:
        first_id = fid
        print(f"Frame #{first_id} started")

    # once we see a new frame index, we're done
    if fid != first_id:
        print(f"Frame #{first_id} complete, collected {len(data)} pixels")
        break

    data.append((row, col, temp))

ser.close()

if not data:
    print("No valid data collected—check your sketch and wiring.")
    exit(1)

# 3) Build DataFrame & plot
df = pd.DataFrame(data, columns=['row','col','temp'])
heatmap = df.pivot(index='row', columns='col', values='temp')

plt.imshow(heatmap, origin='lower')
plt.colorbar(label='Temperature (°C)')
plt.title(f"Thermal Frame {first_id}")
plt.xlabel("Column")
plt.ylabel("Row")
plt.tight_layout()
plt.show()
