#include <Wire.h>
#include <MPU6050.h>
#include <WiFiNINA.h>
#include <ArduinoHttpClient.h>
#include <TinyGPSPlus.h>

MPU6050 mpu;
TinyGPSPlus gps;

char ssid[] = "김강민의 iPhone";
char pass[] = "kangminkim82";

char serverAddress[] = "43.201.25.240";
int port = 5000;

WiFiClient wifi;
HttpClient client = HttpClient(wifi, serverAddress, port);

#define GPS_RX 1
#define GPS_TX 0

// WiFi 연결 함수
void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.print(" WiFi 연결 시도 중...");
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    Serial.print(".");
    digitalWrite(LED_BUILTIN, HIGH); // 연결 실패 시 LED ON
    delay(1000);
  }

  digitalWrite(LED_BUILTIN, LOW); // 연결 성공 시 LED OFF
  Serial.println("\n WiFi 연결 완료");
  Serial.print(" IP 주소: ");
  Serial.println(WiFi.localIP());
}

// 센서 초기화 및 WiFi 연결
void setup() {
  delay(3000);  // 전원 안정화를 위한 지연

  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);

  Serial.println(" 시스템 시작 중");

  Wire.begin();
  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println(" MPU6050 연결 실패 프로그램 중단.");
    while (1);
  }
  Serial.println(" MPU6050 연결 성공");

  Serial1.begin(9600);
  Serial.println(" GPS 모듈 시리얼 시작됨");

  connectWiFi();
}

void loop() {
  connectWiFi();

  // 가속도 센서 값 읽기 및 충격량 계산
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);

  float x = ax / 16384.0;
  float y = ay / 16384.0;
  float z = az / 16384.0;
  float impact = sqrt(x * x + y * y + z * z);

  Serial.println(" 가속도 측정값:");
  Serial.print("  x: "); Serial.print(x, 3);
  Serial.print("  y: "); Serial.print(y, 3);
  Serial.print("  z: "); Serial.print(z, 3);
  Serial.print("  => 충격량: "); Serial.println(impact, 3);

  // GPS 데이터 수신 및 위치 유효성 확인
  while (Serial1.available() > 0) {
    gps.encode(Serial1.read());
  }

  double latitude = 0.0;
  double longitude = 0.0;

  if (gps.location.isValid()) {
    latitude = gps.location.lat();
    longitude = gps.location.lng();
    Serial.print(" GPS 수신됨: ");
    Serial.print("위도: "); Serial.print(latitude, 6);
    Serial.print(" / 경도: "); Serial.println(longitude, 6);
  } else {
    Serial.println(" GPS 위치 수신 중... (위치 유효하지 않음)");
  }

  // JSON 데이터 생성 및 서버로 전송
  String json = "{\"accel_x\": " + String(x, 3) +
                ", \"accel_y\": " + String(y, 3) +
                ", \"accel_z\": " + String(z, 3) +
                ", \"impact\": " + String(impact, 3) +
                ", \"latitude\": " + String(latitude, 6) +
                ", \"longitude\": " + String(longitude, 6) +
                "}";

  Serial.println(" 전송할 JSON 데이터:");
  Serial.println(json);

  client.beginRequest();
  client.post("/receive");
  client.sendHeader("Content-Type", "application/json");
  client.sendHeader("Content-Length", json.length());
  client.write((const uint8_t*)json.c_str(), json.length());
  client.endRequest();

  Serial.println(" 전송 완료");
  Serial.println("------------------------------------------------------\n");

  delay(1000);
}
