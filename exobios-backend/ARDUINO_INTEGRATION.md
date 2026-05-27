# Arduino Integration Guide - Real-time Sensor Data

## Updated Arduino Code Integration

The Arduino needs to be modified to use the new `/api/telemetry/stream` endpoint instead of the old simple endpoint.

### Key Changes

#### 1. Update Server URL

```cpp
const char* serverName = "http://172.20.10.3:8000/api/telemetry/stream";
```

#### 2. Update JSON Payload

Instead of:

```cpp
{
  "bpm": value,
  "spo2": value,
  "temperature": value
}
```

Send:

```cpp
{
  "patient_id": 1,
  "heart_rate": value,
  "spo2": value,
  "temperature": value,
  "systolic_bp": value,
  "diastolic_bp": value,
  "respiratory_rate": value
}
```

### Modified Arduino Telemetry Function

```cpp
void sendTelemetry() {
  if ((WiFi.status() == WL_CONNECTED) && (millis() - tsLastReport > REPORTING_PERIOD_MS)) {

    HTTPClient http;

    // Create JSON payload with new field names
    String payload = "";
    payload += "{\"patient_id\": 1, ";
    payload += "\"heart_rate\": " + String(BPM) + ", ";
    payload += "\"spo2\": " + String(SpO2) + ", ";
    payload += "\"temperature\": " + String(bodytemperature) + "}";

    Serial.print("[HTTP] Sending to: ");
    Serial.println(serverName);
    Serial.println("Payload: " + payload);

    http.begin(client, serverName);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("[HTTP] Status: " + String(httpResponseCode));
      Serial.println("[HTTP] Response: " + response);

      // Parse response to check for alerts
      if (response.indexOf("CRITICAL") > 0) {
        // Trigger visual/audio alert on device
        triggerAlert();
      }
    } else {
      Serial.println("[HTTP] Error: " + String(httpResponseCode));
    }

    http.end();
    tsLastReport = millis();
  }
}

void triggerAlert() {
  // Sound buzzer or flash LED
  digitalWrite(BUZZER_PIN, HIGH);
  delay(500);
  digitalWrite(BUZZER_PIN, LOW);
  delay(100);
  digitalWrite(BUZZER_PIN, HIGH);
  delay(500);
  digitalWrite(BUZZER_PIN, LOW);
}
```

### Optional: Add Blood Pressure Sensor

If using a blood pressure sensor module (e.g., I2C digital sensor):

```cpp
#include <Wire.h>

// If using BMP module (example)
#define BMP_ADDRESS 0x77

int readBMP() {
  // Example: Read from BMP sensor
  Wire.beginTransmission(BMP_ADDRESS);
  Wire.write(0xF7);  // Pressure register
  Wire.endTransmission();

  Wire.requestFrom(BMP_ADDRESS, 3);
  int pressure = 0;
  while(Wire.available()) {
    pressure = (pressure << 8) | Wire.read();
  }

  // Convert to mmHg (example conversion)
  return pressure / 133;  // Pa to mmHg
}
```

### Complete Modified ESP8266 Code Snippet

