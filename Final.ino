#include <Wire.h>
#include <Adafruit_MLX90640.h>
#include <SPI.h>
#include <SD.h>

#define SD_CS_PIN    10
#define FRAME_W      32
#define FRAME_H      24
#define FRAME_SIZE   (FRAME_W * FRAME_H)

// ------------------------------------------------------------------
// HeatMap class: map temperatures into a grayscale PPM image
// ------------------------------------------------------------------
class HeatMap {
public:
  HeatMap(float minTemp, float maxTemp)
    : _min(minTemp), _max(maxTemp) {}
  
  // Write a PPM (P6) image file with one byte per channel (R=G=B)
  void writePPM(const float *data, const char *filename) {
    File img = SD.open(filename, FILE_WRITE);
    if (!img) {
      Serial.println("ERROR: cannot open PPM file");
      return;
    }
    // PPM header
    img.print("P6\n");
    img.print(FRAME_W); img.print(' '); img.print(FRAME_H); img.print("\n255\n");
    // Pixel data
    for (int i = 0; i < FRAME_SIZE; i++) {
      uint8_t v = _map8(data[i]);
      img.write(v);
      img.write(v);
      img.write(v);
    }
    img.close();
    Serial.println("Heatmap image saved.");
  }

private:
  float _min, _max;

  // Map float temp to 0–255
  uint8_t _map8(float t) {
    if (t < _min) t = _min;
    if (t > _max) t = _max;
    return (uint8_t)( (t - _min) / (_max - _min) * 255.0f );
  }
};

// ------------------------------------------------------------------
// Globals
// ------------------------------------------------------------------
Adafruit_MLX90640 mlx;
HeatMap heatmap(20.0f, 40.0f);   // adjust to the expected temperature range

void setup() {
  Serial.begin(115200);
  while (!Serial) { /* wait */ }

  // Initialize I2C for MLX90640 on pins 18/19
  Wire.begin();

  // Init sensor
  if (!mlx.begin()) {
    Serial.println("ERROR: MLX90640 not found!");
    while (1) delay(10);
  }
  Serial.println("MLX90640 initialized");

  // Init SD card
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("ERROR: SD init failed");
    while (1) delay(10);
  }
  Serial.println("SD initialized");

  // Write CSV header (overwrite any existing file)
  File csv = SD.open("thermal.csv", FILE_WRITE);
  if (csv) {
    csv.println("Frame,Row,Col,Temp_C");
    csv.close();
  }
}

void loop() {
  static uint32_t frameCount = 0;
  float frame[FRAME_SIZE];

  // 1) Capture one frame
  if (mlx.getFrame(frame) != 0) {
    Serial.println("ERROR: failed reading frame");
    delay(1000);
    return;
  }

  // 2) Append raw data to CSV
  File csv = SD.open("thermal.csv", FILE_WRITE);
  if (!csv) {
    Serial.println("ERROR: opening CSV");
  } else {
    for (int y = 0; y < FRAME_H; y++) {
      for (int x = 0; x < FRAME_W; x++) {
        int idx = y * FRAME_W + x;
        csv.print(frameCount); csv.print(',');
        csv.print(y);          csv.print(',');
        csv.print(x);          csv.print(',');
        csv.println(frame[idx], 2);
      }
    }
    csv.close();
  }

  // 3) Generate a heatmap image
  heatmap.writePPM(frame, "heatmap.ppm");

  Serial.printf("Frame %u done\n", frameCount++);
  delay(2000);
}

