# Real-time Sensor Data Processing - API Documentation

## Overview

The Real-time Sensor Data Processing module provides comprehensive validation, anomaly detection, and alert management for IoT medical sensors. It processes vital sign data in real-time, validates readings, detects anomalies, and generates actionable alerts for paramedics.

---

## Features

### 1. **Data Validation**

- Validates incoming sensor readings against physically possible ranges
- Checks for required fields and data types
- Returns detailed error messages for invalid data

**Valid Ranges:**

- Heart Rate: 30-200 BPM
- SpO2: 50-100%
- Temperature: 30-42°C
- Systolic BP: 60-200 mmHg
- Diastolic BP: 30-120 mmHg
- Respiratory Rate: 5-40 breaths/min

### 2. **Real-time Anomaly Detection**

Uses multiple statistical methods:

- **Rapid Change Detection**: Identifies abrupt changes in vital signs
- **Z-Score Analysis**: Detects statistical outliers
- **Trend Analysis**: Monitors patterns over time
- **Flatline Detection**: Alerts on sensor disconnection

### 3. **Intelligent Alert System**

- **Three Alert Levels**: INFO, WARNING, CRITICAL
- **Severity Scoring**: 0.0-1.0 severity calculation
- **Anomaly Classification**: out_of_range, rapid_change, flatline, spike
- **Alert Acknowledgment**: Track which alerts have been reviewed

### 4. **Persistent Storage**

- All readings stored in database for historical analysis
- Automatic alert storage linked to readings
- Alert acknowledgment tracking with timestamp and personnel ID

### 5. **Real-time Monitoring**

- In-memory history of recent readings
- Quick access to current patient status
- Real-time statistics calculation
- Alert aggregation and prioritization

---

## API Endpoints

### 1. **Stream Telemetry Data**

```
POST /api/telemetry/stream
```

**Purpose**: Process real-time sensor data with validation and anomaly detection.

**Request Body:**

```json
{
  "patient_id": 1,
  "heart_rate": 88,
  "spo2": 97,
  "temperature": 37.2,
  "systolic_bp": 145,
  "diastolic_bp": 92,
  "respiratory_rate": 16
}
```

**Response:**

```json
{
  "status": "processed",
  "timestamp": "2024-05-24T10:30:45.123456",
  "valid": true,
  "errors": [],
  "warnings": [],
  "alerts": [
    {
      "level": "WARNING",
      "message": "HIGH: systolic_bp is 145 (normal: 90-120)",
      "vital": "systolic_bp",
      "value": 145,
      "range": [90, 120]
    }
  ],
  "processed_data": {
    "heart_rate": 88,
    "spo2": 97,
    "temperature": 37.2,
    "systolic_bp": 145,
    "diastolic_bp": 92,
    "respiratory_rate": 16,
    "timestamp": "2024-05-24T10:30:45.123456"
  }
}
```

**Alert Examples:**

**High Blood Pressure:**

```json
{
  "level": "WARNING",
  "message": "HIGH: systolic_bp is 145 (normal: 90-120)",
  "vital": "systolic_bp",
  "value": 145,
  "range": [90, 120]
}
```

**Rapid Heart Rate Change:**

```json
{
  "level": "WARNING",
  "message": "ANOMALY: heart_rate - rapid_change (severity: 0.65)",
  "vital": "heart_rate",
  "value": 125,
  "range": [0, 0]
}
```

**Critical Low Oxygen:**

```json
{
  "level": "CRITICAL",
  "message": "LOW: spo2 is 88 (normal: 95-100)",
  "vital": "spo2",
  "value": 88,
  "range": [95, 100]
}
```

---

### 2. **Get Current Telemetry**

```
GET /api/telemetry/current
```

**Response:**

```json
{
  "timestamp": "2024-05-24T10:30:45.123456",
  "heart_rate": 88,
  "spo2": 97,
  "temperature": 37.2,
  "systolic_bp": 145,
  "diastolic_bp": 92,
  "respiratory_rate": 16
}
```

---

### 3. **Get Sensor History**

```
GET /api/sensor/history/{patient_id}?limit=100
```

**Response:**

```json
[
  {
    "id": 1,
    "patient_id": 1,
    "heart_rate": 88,
    "spo2": 97,
    "temperature": 37.2,
    "systolic_bp": 145,
    "diastolic_bp": 92,
    "respiratory_rate": 16,
    "is_valid": 1,
    "validation_errors": null,
    "has_anomalies": 1,
    "anomalies": "[{\"level\": \"WARNING\", ...}]",
    "recorded_at": "2024-05-24T10:30:45.123456",
    "created_at": "2024-05-24T10:30:45.123456"
  }
]
```

---

### 4. **Get Sensor Statistics**

```
GET /api/sensor/statistics/{patient_id}?minutes=5
```

**Response:**

