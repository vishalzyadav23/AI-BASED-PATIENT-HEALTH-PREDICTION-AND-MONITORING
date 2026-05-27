# Time-Series Trend Analysis & Sepsis Risk API Documentation

Complete API reference for trend analysis, sepsis risk assessment, and mobile notifications.

---

## TIME-SERIES TREND ANALYSIS

Advanced trend analysis with ARIMA forecasting for 24h, 7d, and 30d periods.

### Endpoint 1: Get Multi-Vital Trends

**Request:**

```http
GET /api/trends/{patient_id}/{hours}
Authorization: Bearer {jwt_token}
```

**Parameters:**

- `patient_id` (integer) - Patient ID
- `hours` (integer) - Lookback period: 24, 168 (7d), or 720 (30d)

**Example:**

```bash
# Get 24-hour trends
curl -X GET "http://localhost:8000/api/trends/1/24" \
  -H "Authorization: Bearer eyJhbGciOi..."

# Get 7-day trends
curl -X GET "http://localhost:8000/api/trends/1/168" \
  -H "Authorization: Bearer eyJhbGciOi..."

# Get 30-day trends
curl -X GET "http://localhost:8000/api/trends/1/720" \
  -H "Authorization: Bearer eyJhbGciOi..."
```

**Response:**

```json
{
  "period_hours": 24,
  "analysis_timestamp": "2024-05-25T14:30:00",
  "overall_status": "STABLE",
  "vital_trends": {
    "heart_rate": {
      "vital": "heart_rate",
      "period_hours": 24,
      "data_points": 24,
      "mean": 75.5,
      "std_dev": 8.2,
      "min": 62,
      "max": 95,
      "slope": 0.15,
      "trend": "STABLE",
      "trend_severity": "LOW",
      "volatility": 0.109,
      "volatility_level": "MODERATE",
      "rate_of_change_percent": 5.3,
      "forecast_next_6": [76.2, 76.9, 77.5, 78.1, 78.7, 79.3],
      "forecast_upper_bound": [85.4, 86.1, 86.7, 87.3, 87.9, 88.5],
      "forecast_lower_bound": [67.0, 67.7, 68.3, 68.9, 69.5, 70.1],
      "forecast_confidence": 0.95,
      "clinical_alert": {
        "type": "NORMAL",
        "severity": "INFO",
        "message": "Trend within expected parameters"
      }
    },
    "spo2": {
      "vital": "spo2",
      "period_hours": 24,
      "data_points": 24,
      "mean": 97.2,
      "std_dev": 1.5,
      "min": 94,
      "max": 99,
      "slope": -0.05,
      "trend": "STABLE",
      "trend_severity": "LOW",
      "volatility": 0.015,
      "volatility_level": "LOW",
      "rate_of_change_percent": -0.3,
      "forecast_next_6": [97.1, 97.0, 96.9, 96.8, 96.7, 96.6],
      "forecast_upper_bound": [99.0, 98.9, 98.8, 98.7, 98.6, 98.5],
      "forecast_lower_bound": [95.2, 95.1, 95.0, 94.9, 94.8, 94.7],
      "forecast_confidence": 0.95,
      "clinical_alert": {
        "type": "NORMAL",
        "severity": "INFO",
        "message": "Oxygen saturation stable"
      }
    },
    "temperature": {
      "vital": "temperature",
      "period_hours": 24,
      "data_points": 24,
      "mean": 37.1,
      "std_dev": 0.4,
      "min": 36.5,
      "max": 38.2,
      "slope": 0.08,
      "trend": "INCREASING",
      "trend_severity": "MODERATE",
      "volatility": 0.011,
      "volatility_level": "LOW",
      "rate_of_change_percent": 3.2,
      "forecast_next_6": [37.25, 37.35, 37.45, 37.55, 37.65, 37.75],
      "forecast_upper_bound": [38.5, 38.6, 38.7, 38.8, 38.9, 39.0],
      "forecast_lower_bound": [36.0, 36.1, 36.2, 36.3, 36.4, 36.5],
      "forecast_confidence": 0.95,
      "clinical_alert": [
        {
          "type": "FORECAST_EXCEED_UPPER",
          "severity": "WARNING",
          "message": "Forecast predicts temperature will exceed upper limit (>38.5°C)"
        }
      ]
    }
  }
}
```

