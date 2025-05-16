#!/usr/bin/env python3
import time, serial, collections
import numpy as np
import matplotlib.pyplot as plt

# — CONFIGURATION —
PORT        = "/dev/cu.usbmodem175676601"
BAUD        = 115200
NUM_FRAMES  = 1000            # total frames to grab for final average/median
ROLLING_N   = 100             # rolling-average window for live update
WIDTH, HEIGHT = 32, 24
PIXELS      = WIDTH * HEIGHT
TIMEOUT_S   = 5.0             # per-frame timeout

def read_raw_frame(ser, timeout_s=TIMEOUT_S):
    """Read exactly PIXELS lines of CSV (frameID,row,col,temp)."""
    data = np.full((HEIGHT, WIDTH), np.nan, dtype=float)
    count = np.zeros((HEIGHT, WIDTH), dtype=int)
    t0 = time.time()
    while count.sum() < PIXELS:
        if time.time() - t0 > timeout_s:
            raise TimeoutError(f"Timeout, got {count.sum()}/{PIXELS}")
        line = ser.readline().decode(errors='ignore').strip()
        if not line: continue
        parts = line.split(',')
        if len(parts) != 4: continue
        _, r, c, t = parts
        try:
            r = int(r); c = int(c); t = float(t)
        except ValueError:
            continue
        if 0 <= r < HEIGHT and 0 <= c < WIDTH:
            # accumulate for possible multi-hits
            if np.isnan(data[r,c]):
                data[r,c] = t
            else:
                data[r,c] = (data[r,c] + t) / 2
            count[r,c] += 1
    return data

def robust_stats(frames):
    """Given list of (H×W) arrays, do per-pixel 3σ outlier rejection
       then compute mean and median maps."""
    stack = np.stack(frames, axis=0)  # shape (N,H,W)
    mean = stack.mean(axis=0)
    std  = stack.std(axis=0)
    # mask outliers > 3σ
    mask = np.abs(stack - mean[None,:,:]) <= 3*std[None,:,:]
    # for each pixel: collect only the non-outlier samples
    cleaned = np.where(mask, stack, np.nan)
    mean_clean = np.nanmean(cleaned, axis=0)
    median_clean = np.nanmedian(cleaned, axis=0)
    return mean_clean, median_clean

def main():
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    ser.reset_input_buffer()

    # 1) Warm up rolling buffer
    rolling = collections.deque(maxlen=ROLLING_N)
    print(f"Collecting initial {ROLLING_N} frames for rolling buffer…")
    for i in range(ROLLING_N):
        rolling.append(read_raw_frame(ser))

    # 2) Live-updating display of rolling average
    plt.ion()
    fig, ax = plt.subplots()
    img = ax.imshow(np.zeros((HEIGHT,WIDTH)), origin='lower', aspect='auto')
    cb = fig.colorbar(img, ax=ax, label='°C')
    print("Live rolling-average display (press Ctrl+C to finish)…")
    try:
        while True:
            frm = read_raw_frame(ser)
            rolling.append(frm)
            mean_roll = np.nanmean(np.stack(rolling), axis=0)
            img.set_data(mean_roll)
            ax.set_title(f"Rolling mean over last {len(rolling)} frames")
            plt.pause(0.01)
    except KeyboardInterrupt:
        pass
    plt.ioff()
    print(f"\nNow capturing full batch of {NUM_FRAMES} frames…")
    
    # 3) Capture full set
    batch = []
    for n in range(NUM_FRAMES):
        print(f" Frame {n+1}/{NUM_FRAMES}", end='\r')
        batch.append(read_raw_frame(ser))
    ser.close()

    # 4) Compute robust mean & median
    mean_map, median_map = robust_stats(batch)
    print("\nDisplaying final robust maps…")

    fig, axes = plt.subplots(1,2, figsize=(10,4))
    for ax, data, title in zip(axes, (mean_map, median_map), ("Mean", "Median")):
        im = ax.imshow(data, origin='lower', aspect='auto')
        ax.set_title(title)
        fig.colorbar(im, ax=ax, label='°C')
    plt.show()

if __name__ == "__main__":
    main()
