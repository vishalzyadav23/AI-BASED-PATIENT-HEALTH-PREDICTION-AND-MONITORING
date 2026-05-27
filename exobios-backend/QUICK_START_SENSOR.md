# Quick Start - Real-time Sensor Data Processing

## Installation & Setup

### 1. Verify Dependencies

Ensure `requirements.txt` includes numpy:

```bash
pip install -r requirements.txt
```

### 2. Start the Backend Server

```bash
cd exobios-backend
python main.py
```

Server should start on `http://localhost:8000`

---

## Basic Usage

### Step 1: Stream Sensor Data

**Send a patient's vital signs:**

```bash
curl -X POST "http://localhost:8000/api/telemetry/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "heart_rate": 88,
    "spo2": 97,
    "temperature": 37.2,
    "systolic_bp": 145,
    "diastolic_bp": 92
  }'
```

**Response (Normal):**

```json
{
  "status": "processed",
  "valid": true,
  "errors": [],
  "alerts": []
}
```

**Response (With Alerts):**

```json
{
  "status": "processed",
  "valid": true,
  "errors": [],
  "alerts": [
    {
      "level": "WARNING",
      "message": "HIGH: systolic_bp is 145 (normal: 90-120)",
      "vital": "systolic_bp",
      "value": 145,
      "range": [90, 120]
    }
  ]
}
```

### Step 2: Get Current Patient Status

```bash
curl -X GET "http://localhost:8000/api/sensor/patient-status/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**

```json
{
  "status": "WARNING",
  "critical_alerts": 0,
  "warning_alerts": 2,
  "current_reading": {
    "heart_rate": 88,
    "spo2": 97,
    "temperature": 37.2
  },
  "recent_alerts": [...]
}
```

### Step 3: Check Patient History

```bash
curl -X GET "http://localhost:8000/api/sensor/history/1?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 4: Acknowledge Alerts

```bash
curl -X PUT "http://localhost:8000/api/sensor/alerts/5/acknowledge" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"personnel_id": "P001"}'
```

---

## Alert Severity Reference

| Status      | Color  | When                 | Action                 |
| ----------- | ------ | -------------------- | ---------------------- |
| 🟢 STABLE   | Green  | All vitals normal    | Continue monitoring    |
| 🟠 WARNING  | Orange | Some vitals abnormal | Monitor closely        |
| 🔴 CRITICAL | Red    | Critical condition   | Immediate intervention |

---

## Testing

### Run Complete Test Suite

```bash
cd exobios-backend
python test_sensor_processing.py
```

### Run Specific Test

```python
from test_sensor_processing import test_high_bp, test_critical_condition

# Test elevated BP
test_high_bp()

# Test critical condition
test_critical_condition()
```

---

## Integration with Frontend

### JavaScript Example

```javascript
async function streamSensorData(patientId, vitals) {
  try {
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

    // Handle alerts
    if (result.alerts.length > 0) {
      const criticalAlerts = result.alerts.filter(
        (a) => a.level === "CRITICAL",
      );
      if (criticalAlerts.length > 0) {
        showCriticalNotification(criticalAlerts[0].message);
      }
    }

    updateVitalsDisplay(result.processed_data);
  } catch (error) {
    console.error("Failed to stream sensor data:", error);
  }
}

// Stream every 5 seconds
setInterval(() => {
  const currentVitals = getLatestVitalsFromDevice();
  streamSensorData(currentPatientId, currentVitals);
}, 5000);
```

---

## Key Endpoints Reference

| Endpoint                          | Method | Purpose                  |
| --------------------------------- | ------ | ------------------------ |
| `/api/telemetry/stream`           | POST   | Stream sensor data       |
| `/api/telemetry/current`          | GET    | Get latest reading       |
| `/api/sensor/history/{id}`        | GET    | Patient history          |
| `/api/sensor/statistics/{id}`     | GET    | Statistics (min/max/avg) |
| `/api/sensor/alerts/{id}`         | GET    | Patient alerts           |
| `/api/sensor/patient-status/{id}` | GET    | Overall status           |

---

## Monitoring Dashboard Example

