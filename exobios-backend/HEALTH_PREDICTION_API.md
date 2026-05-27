# Health Prediction Model Integration - API Documentation

## Overview

The Health Prediction Model Integration provides AI-powered health risk assessment for patients in real-time. It uses machine learning algorithms to analyze vital signs and patient data, then integrates with Google Gemini for enhanced clinical insights.

---

## Features

### 1. **Comprehensive Health Assessment**

- Calculates risk scores for multiple conditions:
  - **Cardiovascular Disease**: Uses Framingham Risk Score approach
  - **Stroke Risk**: Uses simplified CHADS2 Score approach
  - **Hypoxia Risk**: Based on blood oxygen saturation (SpO2)
  - **Fever/Infection Risk**: Temperature-based assessment

### 2. **Real-time Risk Categorization**

- **Overall Categories**: STABLE, MONITOR, ALERT, CRITICAL
- **Priority Levels**: RESUSCITATION, EMERGENT, URGENT, SEMI-URGENT, NON-URGENT
- **Color Coding**: Red (Critical), Orange (Emergent), Yellow (Urgent), Blue (Semi-Urgent), Green (Non-Urgent)

### 3. **AI-Powered Insights**

- Integration with Google Gemini for clinical insights
- Personalized recommendations based on patient data
- Automated analysis of critical factors

### 4. **Persistent Storage**

- All predictions stored in database for patient history tracking
- Timestamps for temporal analysis

---

## API Endpoints

### 1. **Comprehensive Health Prediction**

```
POST /api/predict/health
```

**Request Body:**

```json
{
  "patient_id": 1,
  "age": 65,
  "sex": "male",
  "heart_rate": 88,
  "systolic_bp": 145,
  "diastolic_bp": 92,
  "spo2": 97,
  "temperature": 37.2,
  "symptoms": "Chest pain, shortness of breath",
  "medical_history": "Hypertension, Diabetes"
}
```

**Response:**

```json
{
  "id": 1,
  "patient_id": 1,
  "overall_risk_score": 52,
  "overall_category": "ALERT",
  "priority_level": "URGENT",
  "cardiovascular_risk": 45,
  "stroke_risk": 38,
  "hypoxia_risk": 5,
  "fever_risk": 8,
  "heart_rate": 88,
  "systolic_bp": 145,
  "diastolic_bp": 92,
  "spo2": 97,
  "temperature": 37.2,
  "critical_factors": "Stage 1 Hypertension: 145/92 mmHg, Age-related risk: 65 years",
  "ai_insights": "Patient presenting with hypertension and elevated cardiac load. Close monitoring recommended.",
  "ai_recommendations": "1. Monitor blood pressure every 5 minutes\n2. Prepare for potential cardiac intervention\n3. Establish IV access for medication administration",
  "created_at": "2024-05-24T10:30:45.123456",
  "updated_at": "2024-05-24T10:30:45.123456"
}
```

**Risk Calculation Details:**

- Systolic BP 145: +10 (Stage 1 Hypertension)
- Age 65: +10 (Age-related risk)
- Normal heart rate, SpO2, temperature: Minimal additional risk
- Overall: Moderate cardiovascular risk → ALERT status → URGENT priority

---

### 2. **Get Prediction History**

```
GET /api/predict/history/{patient_id}
```

**Response:** Array of past predictions, ordered by most recent first.

**Example:**

```json
[
  {
    "id": 10,
    "patient_id": 1,
    "overall_risk_score": 55,
    "overall_category": "ALERT",
    "priority_level": "URGENT",
    "created_at": "2024-05-24T10:30:45.123456"
  },
  {
    "id": 9,
    "patient_id": 1,
    "overall_risk_score": 45,
    "overall_category": "MONITOR",
    "priority_level": "SEMI-URGENT",
    "created_at": "2024-05-24T09:15:30.654321"
  }
]
```

---

### 3. **Get Latest Prediction**

```
GET /api/predict/latest/{patient_id}
```

**Response:** Most recent prediction for the patient.

---

### 4. **Quick Triage Assessment (No Database Save)**

```
POST /api/predict/risk-factors
```

**Request Body:** (Same as comprehensive prediction)

**Response:**

