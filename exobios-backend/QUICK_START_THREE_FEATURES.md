# Three Advanced Features - Implementation Guide

Quick start guide for Time-Series Trend Analysis, Sepsis Risk Assessment, and Firebase Mobile Notifications.

## What's New

### ✅ Feature 1: Time-Series Trend Analysis

- **24h, 7d, 30d trend tracking** for all vital signs
- **ARIMA forecasting** with 95% confidence intervals
- **Automatic clinical alerts** for dangerous trends
- Volatility analysis and rate-of-change detection

### ✅ Feature 2: Sepsis Risk Assessment

- **SOFA scoring** (0-24 scale)
- **qSOFA rapid assessment** (0-3 scale)
- **Sepsis probability scoring** (0-100%)
- Automatic mobile alerts when risk is HIGH or CRITICAL

### ✅ Feature 3: Firebase Mobile Notifications

- **iOS & Android support** via Firebase Cloud Messaging
- **Automatic critical alerts** when patient condition worsens
- **Device management** - register/track/deregister devices
- **Notification history** - audit trail of all alerts sent

---

## Installation

### Step 1: Update Dependencies

```bash
cd exobios-backend
pip install -r requirements.txt
```

New packages added:

- `firebase-admin==6.2.0` - Push notifications
- `statsmodels==0.14.0` - Advanced time-series analysis

### Step 2: Configure Firebase (Optional for Development)

**For Development/Testing** (notifications will be simulated):

- No setup required, features work in "demo mode"

**For Production** (real mobile notifications):

1. Follow [FIREBASE_SETUP.md](FIREBASE_SETUP.md)
2. Get `firebase_credentials.json`
3. Place in `exobios-backend/` directory

### Step 3: Create Database Tables

Automatically created on first run, but manually:

```bash
python -c "from main import models; models.Base.metadata.create_all()"
```

---

## Quick Start

### Start the Backend Server

```bash
# In exobios-backend directory
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Test the Features

#### 1. Test Trends

```bash
# Get 24-hour trends for patient 1
curl -X GET "http://localhost:8000/api/trends/1/24" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get 7-day trends
curl -X GET "http://localhost:8000/api/trends/1/168" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get specific vital trend
curl -X GET "http://localhost:8000/api/trends/vital/1/heart_rate/24" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response includes:**

- Current statistics (mean, std dev, min, max)
- Trend direction (increasing/decreasing/stable)
- ARIMA forecast for next 6 readings
- Automatic clinical alerts if needed

#### 2. Test Sepsis Risk Assessment

```bash
curl -X POST "http://localhost:8000/api/sepsis/assess" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "vitals": {
      "heart_rate": 110,
      "respiratory_rate": 24,
      "systolic_bp": 95,
      "temperature": 38.8,
      "spo2": 92,
      "gcs": 15,
      "lactate": 2.5,
      "platelets": 180,
      "bilirubin": 0.9,
      "creatinine": 1.1,
      "urine_output": 0.8
    }
  }'
```

**Response includes:**

- Sepsis probability (0-100%)
- Risk level (LOW/MILD/MODERATE/HIGH/CRITICAL)
- SOFA score breakdown
- qSOFA score breakdown
- Clinical recommendation for action

#### 3. Test Mobile Notifications

