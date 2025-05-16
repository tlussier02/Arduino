#!/usr/bin/env python3
import time
import sys
import numpy as np
import matplotlib.pyplot as plt

# try to import pyserial; if missing, instruct
try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("🔴 Missing pyserial. Install with:\n    pip3 install pyserial")
    sys.exit(1)

# — CONFIGURATION —
BAUD       = 115200
NUM_FRAMES = 30
WIDTH      = 32
HEIGHT     = 24
PIXELS     = WIDTH * HEIGHT
TIMEOUT_S  = 5.0

def find_teensy_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        # look for the typical Teensy identifiers
        if "usbmodem" in p.device or "ttyACM" in p.device:
            return p.device
    raise RuntimeError("Teensy port not found. Is it plugged in and not held open elsewhere?")

def grab_one_frame(ser, timeout_s=TIMEOUT_S):
    sum_arr   = np.zeros((HEIGHT, WIDTH), dtype=float)
    count_arr = np.zeros((HEIGHT, WIDTH), dtype=int)
    t0 = time.time()

    while count_arr.sum() < PIXELS:
        if time.time() - t0 > timeout_s:
            raise TimeoutError(f"Timed out after {timeout_s}s, got {count_arr.sum()} pixels")
        line = ser.readline().decode('ascii', errors='ignore').strip()
        if not line:
            continue
        parts = line.split(',')
        if len(parts) != 4:
            continue
        _, r, c, t = parts
        try:
            r = int(r); c = int(c); t = float(t)
        except ValueError:
            continue
        if 0 <= r < HEIGHT and 0 <= c < WIDTH:
            sum_arr[r, c]   += t
            count_arr[r, c] += 1

    # average and zero‐fill missing
    with np.errstate(divide='ignore', invalid='ignore'):
        frame = sum_arr / count_arr
        frame[np.isnan(frame)] = 0
    return frame

class HeatmapSnippet:
    def __init__(self, port=None, baud=BAUD):
        self.port = port or find_teensy_port()
        self.baud = baud

    def capture(self, n_frames=NUM_FRAMES, countdown=3):
        print(f"→ Using port: {self.port}")
        # make sure no other process is holding the port
        print("…opening serial port")
        with serial.Serial(self.port, self.baud, timeout=1) as ser:
            time.sleep(2)
            ser.reset_input_buffer()

            print("Capture starting in:")
            for i in range(countdown, 0, -1):
                print(f"  {i}"); time.sleep(1)
            print(f"Capturing {n_frames} frames…")

            frames = []
            for i in range(1, n_frames+1):
                print(f" Frame {i}/{n_frames} …", end='', flush=True)
                try:
                    fm = grab_one_frame(ser)
                except TimeoutError as e:
                    print(f"\n⚠️  {e}\nAborting capture.")
                    break
                frames.append(fm)
                print(" done")
        if not frames:
            raise RuntimeError("No frames captured.")
        return frames

    def browse(self, frames):
        idx = 0
        N   = len(frames)
        print("\nBrowse frames: [n]ext, [p]revious, [q]uit")
        plt.ion()
        fig, ax = plt.subplots()
        img = ax.imshow(frames[0], origin='lower', aspect='auto')
        cbar = fig.colorbar(img, ax=ax, label='°C')
        ax.set_title(f"Frame 1/{N}")

        while True:
            cmd = input("Command (n/p/q): ").strip().lower()
            if cmd == 'n' and idx < N-1:
                idx += 1
            elif cmd == 'p' and idx > 0:
                idx -= 1
            elif cmd == 'q':
                break
            else:
                print("Use 'n', 'p', or 'q'.")
                continue

            img.set_data(frames[idx])
            ax.set_title(f"Frame {idx+1}/{N}")
            fig.canvas.draw_idle()

        plt.ioff()
        plt.show()

    def average_map(self, frames):
        return np.mean(frames, axis=0)

def main():
    demo = HeatmapSnippet()
    frames = demo.capture()
    demo.browse(frames)
    avg = demo.average_map(frames)
    plt.figure()
    plt.imshow(avg, origin='lower', aspect='auto')
    plt.title("Average Heat Map")
    plt.colorbar(label='°C')
    plt.show()

if __name__ == "__main__":
    main()