### Endpoint 2: Get Single Vital Trend

**Request:**

```http
GET /api/trends/vital/{patient_id}/{vital_name}/{hours}
Authorization: Bearer {jwt_token}
```

**Parameters:**

- `patient_id` (integer)
- `vital_name` (string) - One of: heart_rate, spo2, temperature, systolic_bp, diastolic_bp, respiratory_rate
- `hours` (integer) - 24, 168, or 720

**Example:**

```bash
curl -X GET "http://localhost:8000/api/trends/vital/1/heart_rate/24" \
  -H "Authorization: Bearer eyJhbGciOi..."
```

**Response:** Same format as `vital_trends[vital_name]` from above

### Trend Analysis Components

#### 1. Descriptive Statistics

- **mean** - Average vital sign value
- **std_dev** - Standard deviation (variability)
- **min/max** - Range of values
- **rate_of_change_percent** - Change from oldest to newest reading

#### 2. Trend Detection

- **slope** - Linear regression slope (units/hour)
- **trend** - INCREASING, DECREASING, or STABLE
- **trend_severity** - HIGH or MODERATE (if non-stable)

#### 3. Volatility Analysis

- **volatility** - Coefficient of variation (0-1 scale)
- **volatility_level** - LOW, MODERATE, or HIGH
  - LOW: < 0.08
  - MODERATE: 0.08 - 0.15
  - HIGH: > 0.15

#### 4. ARIMA Forecasting

- **forecast_next_6** - Predictions for next 6 time periods
- **forecast_upper_bound** - 95% confidence interval upper
- **forecast_lower_bound** - 95% confidence interval lower
- **forecast_confidence** - Confidence level (0.95 = 95%)

#### 5. Clinical Alerts

Automatic alerts based on trend analysis:

| Alert Type            | Trigger                          | Severity |
| --------------------- | -------------------------------- | -------- |
| RAPID_INCREASE        | Trend=INCREASING + HIGH severity | WARNING  |
| RAPID_DECREASE        | Trend=DECREASING + HIGH severity | WARNING  |
| HIGH_VOLATILITY       | Volatility > 0.15                | CAUTION  |
| FORECAST_EXCEED_UPPER | Predicted value > normal max     | WARNING  |
| FORECAST_EXCEED_LOWER | Predicted value < normal min     | WARNING  |

### Usage Examples

**Python:**

```python
import requests

headers = {"Authorization": f"Bearer {jwt_token}"}

# Get 24-hour trends
response = requests.get(
    "http://localhost:8000/api/trends/1/24",
    headers=headers
)
trends = response.json()

# Check overall status
if trends["overall_status"] == "CRITICAL":
    print("⚠️ CRITICAL CONDITIONS DETECTED")

# Analyze individual vital
hr_trend = trends["vital_trends"]["heart_rate"]
if hr_trend["clinical_alert"]["severity"] == "WARNING":
    print(f"Heart Rate Alert: {hr_trend['clinical_alert']['message']}")
```

**JavaScript/Node.js:**

```javascript
const axios = require("axios");

const headers = { Authorization: `Bearer ${jwtToken}` };

// Get 7-day trends
const response = await axios.get("http://localhost:8000/api/trends/1/168", {
  headers,
});

const trends = response.data;
const tempTrend = trends.vital_trends.temperature;

console.log(`Temperature trend: ${tempTrend.trend}`);
console.log(`Forecast: ${tempTrend.forecast_next_6.join(", ")}`);
```

---

## SEPSIS RISK ASSESSMENT

### Endpoint 1: Assess Sepsis Risk

**Request:**

```http
POST /api/sepsis/assess
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "patient_id": 1,
  "vitals": {
    "heart_rate": 110,
    "respiratory_rate": 24,
    "systolic_bp": 95,
    "diastolic_bp": 60,
    "temperature": 38.8,
    "spo2": 92,
    "gcs": 15,
    "lactate": 2.5,
    "platelets": 180,
    "bilirubin": 0.9,
    "creatinine": 1.1,
    "urine_output": 0.8
  }
}
```

**Response:**

