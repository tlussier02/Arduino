#include <Wire.h>
#include <Adafruit_MLX90640.h>

#define FRAME_WIDTH   32
#define FRAME_HEIGHT  24
#define MLX_I2C_ADDR  0x33

Adafruit_MLX90640 mlx;
float frame[FRAME_WIDTH * FRAME_HEIGHT];

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  Wire.begin();
  Wire.setClock(400000);              // I2C @400 kHz

  if (!mlx.begin(MLX_I2C_ADDR)) {
    Serial.println("ERROR: MLX90640 not found!");
    while (1) delay(10);
  }
  Serial.println("frame,row,col,temp_C");
}

void loop() {
  static uint32_t frameCount = 0;

  if (mlx.getFrame(frame) != 0) {
    Serial.println("ERROR: reading MLX90640");
    delay(100);
    return;
  }

  // print out every pixel as CSV
  for (int y = 0; y < FRAME_HEIGHT; y++) {
    for (int x = 0; x < FRAME_WIDTH; x++) {
      int idx = y * FRAME_WIDTH + x;
      Serial.print(frameCount);
      Serial.print(',');
      Serial.print(y);
      Serial.print(',');
      Serial.print(x);
      Serial.print(',');
      Serial.println(frame[idx], 2);
    }
  }

  frameCount++;
  delay(200);  // ~5 Hz
}