```json
{
  "reading_count": 12,
  "timeframe_minutes": 5,
  "heart_rate": {
    "min": 75,
    "max": 98,
    "avg": 86.5,
    "median": 88
  },
  "spo2": {
    "min": 95,
    "max": 99,
    "avg": 97.2,
    "median": 97
  },
  "temperature": {
    "min": 36.9,
    "max": 37.5,
    "avg": 37.2,
    "median": 37.2
  },
  "timestamp": "2024-05-24T10:35:00.000000"
}
```

---

### 5. **Get Sensor Alerts**

```
GET /api/sensor/alerts/{patient_id}?limit=50
```

**Response:**

```json
[
  {
    "id": 5,
    "patient_id": 1,
    "sensor_reading_id": 10,
    "alert_level": "WARNING",
    "message": "HIGH: systolic_bp is 145 (normal: 90-120)",
    "affected_vital": "systolic_bp",
    "reading_value": 145,
    "normal_range_min": 90,
    "normal_range_max": 120,
    "anomaly_type": "above_range",
    "is_acknowledged": 0,
    "acknowledged_by": null,
    "acknowledged_at": null,
    "created_at": "2024-05-24T10:30:45.123456"
  }
]
```

---

### 6. **Get Recent Alerts**

```
GET /api/sensor/alerts/recent/{minutes}?minutes=5
```

**Response:**

```json
[
  {
    "timestamp": "2024-05-24T10:30:45.123456",
    "level": "WARNING",
    "message": "HIGH: systolic_bp is 145 (normal: 90-120)",
    "vital": "systolic_bp",
    "value": 145
  }
]
```

---

### 7. **Acknowledge Alert**

```
PUT /api/sensor/alerts/{alert_id}/acknowledge
```

**Request Body:**

```json
{
  "personnel_id": "P123"
}
```

**Response:**

```json
{
  "status": "acknowledged",
  "alert_id": 5
}
```

---

### 8. **Get Patient Sensor Status**

```
GET /api/sensor/patient-status/{patient_id}
```

**Response:**

```json
{
  "status": "WARNING",
  "critical_alerts": 0,
  "warning_alerts": 2,
  "current_reading": {
    "timestamp": "2024-05-24T10:30:45.123456",
    "heart_rate": 88,
    "spo2": 97,
    "temperature": 37.2,
    "systolic_bp": 145,
    "diastolic_bp": 92,
    "respiratory_rate": 16
  },
  "recent_alerts": [
    {
      "timestamp": "2024-05-24T10:30:45.123456",
      "level": "WARNING",
      "message": "HIGH: systolic_bp is 145",
      "vital": "systolic_bp",
      "value": 145
    }
  ]
}
```

**Status Values:**

- `STABLE`: All vitals normal, no alerts
- `WARNING`: Some vitals out of normal range
- `CRITICAL`: One or more critical alerts
- `NO_DATA`: No sensor readings available

---

## Alert Severity Calculation

### Critical Alerts (Level = CRITICAL):

- **SpO2 < 85%**: Severe hypoxia
- **Heart Rate < 40 or > 150**: Severe arrhythmia
- **Temperature > 40°C**: Dangerously high fever
- **Systolic BP > 180 mmHg**: Hypertensive crisis
- **Rapid change with severity > 0.8**: Critical anomaly

### Warning Alerts (Level = WARNING):

- **SpO2 85-94%**: Mild to moderate hypoxia
- **Heart Rate 40-50 or 120-150**: Abnormal rate
- **Temperature 35-36°C or 38.5-40°C**: Significant temperature issue
- **Systolic BP 140-180 mmHg**: Elevated blood pressure
- **Rapid change with severity 0.6-0.8**: Notable anomaly

### Info Alerts (Level = INFO):

- Minor out-of-range values
- Low-severity anomalies

---

## Anomaly Detection Types

### 1. **Rapid Change Detection**

Alerts when vital signs change dramatically in short timeframes:

- Heart Rate change > 30 BPM
- SpO2 change > 5%
- Temperature change > 0.5°C

### 2. **Statistical Outlier Detection**

Uses Z-score analysis (threshold 2.5):

- Identifies readings that deviate from recent average
- Adapts to patient's baseline
- Requires at least 3 historical readings

### 3. **Out of Range Detection**

Compares readings to normal physiological ranges:

- Immediate alerts for values outside normal ranges
- Severity scaled by distance from range

### 4. **Flatline Detection**

Detects sensor disconnection or failure:

- Multiple identical readings
- No variation over time

---

## Database Schema

### SensorReading Table