```json
{
  "sepsis_probability_percent": 62.5,
  "risk_level": "HIGH",
  "indicators": [
    {
      "indicator": "qSOFA Score",
      "value": 2,
      "weight": 25,
      "contribution": 16.67,
      "risk": "HIGH RISK - Possible sepsis, immediate evaluation recommended"
    },
    {
      "indicator": "Temperature",
      "value": 38.8,
      "status": "ABNORMAL",
      "weight": 20
    },
    {
      "indicator": "Heart Rate (Tachycardia)",
      "value": 110,
      "status": "TACHYCARDIC",
      "weight": 15
    },
    {
      "indicator": "Respiratory Rate (Tachypnea)",
      "value": 24,
      "status": "TACHYPNEIC",
      "weight": 15
    },
    {
      "indicator": "Oxygen Saturation (SpO2)",
      "value": 92,
      "status": "HYPOXEMIA",
      "weight": 15
    },
    {
      "indicator": "Lactate Level",
      "value": 2.5,
      "status": "BORDERLINE",
      "weight": 10
    }
  ],
  "sofa_score": 5,
  "qsofa_score": 2,
  "clinical_recommendation": "HIGH PRIORITY: Evaluate for sepsis. Consider blood cultures and lactate measurement. Close monitoring required."
}
```

### Risk Levels

| Risk Level | Probability | Action               |
| ---------- | ----------- | -------------------- |
| LOW        | 0-15%       | Routine monitoring   |
| MILD       | 15-30%      | Enhanced monitoring  |
| MODERATE   | 30-50%      | Close observation    |
| HIGH       | 50-70%      | Immediate evaluation |
| CRITICAL   | 70%+        | Urgent intervention  |

### SOFA Score Components

| Component          | Score | Criteria               |
| ------------------ | ----- | ---------------------- |
| **Respiratory**    | 0     | SpO2 >= 95%            |
|                    | 1     | SpO2 90-94%            |
|                    | 2     | SpO2 80-89%            |
|                    | 3     | SpO2 75-79%            |
|                    | 4     | SpO2 < 75%             |
| **Coagulation**    | 0     | Platelets >= 150       |
|                    | 1     | Platelets 100-149      |
|                    | 2     | Platelets 50-99        |
|                    | 3     | Platelets 20-49        |
|                    | 4     | Platelets < 20         |
| **Hepatic**        | 0     | Bilirubin < 1.2        |
|                    | 1     | Bilirubin 1.2-1.9      |
|                    | 2     | Bilirubin 2.0-5.9      |
|                    | 3     | Bilirubin 6.0-11.9     |
|                    | 4     | Bilirubin >= 12.0      |
| **Cardiovascular** | 0     | MAP >= 90              |
|                    | 1     | MAP 80-89              |
|                    | 2     | MAP 70-79              |
|                    | 3     | MAP < 70               |
|                    | 4     | MAP < 70 + vasopressor |
| **CNS**            | 0     | GCS = 15               |
|                    | 1     | GCS 13-14              |
|                    | 2     | GCS 10-12              |
|                    | 3     | GCS 6-9                |
|                    | 4     | GCS < 6                |
| **Renal**          | 0     | Creatinine < 1.2       |
|                    | 1     | Creatinine 1.2-1.9     |
|                    | 2     | Creatinine 2.0-3.4     |
|                    | 3     | Creatinine 3.5-4.9     |
|                    | 4     | Creatinine >= 5.0      |

### qSOFA Score Criteria

1. **Altered Mental Status** - GCS < 15
2. **Hypotension** - Systolic BP <= 100 mmHg
3. **Tachypnea** - Respiratory Rate >= 22/min

Score >= 2 indicates increased mortality risk.

### Endpoint 2: Get Sepsis Assessment History

**Request:**

```http
GET /api/sepsis/history/{patient_id}?days=7
Authorization: Bearer {jwt_token}
```

**Parameters:**

- `patient_id` (integer)
- `days` (integer, optional) - Lookback period, default 7

**Response:**

```json
[
  {
    "sepsis_probability_percent": 62.5,
    "risk_level": "HIGH",
    "indicators": [...],
    "sofa_score": 5,
    "qsofa_score": 2,
    "clinical_recommendation": "..."
  },
  {
    "sepsis_probability_percent": 48.2,
    "risk_level": "MODERATE",
    "indicators": [...],
    "sofa_score": 3,
    "qsofa_score": 1,
    "clinical_recommendation": "..."
  }
]
```