```html
<div class="patient-card">
  <h2 id="patient-name">Patient: Loading...</h2>
  <div id="status-indicator" class="status status-stable">
    <span>STABLE</span>
  </div>

  <div class="vitals-grid">
    <div class="vital">
      <span class="label">Heart Rate</span>
      <span id="hr-value" class="value">-- bpm</span>
      <div id="hr-alert" class="alert"></div>
    </div>
    <div class="vital">
      <span class="label">SpO2</span>
      <span id="spo2-value" class="value">-- %</span>
      <div id="spo2-alert" class="alert"></div>
    </div>
    <div class="vital">
      <span class="label">Temperature</span>
      <span id="temp-value" class="value">-- °C</span>
      <div id="temp-alert" class="alert"></div>
    </div>
  </div>

  <div id="alerts-container" class="alerts"></div>
</div>

<script>
  async function updateDashboard(patientId) {
    try {
      const response = await fetch(`/api/sensor/patient-status/${patientId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      const status = await response.json();

      // Update status
      const statusEl = document.getElementById("status-indicator");
      statusEl.className = `status status-${status.status.toLowerCase()}`;
      statusEl.textContent = status.status;

      // Update vitals
      if (status.current_reading) {
        document.getElementById("hr-value").textContent =
          `${status.current_reading.heart_rate} bpm`;
        document.getElementById("spo2-value").textContent =
          `${status.current_reading.spo2} %`;
        document.getElementById("temp-value").textContent =
          `${status.current_reading.temperature} °C`;
      }

      // Update alerts
      const alertsContainer = document.getElementById("alerts-container");
      alertsContainer.innerHTML = "";
      for (const alert of status.recent_alerts) {
        const alertEl = document.createElement("div");
        alertEl.className = `alert alert-${alert.level.toLowerCase()}`;
        alertEl.textContent = alert.message;
        alertsContainer.appendChild(alertEl);
      }
    } catch (error) {
      console.error("Dashboard update failed:", error);
    }
  }

  // Update every 5 seconds
  setInterval(() => updateDashboard(1), 5000);
</script>

<style>
  .status {
    display: inline-block;
    padding: 10px 20px;
    border-radius: 5px;
    font-weight: bold;
  }

  .status-stable {
    background-color: #4caf50;
    color: white;
  }
  .status-warning {
    background-color: #ff9800;
    color: white;
  }
  .status-critical {
    background-color: #f44336;
    color: white;
  }

  .alert {
    padding: 10px;
    margin: 5px 0;
    border-left: 4px solid;
  }

  .alert-info {
    border-color: #2196f3;
    background-color: #e3f2fd;
  }
  .alert-warning {
    border-color: #ff9800;
    background-color: #fff3e0;
  }
  .alert-critical {
    border-color: #f44336;
    background-color: #ffebee;
  }
</style>
```

---

## Database Queries

### Get All Critical Alerts

```sql
SELECT * FROM sensor_alerts
WHERE alert_level = 'CRITICAL'
AND is_acknowledged = 0
ORDER BY created_at DESC;
```

### Get Reading Trends for a Patient

```sql
SELECT
  DATE(recorded_at) as date,
  AVG(heart_rate) as avg_hr,
  AVG(spo2) as avg_spo2,
  AVG(temperature) as avg_temp
FROM sensor_readings
WHERE patient_id = 1
GROUP BY DATE(recorded_at);
```

### Find Patients with Anomalies

```sql
SELECT DISTINCT patient_id, COUNT(*) as anomaly_count
FROM sensor_readings
WHERE has_anomalies = 1
GROUP BY patient_id
ORDER BY anomaly_count DESC;
```

---

## Troubleshooting

### Issue: "No sensor readings available"

- **Cause**: No data streamed yet
- **Solution**: First, POST data to `/api/telemetry/stream`

### Issue: All vital signs show as "WARNING"

- **Cause**: Values outside normal ranges
- **Solution**: Check if actual vital signs are abnormal or adjust normal ranges

### Issue: Duplicate alerts

- **Cause**: Same condition detected in consecutive readings
- **Solution**: This is normal - acknowledge alerts to reduce noise

### Issue: Database errors

- **Cause**: Tables not created
- **Solution**: Restart server - models.py auto-creates tables on startup

---

## Performance Optimization Tips

1. **Batch Updates**: Send multiple readings in one request (future feature)
2. **Reduce Frequency**: If processing too fast, increase `REPORTING_PERIOD_MS` on Arduino
3. **Archive Old Data**: Move readings older than 30 days to archive table
4. **Index Optimization**: Add index on (patient_id, created_at) for faster queries
5. **Caching**: Cache patient status for 5-10 seconds to reduce DB queries

---

## Next Steps

1. ✅ Integrate with Arduino/IoT devices
2. ✅ Build frontend dashboard
3. ✅ Set up alert notifications (email/SMS)
4. ✅ Create alert rules configuration
5. ✅ Add historical trend analysis