```json
{
  "timestamp": "2024-05-24T10:30:45.123456",
  "overall_risk_score": 52,
  "overall_category": "ALERT",
  "individual_assessments": [
    {
      "score": 45,
      "category": "MODERATE",
      "risk_factors": ["Stage 1 Hypertension: 145/92 mmHg"],
      "condition": "Cardiovascular Disease"
    },
    {
      "score": 38,
      "category": "MODERATE",
      "risk_factors": ["Age 65 (65-74 years)"],
      "condition": "Stroke"
    },
    {
      "score": 5,
      "category": "LOW",
      "risk_factors": ["Normal SpO2: 97%"],
      "condition": "Hypoxia"
    },
    {
      "score": 0,
      "category": "NORMAL",
      "risk_factors": ["Normal temperature: 37.2°C"],
      "condition": "Infection/Fever"
    }
  ],
  "critical_factors": [
    "Stage 1 Hypertension: 145/92 mmHg",
    "Age-related risk: 65 years"
  ],
  "vital_signs": {
    "heart_rate": 88,
    "systolic_bp": 145,
    "diastolic_bp": 92,
    "spo2": 97,
    "temperature": 37.2
  },
  "patient_info": {
    "age": 65,
    "sex": "male",
    "symptoms": "Chest pain",
    "medical_history": "Hypertension"
  },
  "priority_level": "URGENT",
  "ai_insights": "Patient with hypertension and elevated risk. Monitor closely."
}
```

---

### 5. **Quick Field Triage (Minimal Parameters)**

```
GET /api/predict/quick-triage?heart_rate=88&systolic_bp=145&diastolic_bp=92&spo2=97&temperature=37.2&age=65
```

**Response:**

```json
{
  "risk_score": 35,
  "priority_level": "SEMI-URGENT",
  "priority_color": "blue",
  "alerts": ["HIGH: Stage 2 hypertension (145/92)"],
  "vital_signs": {
    "heart_rate": 88,
    "systolic_bp": 145,
    "diastolic_bp": 92,
    "spo2": 97,
    "temperature": 37.2
  }
}
```

---

## Risk Scoring System

### Cardiovascular Risk Factors:

- **Heart Rate**: <60 or >100 bpm: +15 points
- **Hypertension Stage 2**: (SBP ≥140 or DBP ≥90): +20 points
- **Hypertension Stage 1**: (SBP ≥130 or DBP ≥80): +10 points
- **Age >50**: +10 points (varies with age)
- **Male**: +5 points

### Stroke Risk Factors:

- **Age ≥75**: +15 points
- **Age 65-74**: +10 points
- **Hypertension (SBP ≥140)**: +15 points
- **Severe HR abnormality** (>120 or <40): +20 points

### Hypoxia Risk:

- **SpO2 ≥95%**: Low (5 points)
- **SpO2 90-94%**: Moderate (30 points)
- **SpO2 85-89%**: High (65 points)
- **SpO2 <85%**: Very High (95 points)

### Fever/Infection Risk:

- **Hypothermia** (<36.5°C): Moderate (20 points)
- **Normal** (36.5-37.5°C): Low (0 points)
- **Mild Fever** (37.5-38.5°C): Moderate (20 points)
- **High Fever** (38.5-39.5°C): High (50 points)
- **Critical** (>39.5°C): Very High (85 points)

---

## Priority Levels Mapping

| Risk Score | Priority Level | Color  | Action                             |
| ---------- | -------------- | ------ | ---------------------------------- |
| ≥80        | RESUSCITATION  | Red    | Immediate life-saving intervention |
| 60-79      | EMERGENT       | Orange | Urgent evaluation & treatment      |
| 40-59      | URGENT         | Yellow | Prompt evaluation needed           |
| 20-39      | SEMI-URGENT    | Blue   | Non-urgent evaluation              |
| <20        | NON-URGENT     | Green  | Routine care                       |

---

## Integration with Gemini AI

For each prediction, the system prompts Gemini with:

- Patient demographics
- Risk assessment results
- Vital signs
- Critical factors

Gemini returns:

1. **Clinical Insight**: One-line summary of clinical significance
2. **Recommendations**: Specific actionable steps for paramedics

Example Gemini Prompt:

```
Based on this medical assessment, provide a brief clinical insight:

Patient: 65 yo male
Overall Risk: ALERT (52/100)
Priority: URGENT
Critical Factors: Stage 1 Hypertension: 145/92 mmHg; Age-related risk: 65 years
Vital Signs: HR=88, BP=145/92, SpO2=97%, Temp=37.2°C

Provide:
1. One-line clinical insight (max 20 words)
2. Two immediate recommendations for paramedic care
Keep response concise and actionable.
```

