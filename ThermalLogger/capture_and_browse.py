#!/usr/bin/env python3
import time, serial
import numpy as np
import matplotlib.pyplot as plt

# — CONFIGURATION —
PORT        = "/dev/cu.usbmodem175676601"
BAUD        = 115200
NUM_FRAMES  = 10        # you can set back to 100 once stable
WIDTH, HEIGHT = 32, 24
PIXELS      = WIDTH * HEIGHT
TIMEOUT_S   = 3.0       # per-frame timeout in seconds

def grab_one_frame(ser, timeout_s=TIMEOUT_S):
    """Read exactly PIXELS CSV lines (frame,row,col,temp) within timeout."""
    sum_arr   = np.zeros((HEIGHT, WIDTH), dtype=float)
    count_arr = np.zeros((HEIGHT, WIDTH), dtype=int)
    start = time.time()

    while count_arr.sum() < PIXELS:
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Timed out after {timeout_s}s, got {count_arr.sum()} pixels")
        line = ser.readline().decode('ascii', errors='ignore').strip()
        if not line:
            continue

        parts = line.split(',')
        if len(parts) != 4:
            continue

        try:
            _, r, c, t = parts
            r = int(r); c = int(c); t = float(t)
        except ValueError:
            continue

        if 0 <= r < HEIGHT and 0 <= c < WIDTH:
            sum_arr[r, c]   += t
            count_arr[r, c] += 1

    # compute per-pixel average
    with np.errstate(divide='ignore', invalid='ignore'):
        frame = sum_arr / count_arr
        frame[np.isnan(frame)] = 0
    return frame

def main():
    # 1) Open serial and reset
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    ser.reset_input_buffer()

    # 2) Countdown
    print("Capture starts in:")
    for i in range(5, 0, -1):
        print(f"  {i}")
        time.sleep(1)
    print(f"Capturing {NUM_FRAMES} frames…")

    # 3) Capture loop with timeout handling
    frames = []
    for n in range(1, NUM_FRAMES+1):
        print(f" Frame {n}/{NUM_FRAMES} …", end='', flush=True)
        try:
            fm = grab_one_frame(ser)
        except TimeoutError as e:
            print(f"\n⚠️  {e}")
            break
        frames.append(fm)
        print(" done")
    ser.close()

    if not frames:
        print("No frames captured—exiting.")
        return

    # 4) Compute average map
    avg_map = np.mean(frames, axis=0)

    # 5) Interactive back/forward browsing
    idx = 0
    N   = len(frames)
    print("\nBrowse frames: [n]ext, [p]revious, [q]uit")
    while True:
        plt.imshow(frames[idx], origin='lower', aspect='auto')
        plt.title(f"Frame {idx+1}/{N}")
        plt.colorbar(label='°C')
        plt.pause(0.1)

        cmd = input("Command (n/p/q): ").strip().lower()
        plt.clf()
        if cmd == 'n':
            if idx < N-1:
                idx += 1
            else:
                print("Already at last frame.")
        elif cmd == 'p':
            if idx > 0:
                idx -= 1
            else:
                print("Already at first frame.")
        elif cmd == 'q':
            break
        else:
            print("Use 'n', 'p', or 'q'.")

    # 6) Show average heat map
    print("Displaying average of captured frames. Done.")
    plt.imshow(avg_map, origin='lower', aspect='auto')
    plt.title("Average Heat Map")
    plt.colorbar(label='°C')
    plt.show()

if __name__ == "__main__":
    main()