```bash
# Register a device (get FCM token from mobile app)
curl -X POST "http://localhost:8000/api/notifications/register-device" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_token": "f8wCl3-xYsY:APA91bF1JzAh...",
    "device_type": "iOS",
    "device_model": "iPhone 14"
  }'

# Send test notification
curl -X POST "http://localhost:8000/api/notifications/test/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get notification history
curl -X GET "http://localhost:8000/api/notifications/history/1?limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## API Endpoints Summary

### Trends

| Endpoint                                              | Method | Description            |
| ----------------------------------------------------- | ------ | ---------------------- |
| `/api/trends/{patient_id}/{hours}`                    | GET    | Get all vital trends   |
| `/api/trends/vital/{patient_id}/{vital_name}/{hours}` | GET    | Get single vital trend |

### Sepsis

| Endpoint                           | Method | Description            |
| ---------------------------------- | ------ | ---------------------- |
| `/api/sepsis/assess`               | POST   | Calculate sepsis risk  |
| `/api/sepsis/history/{patient_id}` | GET    | Get assessment history |

### Notifications

| Endpoint                                       | Method | Description            |
| ---------------------------------------------- | ------ | ---------------------- |
| `/api/notifications/register-device`           | POST   | Register mobile device |
| `/api/notifications/deregister-device/{token}` | DELETE | Unregister device      |
| `/api/notifications/devices/{patient_id}`      | GET    | List patient devices   |
| `/api/notifications/test/{patient_id}`         | POST   | Send test notification |
| `/api/notifications/history/{patient_id}`      | GET    | Get notification logs  |

---

## Features in Detail

### Trend Analysis Features

**What It Does:**

- Tracks vital signs over time (24 hours, 7 days, 30 days)
- Detects trends (increasing, decreasing, stable)
- Measures volatility (steady vs. fluctuating)
- Predicts next values with ARIMA
- Generates clinical alerts

**Clinical Use:**

- Spot deteriorating trends before critical
- Distinguish true changes from noise
- Predict when intervention needed
- Early warning system

**Example Alerts:**

- "Heart rate rapidly increasing - monitor closely"
- "Forecast predicts SpO2 will drop below 95%"
- "Temperature showing high variability"

### Sepsis Risk Assessment

**What It Does:**

- Scores organ dysfunction (SOFA: 0-24)
- Quick bedside assessment (qSOFA: 0-3)
- Calculates sepsis probability (0-100%)
- Provides clinical recommendations

**Clinical Use:**

- Early detection of sepsis (before clinical deterioration)
- Risk stratification for treatment decisions
- Protocol triggering (if high risk)
- Outcome prediction

**Example Output:**

```
Risk Level: HIGH (65% probability)
qSOFA Score: 2/3 ← ALERT THRESHOLD
SOFA Score: 5/24
Recommendation: "HIGH PRIORITY: Evaluate for sepsis.
  Consider blood cultures and lactate measurement."
```

### Mobile Notifications

**What It Does:**

- Sends push notifications to iOS/Android
- Automatic triggers on critical events
- Device management (register/deregister)
- Notification history and audit trail

**Automatic Triggers:**

1. **CRITICAL_ALERT** - Patient in critical condition
2. **SEPSIS_WARNING** - High sepsis probability
3. **ANOMALY** - Anomaly detected
4. **UNREVIEWED_ALERT** - Alerts pending review

**Example Notification:**

```
Title: 🚨 CRITICAL ALERT - Patient 1
Body: SpO2 dropped to 88% - immediate action needed
Data: {patient_id: 1, vital: spo2, value: 88, action: open_details}
```

---

## Database Changes

Three new tables created automatically:

### DeviceToken

Stores mobile device registration info

```
Fields: id, patient_id, device_token, device_type, is_active,
        registered_at, last_used, deregistered_at
```

### NotificationLog

Audit trail of all notifications

```
Fields: id, patient_id, notification_type, title, message,
        send_status, sent_to_devices, failed_devices,
        created_at, sent_at
```

### SepsisRiskLog

Historical sepsis risk assessments

```
Fields: id, patient_id, qsofa_score, sofa_score, sepsis_probability,
        risk_level, clinical_recommendation, created_at, assessment_time
```

---

## Integration with Existing Features

### With Health Prediction

- Sepsis assessment complements cardiovascular/stroke risk
- Higher accuracy for multi-condition patients
- Automatic notifications if both systems flag risk

### With Sensor Processing

- Trends automatically calculated from sensor readings
- Anomalies feed into sepsis scoring
- Alert data stored for notifications

### With Existing API

- All endpoints require JWT authentication
- Follow same response format as existing endpoints
- Compatible with current database schema

---

## Configuration Files

### New Environment Variables (Optional)

Add to `.env`:

```env
# Firebase (optional - works without it)
FIREBASE_CREDENTIALS_PATH=firebase_credentials.json
FIREBASE_PROJECT_ID=your-project-id