---

## Database Schema

### HealthPrediction Table

```sql
CREATE TABLE health_predictions (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    overall_risk_score INTEGER NOT NULL,
    overall_category VARCHAR NOT NULL,
    priority_level VARCHAR NOT NULL,
    cardiovascular_risk INTEGER NOT NULL,
    stroke_risk INTEGER NOT NULL,
    hypoxia_risk INTEGER NOT NULL,
    fever_risk INTEGER NOT NULL,
    heart_rate INTEGER,
    systolic_bp INTEGER,
    diastolic_bp INTEGER,
    spo2 INTEGER,
    temperature FLOAT,
    critical_factors TEXT,
    ai_insights TEXT,
    ai_recommendations TEXT,
    created_at DATETIME,
    updated_at DATETIME
);
```

---

## Usage Examples

### Example 1: Patient with Hypertension

```bash
curl -X POST "http://localhost:8000/api/predict/health" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "age": 58,
    "sex": "female",
    "heart_rate": 95,
    "systolic_bp": 155,
    "diastolic_bp": 98,
    "spo2": 96,
    "temperature": 37.0,
    "symptoms": "Headache, dizziness",
    "medical_history": "Hypertension on medication"
  }'
```

**Expected Risk Score: 55-60 (ALERT/URGENT)**

### Example 2: Critical Patient with Low Oxygen

```bash
curl -X POST "http://localhost:8000/api/predict/health" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 2,
    "age": 72,
    "sex": "male",
    "heart_rate": 125,
    "systolic_bp": 165,
    "diastolic_bp": 95,
    "spo2": 88,
    "temperature": 38.5,
    "symptoms": "Severe respiratory distress",
    "medical_history": "COPD, Cardiac history"
  }'
```

**Expected Risk Score: 85+ (CRITICAL/RESUSCITATION)**

### Example 3: Stable Patient

```bash
curl -X POST "http://localhost:8000/api/predict/health" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 3,
    "age": 35,
    "sex": "female",
    "heart_rate": 72,
    "systolic_bp": 118,
    "diastolic_bp": 76,
    "spo2": 98,
    "temperature": 37.0,
    "symptoms": "Minor ankle injury",
    "medical_history": "No significant history"
  }'
```

**Expected Risk Score: <15 (STABLE/NON-URGENT)**

---

## Frontend Integration Example

### HTML/JavaScript Integration

```html
<script>
  async function performHealthAssessment(patientData) {
    const token = localStorage.getItem("access_token");

    const response = await fetch("/api/predict/health", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(patientData),
    });

    const prediction = await response.json();

    // Color-code based on priority
    const colorMap = {
      RESUSCITATION: "#d32f2f", // Red
      EMERGENT: "#f57c00", // Orange
      URGENT: "#fbc02d", // Yellow
      "SEMI-URGENT": "#1976d2", // Blue
      "NON-URGENT": "#388e3c", // Green
    };

    document.getElementById("risk-display").style.backgroundColor =
      colorMap[prediction.priority_level];
    document.getElementById("risk-text").textContent =
      `Risk: ${prediction.overall_risk_score}/100 - ${prediction.priority_level}`;
    document.getElementById("ai-insights").textContent = prediction.ai_insights;
  }
</script>
```

---

## Error Handling

### Common Error Responses

**400 Bad Request:**

```json
{
  "detail": "Prediction error: Invalid vital signs"
}
```

**404 Not Found:**

```json
{
  "detail": "No predictions found for this patient"
}
```

**401 Unauthorized:**

```json
{
  "detail": "Not authenticated"
}
```

---

## Performance Considerations

- Predictions are calculated in <500ms
- Gemini AI integration adds ~1-2 seconds for insights
- Database queries for history are indexed by patient_id
- Consider caching frequent predictions for the same patient

---

## Future Enhancements

1. **Machine Learning Model Training**
   - Train on historical patient data
   - Improve accuracy with local datasets

2. **Trend Analysis**
   - Track patient risk score over time
   - Identify deterioration patterns

3. **Multi-Condition Risk Correlations**
   - Consider comorbidities
   - Adjust risks based on interactions

4. **Predictive Alerts**
   - Alert paramedics 30 minutes before potential crisis
   - Based on trend analysis

5. **Integration with Wearables**
   - Real-time continuous monitoring
   - Automatic alerts on critical threshold breach