### Sepsis Protocol Integration

Recommended clinical actions based on assessment:

```
Risk Level: CRITICAL or HIGH
├─ ✓ Blood cultures (before antibiotics)
├─ ✓ Lactate measurement
├─ ✓ IV fluid resuscitation (30 mL/kg)
├─ ✓ Broad-spectrum antibiotics (within 1 hour)
├─ ✓ Vasopressor support if hypotensive
├─ ✓ Source control
├─ ✓ Escalate to physician
└─ ✓ Consider ICU admission

Risk Level: MODERATE
├─ ✓ Enhanced monitoring
├─ ✓ Blood cultures if fever present
├─ ✓ Watch for deterioration
└─ ✓ Prepare for escalation

Risk Level: LOW/MILD
├─ ✓ Routine monitoring
├─ ✓ Re-assess in 2-4 hours
└─ ✓ Document findings
```

---

## FIREBASE MOBILE NOTIFICATIONS

### Endpoint 1: Register Device

**Request:**

```http
POST /api/notifications/register-device
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "device_token": "f8wCl3-xYsY:APA91bF1JzAh...",
  "device_type": "iOS",
  "device_model": "iPhone 14 Pro"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Device token registered for iOS",
  "device_id": 42
}
```

### Endpoint 2: Deregister Device

**Request:**

```http
DELETE /api/notifications/deregister-device/{device_token}
Authorization: Bearer {jwt_token}
```

**Response:**

```json
{
  "status": "success",
  "message": "Device token deregistered"
}
```

### Endpoint 3: Get Patient Devices

**Request:**

```http
GET /api/notifications/devices/{patient_id}
Authorization: Bearer {jwt_token}
```

**Response:**

```json
{
  "patient_id": 1,
  "device_count": 2,
  "devices": [
    {
      "id": 1,
      "device_type": "iOS",
      "device_model": "iPhone 14",
      "registered_at": "2024-05-20T10:30:00",
      "last_used": "2024-05-25T14:15:00"
    },
    {
      "id": 2,
      "device_type": "Android",
      "device_model": "Samsung Galaxy S23",
      "registered_at": "2024-05-22T08:00:00",
      "last_used": "2024-05-25T13:45:00"
    }
  ]
}
```

### Endpoint 4: Send Test Notification

**Request:**

```http
POST /api/notifications/test/{patient_id}
Authorization: Bearer {jwt_token}
```

**Response:**

```json
{
  "status": "success",
  "sent_count": 2,
  "failed_count": 0,
  "message": "Notification sent to 2 devices"
}
```

### Endpoint 5: Get Notification History

**Request:**

```http
GET /api/notifications/history/{patient_id}?limit=50
Authorization: Bearer {jwt_token}
```

**Response:**

```json
[
  {
    "id": 156,
    "patient_id": 1,
    "notification_type": "CRITICAL_ALERT",
    "title": "🚨 CRITICAL ALERT - Patient 1",
    "message": "SpO2 dropped to 88% - immediate action needed",
    "send_status": "SENT",
    "sent_to_devices": 2,
    "created_at": "2024-05-25T14:32:10",
    "sent_at": "2024-05-25T14:32:12"
  },
  {
    "id": 155,
    "patient_id": 1,
    "notification_type": "SEPSIS_WARNING",
    "title": "⚠️ Sepsis Risk Detected",
    "message": "Sepsis probability: 65% - Recommend immediate evaluation",
    "send_status": "SENT",
    "sent_to_devices": 2,
    "created_at": "2024-05-25T14:25:00",
    "sent_at": "2024-05-25T14:25:02"
  }
]
```

### Automatic Notification Triggers

Notifications are automatically sent when:

1. **CRITICAL ALERT** - Patient enters CRITICAL health state
   - Severity: High
   - Sound: Alert tone
   - Immediate action required

2. **ANOMALY ALERT** - Anomaly detected in vital signs
   - Severity: Medium
   - Sound: Notification tone
   - Investigate cause

3. **SEPSIS WARNING** - High sepsis probability detected (>50%)
   - Severity: Critical
   - Sound: Alert tone
   - Initiate sepsis protocol