# Notification settings (optional)
NOTIFICATION_BATCH_SIZE=10
NOTIFICATION_THROTTLE_MINUTES=1
```

### Requirements Updated

```
firebase-admin==6.2.0
statsmodels==0.14.0
```

---

## Troubleshooting

### Trends Not Working

**Problem:** 404 "No readings available"
**Solution:**

- Ensure sensor data is being stored (check SensorReading table)
- Try larger time period (7 days vs 24 hours)
- Verify patient_id matches database

### Sepsis Assessment Not Working

**Problem:** Missing required vital fields
**Solution:**

- Include all vitals in request: heart_rate, respiratory_rate, systolic_bp, spo2, temperature, gcs
- Use sensible default values if not available
- Optional fields: lactate, platelets, bilirubin, creatinine

### Notifications Not Sending

**Problem:** Firebase not initialized
**Solution (Development):**

- Notifications work in "simulated" mode without Firebase
- Check response: `"status": "simulated"`

**Solution (Production):**

- Follow [FIREBASE_SETUP.md](FIREBASE_SETUP.md)
- Verify `firebase_credentials.json` exists
- Check `.env` FIREBASE_CREDENTIALS_PATH

### Notifications Not Received on Mobile

**Problem:** Devices not registered
**Solution:**

- Call `/api/notifications/register-device` with valid FCM token
- Verify device_type matches (iOS/Android)
- Check notifications enabled in app/OS settings

---

## Performance Optimization

### Large Datasets

If analyzing patients with thousands of readings:

- Use specific time periods (24h instead of 30d)
- Query specific vitals instead of all
- Implement pagination for history endpoints

### High-Frequency Alerts

If getting too many alerts:

- Implement alert throttling (1 per vital per minute)
- Aggregate related alerts
- Use notification batching

### Database Scaling

For production with many patients:

- Index: patient_id, recorded_at
- Partition SensorReading table by date
- Archive old notifications (>30 days)

---

## Next Steps

1. ✅ **Verify Installation** - Run tests above
2. ✅ **Mobile Integration** - Add Firebase SDK to apps
3. ✅ **Configure Firebase** - Set up for production (optional)
4. ✅ **Frontend Integration** - Display trends/alerts on dashboard
5. ✅ **Clinical Workflows** - Integrate into care protocols
6. ✅ **Monitor Performance** - Check logs and notification delivery

---

## Documentation Files

- **FIREBASE_SETUP.md** - Complete Firebase configuration guide
- **TREND_SEPSIS_NOTIFICATIONS_API.md** - Full API reference
- **ARDUINO_INTEGRATION.md** - Sensor data integration
- **SENSOR_DATA_PROCESSING.md** - Real-time processing details
- **HEALTH_PREDICTION_API.md** - Health risk scoring

---

## Support

For issues or questions:

1. Check [TREND_SEPSIS_NOTIFICATIONS_API.md](TREND_SEPSIS_NOTIFICATIONS_API.md) for API details
2. Review error messages and HTTP status codes
3. Check database tables for data presence
4. Verify JWT tokens are valid and not expired
5. Test endpoints with cURL before integrating

---

## Summary

You now have three powerful new features:

| Feature           | What It Does                         | When to Use                                      |
| ----------------- | ------------------------------------ | ------------------------------------------------ |
| **Trends**        | Track and predict vital sign changes | Monitor for deterioration, predict interventions |
| **Sepsis**        | Early detection of sepsis            | Flag high-risk patients automatically            |
| **Notifications** | Real-time mobile alerts              | Keep clinicians informed 24/7                    |

All three work together to provide **early warning, accurate risk assessment, and instant alerts** for better patient outcomes.
