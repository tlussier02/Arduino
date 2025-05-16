#include <Adafruit_MLX90640.h>
#define MLX90640_I2C_ADDRESS 0x33 // Default I2C address for MLX90640
Adafruit_MLX90640 mlx;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  if (!mlx.begin(MLX90640_I2C_ADDRESS)) {
    Serial.println(F("ERROR: MLX90640 not found!"));
    while (1) yield();
  }
  Serial.println(F("MLX90640 ready"));
}

void loop() {
  float frame[32*24];
  if (mlx.getFrame(frame) != 0) {
    Serial.println(F("Frame error"));
    return;
  }

  static uint32_t frameID = 0;
  for (uint16_t i = 0; i < 32*24; i++) {
    uint8_t row = i / 32;
    uint8_t col = i % 32;
    // apply skin emissivity correction manually if desired:
    float tempC = frame[i] * 0.98;
    Serial.print(frameID); Serial.print(',');
    Serial.print(row);     Serial.print(',');
    Serial.print(col);     Serial.print(',');
    Serial.println(tempC);
  }
  frameID++;
}