```sql
CREATE TABLE sensor_readings (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    heart_rate INTEGER NOT NULL,
    spo2 INTEGER NOT NULL,
    temperature FLOAT NOT NULL,
    systolic_bp INTEGER,
    diastolic_bp INTEGER,
    respiratory_rate INTEGER,
    is_valid INTEGER DEFAULT 1,
    validation_errors TEXT,
    has_anomalies INTEGER DEFAULT 0,
    anomalies TEXT,
    recorded_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### SensorAlert Table

```sql
CREATE TABLE sensor_alerts (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    sensor_reading_id INTEGER,
    alert_level VARCHAR NOT NULL,
    message TEXT NOT NULL,
    affected_vital VARCHAR NOT NULL,
    reading_value FLOAT NOT NULL,
    normal_range_min FLOAT,
    normal_range_max FLOAT,
    anomaly_type VARCHAR,
    is_acknowledged INTEGER DEFAULT 0,
    acknowledged_by VARCHAR,
    acknowledged_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Valid and Normal Ranges

### Heart Rate (BPM)

- **Valid Range**: 30-200
- **Normal Range**: 60-100
- **Critical Low**: < 40
- **Critical High**: > 150

### SpO2 (%)

- **Valid Range**: 50-100
- **Normal Range**: 95-100
- **Critical Low**: < 85

### Temperature (°C)

- **Valid Range**: 30-42
- **Normal Range**: 36.5-37.5
- **Critical Low**: < 35
- **Critical High**: > 40

### Systolic BP (mmHg)

- **Valid Range**: 60-200
- **Normal Range**: 90-120
- **High**: 130-139
- **Stage 1**: 140-159
- **Stage 2**: ≥ 160
- **Critical**: ≥ 180

### Diastolic BP (mmHg)

- **Valid Range**: 30-120
- **Normal Range**: 60-80

### Respiratory Rate (breaths/min)

- **Valid Range**: 5-40
- **Normal Range**: 12-20

---

## Usage Examples

### Example 1: Normal Reading

```bash
curl -X POST "http://localhost:8000/api/telemetry/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "heart_rate": 72,
    "spo2": 98,
    "temperature": 37.0,
    "systolic_bp": 120,
    "diastolic_bp": 80
  }'
```

**Response**: No alerts, status "processed"

### Example 2: Warning Condition

```bash
curl -X POST "http://localhost:8000/api/telemetry/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "heart_rate": 125,
    "spo2": 93,
    "temperature": 38.2,
    "systolic_bp": 155,
    "diastolic_bp": 98
  }'
```

**Response**: Multiple WARNING level alerts

### Example 3: Critical Condition

```bash
curl -X POST "http://localhost:8000/api/telemetry/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 2,
    "heart_rate": 155,
    "spo2": 82,
    "temperature": 40.5,
    "systolic_bp": 185,
    "diastolic_bp": 110
  }'
```

**Response**: Multiple CRITICAL level alerts

---

## Frontend Integration Example

### HTML/JavaScript

```html
<script>
  async function streamSensorData(patientId, vitals) {
    const response = await fetch("/api/telemetry/stream", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        patient_id: patientId,
        heart_rate: vitals.hr,
        spo2: vitals.spO2,
        temperature: vitals.temp,
        systolic_bp: vitals.systolic,
        diastolic_bp: vitals.diastolic,
      }),
    });

    const result = await response.json();

    // Update UI based on alerts
    if (result.alerts.length > 0) {
      const criticalAlerts = result.alerts.filter(
        (a) => a.level === "CRITICAL",
      );
      if (criticalAlerts.length > 0) {
        showCriticalAlert(criticalAlerts[0]);
      }
    }

    updateVitalsDisplay(result.processed_data);
  }

  // Get patient status every 30 seconds
  setInterval(async () => {
    const response = await fetch(`/api/sensor/patient-status/1`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const status = await response.json();
    updateStatusIndicator(status.status);
  }, 30000);
</script>
```

---

## Error Handling

### Invalid Request

```json
{
  "status": "processed",
  "valid": false,
  "errors": [
    "Missing required field: heart_rate",
    "spo2 92 outside valid range (50-100)"
  ],
  "alerts": []
}
```

### Patient Not Found

```json
{
  "detail": "No sensor readings found for this patient"
}
```

### Authentication Failed

```json
{
  "detail": "Not authenticated"
}
```

---

## Performance Considerations

- Sensor readings processed in <100ms
- Anomaly detection using in-memory history (10 readings)
- Database queries indexed by patient_id
- Alert aggregation for real-time display
- Automatic data retention (1000 recent readings in memory)

---

## Future Enhancements

1. **Machine Learning Integration**
   - Learn patient-specific normal ranges
   - Predictive anomaly detection

2. **Time Series Analysis**
   - Trend-based alerts (gradually increasing BP)
   - Seasonal pattern recognition

3. **Multi-sensor Correlation**
   - Correlate patterns across multiple vitals
   - Detect compound conditions

4. **Wireless Real-time Streaming**
   - WebSocket support for live streaming
   - Reduce latency for critical alerts

5. **Data Compression**
   - Automatic archiving of old readings
   - Efficient storage of historical data

6. **Integration with Wearables**
   - Support for Apple Watch, Fitbit, etc.
   - Multi-source data fusion