4. **UNREVIEWED ALERTS** - Staff alerts awaiting review
   - Severity: Normal
   - Sound: Notification tone
   - Periodic reminders

### Notification Payload Format

```json
{
  "title": "🚨 CRITICAL ALERT - Patient 1",
  "body": "Heart rate 145 bpm - severe tachycardia",
  "data": {
    "patient_id": "1",
    "alert_level": "CRITICAL",
    "vital": "heart_rate",
    "value": "145",
    "normal_range": "60-100",
    "timestamp": "2024-05-25T14:32:10",
    "action": "open_patient_details"
  },
  "android": {
    "priority": "high",
    "notification": {
      "sound": "default",
      "click_action": "CRITICAL_ALERT"
    }
  }
}
```

---

## Error Handling

All endpoints return standard error responses:

```json
{
  "detail": "No active devices for this patient"
}
```

HTTP Status Codes:

- `200` - Success
- `400` - Invalid request
- `401` - Unauthorized (missing/invalid token)
- `404` - Resource not found
- `500` - Server error

---

## Rate Limiting & Best Practices

1. **Avoid notification spam** - Maximum 1 notification per minute per vital
2. **Batch alerts** - Combine multiple issues into single notification
3. **Test first** - Use `/api/notifications/test/{patient_id}` before production
4. **Monitor delivery** - Check history endpoint for success rates
5. **Device rotation** - Refresh tokens if not used for 30+ days

---

## Integration Examples

### Python (Requests)

```python
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"
HEADERS = {"Authorization": f"Bearer {jwt_token}"}

# Get trends
trends = requests.get(
    f"{BASE_URL}/api/trends/1/24",
    headers=HEADERS
).json()

# Assess sepsis risk
sepsis = requests.post(
    f"{BASE_URL}/api/sepsis/assess",
    headers=HEADERS,
    json={"patient_id": 1, "vitals": {...}}
).json()

# Register device for notifications
device = requests.post(
    f"{BASE_URL}/api/notifications/register-device",
    headers=HEADERS,
    json={
        "device_token": "FCM_TOKEN",
        "device_type": "iOS"
    }
).json()
```

### JavaScript/Fetch

```javascript
const BASE_URL = "http://localhost:8000";
const headers = { Authorization: `Bearer ${jwtToken}` };

// Get trends
const trends = await fetch(`${BASE_URL}/api/trends/1/24`, { headers }).then(
  (r) => r.json(),
);

// Register device
const device = await fetch(`${BASE_URL}/api/notifications/register-device`, {
  method: "POST",
  headers: { ...headers, "Content-Type": "application/json" },
  body: JSON.stringify({
    device_token: fcmToken,
    device_type: "iOS",
  }),
}).then((r) => r.json());
```

---

## Database Schema

### DeviceToken Table

```sql
CREATE TABLE device_tokens (
  id INTEGER PRIMARY KEY,
  patient_id INTEGER NOT NULL,
  device_token VARCHAR UNIQUE NOT NULL,
  device_type VARCHAR NOT NULL,
  device_model VARCHAR,
  is_active INTEGER DEFAULT 1,
  registered_at DATETIME DEFAULT now(),
  last_used DATETIME,
  deregistered_at DATETIME
);
```

### NotificationLog Table

```sql
CREATE TABLE notification_logs (
  id INTEGER PRIMARY KEY,
  patient_id INTEGER NOT NULL,
  notification_type VARCHAR NOT NULL,
  title VARCHAR NOT NULL,
  message TEXT NOT NULL,
  send_status VARCHAR NOT NULL,
  sent_to_devices INTEGER,
  failed_devices INTEGER,
  created_at DATETIME DEFAULT now(),
  sent_at DATETIME
);
```

### SepsisRiskLog Table

```sql
CREATE TABLE sepsis_risk_logs (
  id INTEGER PRIMARY KEY,
  patient_id INTEGER NOT NULL,
  qsofa_score INTEGER NOT NULL,
  sofa_score INTEGER NOT NULL,
  sepsis_probability FLOAT NOT NULL,
  risk_level VARCHAR NOT NULL,
  clinical_recommendation TEXT NOT NULL,
  created_at DATETIME DEFAULT now(),
  assessment_time DATETIME NOT NULL
);
```