```cpp
// ESP8266 Updated Telemetry Pipeline
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <Wire.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "DHT.h"
#include "MAX30105.h"
#include "heartRate.h"

#define DHTTYPE DHT22
#define DHTPIN 14
#define DS18B20 2
#define REPORTING_PERIOD_MS 1000
#define PATIENT_ID 1

const char* ssid = "iPhone";
const char* password = "12345678";
const char* serverName = "http://172.20.10.3:8000/api/telemetry/stream";

float temperature, humidity, bodytemperature;
int BPM, SpO2, systolicBP = 0, diastolicBP = 0;

DHT dht(DHTPIN, DHTTYPE);
OneWire oneWire(DS18B20);
DallasTemperature sensors(&oneWire);
MAX30105 particleSensor;

uint32_t tsLastReport = 0;
WiFiClient client;

void setup() {
  Serial.begin(115200);
  delay(100);

  dht.begin();
  sensors.begin();

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected");
    Serial.println(WiFi.localIP());
  }

  // Initialize sensors
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30105 not found");
  }

  particleSensor.setup();
}

void loop() {
  readSensors();

  if ((WiFi.status() == WL_CONNECTED) && (millis() - tsLastReport > REPORTING_PERIOD_MS)) {
    sendTelemetry();
  }

  delay(100);
}

void readSensors() {
  // Read DHT22
  humidity = dht.readHumidity();
  temperature = dht.readTemperature();

  // Read DS18B20
  sensors.requestTemperatures();
  bodytemperature = sensors.getTempCByIndex(0);

  // Read MAX30105
  if (particleSensor.available()) {
    int irValue = particleSensor.getIR();

    if (irValue < 50000) {
      Serial.println("No finger detected");
      BPM = 0;
      SpO2 = 0;
    } else {
      // Simplified BPM calculation
      if (checkForBeat(irValue)) {
        long delta = millis() - lastBeat;
        lastBeat = millis();

        beatsPerMinute = 60 / (delta / 1000.0);

        if (beatsPerMinute < 255 && beatsPerMinute > 20) {
          rates[rateSpot++] = (byte)beatsPerMinute;
          rateSpot %= RATE_SIZE;

          beatAvg = 0;
          for (byte x = 0 ; x < RATE_SIZE ; x++)
            beatAvg += rates[x];
          beatAvg /= RATE_SIZE;
        }
      }

      BPM = beatAvg;
      SpO2 = calculateSpO2(irValue);
    }

    particleSensor.nextSample();
  }
}

void sendTelemetry() {
  HTTPClient http;

  String payload = "{";
  payload += "\"patient_id\": " + String(PATIENT_ID) + ", ";
  payload += "\"heart_rate\": " + String(BPM) + ", ";
  payload += "\"spo2\": " + String(SpO2) + ", ";
  payload += "\"temperature\": " + String(bodytemperature) + ", ";
  payload += "\"systolic_bp\": " + String(systolicBP) + ", ";
  payload += "\"diastolic_bp\": " + String(diastolicBP) + ", ";
  payload += "\"respiratory_rate\": 16";
  payload += "}";

  Serial.println("[HTTP] Sending: " + payload);

  http.begin(client, serverName);
  http.addHeader("Content-Type", "application/json");

  int httpResponseCode = http.POST(payload);

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("[HTTP] Response Code: " + String(httpResponseCode));

    // Check for critical alerts
    if (response.indexOf("\"level\": \"CRITICAL\"") > 0) {
      triggerCriticalAlert();
    }
    // Check for warnings
    else if (response.indexOf("\"level\": \"WARNING\"") > 0) {
      triggerWarningAlert();
    }
  } else {
    Serial.println("[HTTP] Error: " + String(httpResponseCode));
  }

  http.end();
  tsLastReport = millis();
}

void triggerCriticalAlert() {
  // Flash LED rapidly + continuous beep
  for (int i = 0; i < 5; i++) {
    digitalWrite(LED_BUILTIN, LOW);
    digitalWrite(BUZZER_PIN, HIGH);
    delay(200);
    digitalWrite(LED_BUILTIN, HIGH);
    digitalWrite(BUZZER_PIN, LOW);
    delay(200);
  }
}

void triggerWarningAlert() {
  // Single beep + LED blink
  digitalWrite(LED_BUILTIN, LOW);
  digitalWrite(BUZZER_PIN, HIGH);
  delay(300);
  digitalWrite(LED_BUILTIN, HIGH);
  digitalWrite(BUZZER_PIN, LOW);
}

int calculateSpO2(int irValue) {
  // Simplified SpO2 calculation
  // Real implementation would use AC/DC ratios
  if (irValue < 50000) return 0;
  if (irValue > 100000) return 99;
  return 95 + ((irValue - 50000) / 50000) * 4;  // Map to 95-99
}
```

### Key API Response Handling

The Arduino can now parse the response to handle alerts:

```cpp
void parseResponse(String response) {
  // Parse JSON response
  int alertStartIdx = response.indexOf("\"alerts\"");

  if (alertStartIdx > 0) {
    // Extract alert level
    int levelIdx = response.indexOf("\"level\"", alertStartIdx);
    int levelQuote = response.indexOf("\"", levelIdx + 8);
    int levelEnd = response.indexOf("\"", levelQuote + 1);

    String level = response.substring(levelQuote + 1, levelEnd);

    if (level == "CRITICAL") {
      triggerCriticalAlert();
      Serial.println("CRITICAL ALERT!");
    } else if (level == "WARNING") {
      triggerWarningAlert();
      Serial.println("WARNING ALERT!");
    }
  }
}
```

### Troubleshooting

**Issue**: Getting 422 Unprocessable Entity

- **Solution**: Check JSON field names match exactly (patient_id, heart_rate, spo2, temperature)

**Issue**: Connection timeout

- **Solution**: Verify server URL is correct and accessible from network

**Issue**: Getting validation errors

- **Solution**: Ensure vital signs are within valid ranges:
  - HR: 30-200 BPM
  - SpO2: 50-100%
  - Temperature: 30-42°C

**Issue**: No alerts generated

- **Solution**: Check that vital signs are actually out of normal range (not just valid range)

### Performance Tips

1. **Reduce Report Frequency**: Change `REPORTING_PERIOD_MS` to 2000-5000ms for lighter load
2. **Batch Multiple Readings**: Accumulate 5-10 readings before sending
3. **Local Validation**: Validate on device before sending to server
4. **Handle Network Failures**: Implement retry logic with exponential backoff

### Future Enhancements

1. Add optional fields like blood pressure when available
2. Implement local alert thresholds on device
3. Store readings locally if no network
4. Add battery level monitoring
5. Support for multiple sensors with unique IDs
