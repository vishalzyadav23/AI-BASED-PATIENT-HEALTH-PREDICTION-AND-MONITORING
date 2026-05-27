# backend/main.py
import os
import smtplib
import random
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json

# --- The modern, official Google GenAI SDK ---
from dotenv import load_dotenv
from google import genai

import models
import schemas
import security
from database import engine, get_db
from health_prediction import prediction_model
from sensor_processor import sensor_processor
from timeseries_analysis import trend_analyzer
from sepsis_risk import sepsis_calculator
from firebase_notifications import notification_manager

# Load the secret .env file
load_dotenv()

# Configure the new Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    gemini_client = genai.Client(api_key=api_key)
else:
    gemini_client = None

# Create Database Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Based Patient Health Prediction & Monitoring API", version="1.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LATEST_HARDWARE_DATA = {
    "bpm": "--", "spo2": "--", "temperature": "--", "systolic_bp": None, "diastolic_bp": None
}

class LoginRequest(BaseModel):
    personnel_id: str
    password: str

# ==========================================
# OTP AUTHENTICATION SYSTEM
# ==========================================
OTP_STORE = {}

class OTPRequest(BaseModel):
    email: str

class OTPVerify(BaseModel):
    email: str
    otp: str

@app.post("/api/otp/send")
def send_otp(request: OTPRequest):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    if not sender_email or not sender_password or sender_email == "your_actual_email@gmail.com":
        raise HTTPException(status_code=500, detail="Email server not configured in .env")

    otp_code = str(random.randint(1000, 9999))
    OTP_STORE[request.email] = otp_code
    
    try:
        msg = MIMEText(f"Your Exobios Clinical secure verification code is: {otp_code}\n\nDo not share this code with anyone.")
        msg['Subject'] = "Exobios Verification Code"
        msg['From'] = f"Exobios Security <{sender_email}>"
        msg['To'] = request.email
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            
        return {"message": "OTP sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to route email: {str(e)}")

@app.post("/api/otp/verify")
def verify_otp(request: OTPVerify):
    stored_otp = OTP_STORE.get(request.email)
    
    if not stored_otp or stored_otp != request.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
    
    del OTP_STORE[request.email]
    return {"message": "Identity Verified"}

# ==========================================
# SECURE PASSWORD RESET FLOW
# ==========================================
class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    email: str
    otp: str
    new_password: str

@app.post("/api/password-reset/request")
def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.personnel_id == request.email).first()
    if not user:
        return {"message": "If registered, an OTP has been sent."}
    
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    otp_code = str(random.randint(1000, 9999))
    OTP_STORE[request.email] = otp_code
    
    try:
        msg = MIMEText(f"We received a request to reset your password.\n\nYour secure reset code is: {otp_code}\n\nIf you did not request this, please ignore this email.")
        msg['Subject'] = "Exobios Password Reset Request"
        msg['From'] = f"Exobios Security <{sender_email}>"
        msg['To'] = request.email
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send reset email: {e}")
        
    return {"message": "If registered, an OTP has been sent."}

@app.post("/api/password-reset/confirm")
def confirm_password_reset(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    stored_otp = OTP_STORE.get(request.email)
    if not stored_otp or stored_otp != request.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired recovery code.")
    
    user = db.query(models.User).filter(models.User.personnel_id == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    user.hashed_password = security.get_password_hash(request.new_password)
    db.commit()
    del OTP_STORE[request.email]
    
    return {"message": "Password successfully updated."}

# ==========================================
# ENDPOINT 1: Register Initial Paramedic
# ==========================================
@app.post("/api/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.personnel_id == user.personnel_id).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Personnel ID already registered")
    
    hashed_pw = security.get_password_hash(user.password)
    new_user = models.User(
        personnel_id=user.personnel_id, 
        name=user.name, 
        phone=user.phone,                  # POSTGRES FIELD
        pin_code=user.pin_code,            # POSTGRES FIELD
        area_location=user.area_location,  # POSTGRES FIELD
        region=user.region,                # POSTGRES FIELD
        hashed_password=hashed_pw, 
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ==========================================
# ENDPOINT 2: Secure Login
# ==========================================
@app.post("/api/login", response_model=schemas.Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.personnel_id == credentials.personnel_id).first()
    if not user or not security.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Personnel ID or Security Key"
        )
    access_token = security.create_access_token(data={"sub": user.personnel_id})
    return {"access_token": access_token, "token_type": "bearer"}

# ==========================================
# ENDPOINT 3: Secure Patient Intake
# ==========================================
@app.post("/api/patients", response_model=schemas.PatientResponse)
def create_patient(
    patient: schemas.PatientCreate, 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    new_patient = models.Patient(**patient.model_dump())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

# ==========================================
# ENDPOINT 4: Get Latest Patient
# ==========================================
@app.get("/api/patients/latest", response_model=schemas.PatientResponse)
def get_latest_patient(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    patient = db.query(models.Patient).order_by(models.Patient.id.desc()).first()
    if not patient:
        raise HTTPException(status_code=404, detail="No patients found in the active queue.")
    return patient

# ==========================================
# ENDPOINT 5: Advanced Sensor Data Processing
# ==========================================

@app.post("/api/telemetry/stream", response_model=schemas.SensorProcessingResult)
def stream_telemetry_data(data: schemas.SensorReadingCreate, db: Session = Depends(get_db)):
    global LATEST_HARDWARE_DATA
    
    LATEST_HARDWARE_DATA["bpm"] = data.heart_rate
    LATEST_HARDWARE_DATA["spo2"] = data.spo2
    LATEST_HARDWARE_DATA["temperature"] = round(data.temperature, 2) if data.temperature else "--"
    LATEST_HARDWARE_DATA["systolic_bp"] = data.systolic_bp
    LATEST_HARDWARE_DATA["diastolic_bp"] = data.diastolic_bp

    processing_result = sensor_processor.process_telemetry({
        "patient_id": data.patient_id,
        "heart_rate": data.heart_rate,
        "spo2": data.spo2,
        "temperature": data.temperature,
        "systolic_bp": data.systolic_bp,
        "diastolic_bp": data.diastolic_bp,
        "respiratory_rate": data.respiratory_rate
    })
    
    if not processing_result["valid"]:
        return schemas.SensorProcessingResult(**processing_result)
    
    db_reading = models.SensorReading(
        patient_id=data.patient_id,
        heart_rate=data.heart_rate,
        spo2=data.spo2,
        temperature=data.temperature,
        systolic_bp=data.systolic_bp,
        diastolic_bp=data.diastolic_bp,
        respiratory_rate=data.respiratory_rate,
        is_valid=1 if processing_result["valid"] else 0,
        validation_errors="; ".join(processing_result["errors"]),
        has_anomalies=1 if processing_result["alerts"] else 0,
        anomalies=str(processing_result["alerts"]),
        recorded_at=datetime.fromisoformat(processing_result["timestamp"])
    )
    
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    
    for alert_data in processing_result["alerts"]:
        db_alert = models.SensorAlert(
            patient_id=data.patient_id,
            sensor_reading_id=db_reading.id,
            alert_level=alert_data["level"],
            message=alert_data["message"],
            affected_vital=alert_data["vital"],
            reading_value=alert_data["value"],
            normal_range_min=alert_data["range"][0],
            normal_range_max=alert_data["range"][1]
        )
        db.add(db_alert)
    
    db.commit()
    
    return schemas.SensorProcessingResult(**processing_result)

@app.get("/api/telemetry/current")
def get_current_telemetry():
    current = sensor_processor.get_current_reading()
    if not current:
        raise HTTPException(status_code=404, detail="No sensor readings available")
    return current

@app.get("/api/telemetry")
def get_telemetry():
    return LATEST_HARDWARE_DATA

@app.get("/api/sensor/history/{patient_id}", response_model=List[schemas.SensorReadingResponse])
def get_sensor_history(
    patient_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    readings = db.query(models.SensorReading).filter(
        models.SensorReading.patient_id == patient_id
    ).order_by(models.SensorReading.recorded_at.desc()).limit(limit).all()
    
    if not readings:
        raise HTTPException(status_code=404, detail="No sensor readings found for this patient")
    
    return readings

@app.get("/api/sensor/statistics/{patient_id}", response_model=schemas.ReadingStatistics)
def get_sensor_statistics(
    patient_id: int,
    minutes: int = 5,
    token: str = Depends(oauth2_scheme)
):
    stats = sensor_processor.get_reading_statistics(minutes=minutes)
    return schemas.ReadingStatistics(**stats)

@app.get("/api/sensor/alerts/{patient_id}", response_model=List[schemas.SensorAlertResponse])
def get_sensor_alerts(
    patient_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    alerts = db.query(models.SensorAlert).filter(
        models.SensorAlert.patient_id == patient_id
    ).order_by(models.SensorAlert.created_at.desc()).limit(limit).all()
    
    return alerts

@app.get("/api/sensor/alerts/recent/{minutes}", response_model=List[dict])
def get_recent_alerts(minutes: int = 5, token: str = Depends(oauth2_scheme)):
    return sensor_processor.get_recent_alerts(minutes=minutes)

@app.put("/api/sensor/alerts/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    personnel_id: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    alert = db.query(models.SensorAlert).filter(models.SensorAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_acknowledged = 1
    alert.acknowledged_by = personnel_id
    alert.acknowledged_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return {"status": "acknowledged", "alert_id": alert_id}

@app.get("/api/sensor/patient-status/{patient_id}", response_model=schemas.PatientStatusResponse)
def get_patient_sensor_status(
    patient_id: int,
    token: str = Depends(oauth2_scheme)
):
    status = sensor_processor.check_patient_status()
    return schemas.PatientStatusResponse(**status)

# ==========================================
# ENDPOINT 6: LIVE AI Paramedic Assist
# ==========================================
class ChatMessage(BaseModel):
    message: str

@app.post("/api/chat")
def ai_assist_chat(chat: ChatMessage, token: str = Depends(oauth2_scheme)):
    if not gemini_client:
        return {"response": "SYSTEM ERROR: API Key missing or invalid."}
    
    system_prompt = f"""
    You are the Exobios AI Core, an advanced paramedic field assistant. 
    A field paramedic is asking you a question. Provide a highly concise, professional, and medically accurate response. 
    Keep your answer under 3 sentences so it fits perfectly on a rugged tablet screen. 
    
    Paramedic Query: {chat.message}
    """
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=system_prompt
        )
        ai_response = response.text
    except Exception as e:
        ai_response = f"Error communicating with AI Core: {str(e)}"
    return {"response": ai_response}

# ==========================================
# ENDPOINT 7: Health Prediction & Risk Assessment
# ==========================================

@app.post("/api/predict/health", response_model=schemas.HealthPredictionResponse)
def predict_health_risk(
    prediction_data: schemas.HealthPredictionRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        assessment = prediction_model.comprehensive_health_assessment(
            age=prediction_data.age, sex=prediction_data.sex, heart_rate=prediction_data.heart_rate,
            systolic_bp=prediction_data.systolic_bp, diastolic_bp=prediction_data.diastolic_bp,
            spo2=prediction_data.spo2, temperature=prediction_data.temperature,
            symptoms=prediction_data.symptoms, medical_history=prediction_data.medical_history
        )
        priority_level, color = prediction_model.get_priority_level(assessment["overall_risk_score"])
        
        ai_insights = None
        ai_recommendations = None
        
        if gemini_client:
            try:
                critical_summary = "; ".join(assessment["critical_factors"]) if assessment["critical_factors"] else "Stable vitals"
                ai_prompt = f"""
                Based on this medical assessment, provide a brief clinical insight:
                Patient: {prediction_data.age} yo {prediction_data.sex}
                Overall Risk: {assessment['overall_category']} ({assessment['overall_risk_score']}/100)
                Priority: {priority_level}
                Critical Factors: {critical_summary}
                Vital Signs: HR={prediction_data.heart_rate}, BP={prediction_data.systolic_bp}/{prediction_data.diastolic_bp}, SpO2={prediction_data.spo2}%, Temp={prediction_data.temperature}°C
                Provide: 1. One-line clinical insight (max 20 words) 2. Two immediate recommendations for paramedic care
                """
                gemini_response = gemini_client.models.generate_content(model='gemini-2.5-flash', contents=ai_prompt)
                lines = gemini_response.text.split('\n')
                ai_insights = lines[0] if lines else "Assessment complete"
                ai_recommendations = "\n".join(lines[1:]) if len(lines) > 1 else "Follow standard protocol"
            except Exception as e:
                ai_insights = "AI analysis unavailable"
                ai_recommendations = "Follow standard protocol"
        
        critical_factors_str = ", ".join(assessment["critical_factors"]) if assessment["critical_factors"] else "None"
        individual_assessments = assessment["individual_assessments"]
        
        db_prediction = models.HealthPrediction(
            patient_id=prediction_data.patient_id, overall_risk_score=assessment["overall_risk_score"],
            overall_category=assessment["overall_category"], priority_level=priority_level,
            cardiovascular_risk=individual_assessments[0]["score"], stroke_risk=individual_assessments[1]["score"],
            hypoxia_risk=individual_assessments[2]["score"], fever_risk=individual_assessments[3]["score"],
            heart_rate=prediction_data.heart_rate, systolic_bp=prediction_data.systolic_bp,
            diastolic_bp=prediction_data.diastolic_bp, spo2=prediction_data.spo2, temperature=prediction_data.temperature,
            critical_factors=critical_factors_str, ai_insights=ai_insights, ai_recommendations=ai_recommendations
        )
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        return db_prediction
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.get("/api/predict/history/{patient_id}", response_model=list[schemas.HealthPredictionResponse])
def get_prediction_history(patient_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    predictions = db.query(models.HealthPrediction).filter(models.HealthPrediction.patient_id == patient_id).order_by(models.HealthPrediction.created_at.desc()).all()
    if not predictions:
        raise HTTPException(status_code=404, detail="No predictions found for this patient")
    return predictions

@app.get("/api/predict/latest/{patient_id}", response_model=schemas.HealthPredictionResponse)
def get_latest_prediction(patient_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    prediction = db.query(models.HealthPrediction).filter(models.HealthPrediction.patient_id == patient_id).order_by(models.HealthPrediction.created_at.desc()).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="No predictions found for this patient")
    return prediction

@app.post("/api/predict/risk-factors")
def analyze_risk_factors(prediction_data: schemas.HealthPredictionRequest, token: str = Depends(oauth2_scheme)):
    assessment = prediction_model.comprehensive_health_assessment(
        age=prediction_data.age, sex=prediction_data.sex, heart_rate=prediction_data.heart_rate,
        systolic_bp=prediction_data.systolic_bp, diastolic_bp=prediction_data.diastolic_bp,
        spo2=prediction_data.spo2, temperature=prediction_data.temperature,
        symptoms=prediction_data.symptoms, medical_history=prediction_data.medical_history
    )
    priority_level, color = prediction_model.get_priority_level(assessment["overall_risk_score"])
    assessment["priority_level"] = priority_level
    assessment["priority_color"] = color
    return assessment

@app.get("/api/predict/quick-triage")
def quick_triage_assessment(heart_rate: int, systolic_bp: int, diastolic_bp: int, spo2: int, temperature: float, age: int = 45, token: str = Depends(oauth2_scheme)):
    risk_score = 0
    alerts = []
    if spo2 < 90: risk_score += 30; alerts.append(f"CRITICAL: Severe hypoxia (SpO2 {spo2}%)")
    elif spo2 < 95: risk_score += 15; alerts.append(f"HIGH: Low oxygen (SpO2 {spo2}%)")
    if heart_rate > 120: risk_score += 15; alerts.append(f"HIGH: Tachycardia ({heart_rate} bpm)")
    elif heart_rate < 40: risk_score += 20; alerts.append(f"CRITICAL: Severe bradycardia ({heart_rate} bpm)")
    if systolic_bp >= 180: risk_score += 20; alerts.append(f"CRITICAL: Hypertensive crisis ({systolic_bp}/{diastolic_bp})")
    elif systolic_bp >= 140: risk_score += 10; alerts.append(f"HIGH: Stage 2 hypertension ({systolic_bp}/{diastolic_bp})")
    if temperature > 39: risk_score += 10; alerts.append(f"HIGH: Severe fever ({temperature}°C)")
    elif temperature < 35: risk_score += 15; alerts.append(f"HIGH: Hypothermia ({temperature}°C)")
    risk_score = min(100, risk_score)
    priority_level, color = prediction_model.get_priority_level(risk_score)
    return {
        "risk_score": risk_score, "priority_level": priority_level, "priority_color": color, "alerts": alerts,
        "vital_signs": {"heart_rate": heart_rate, "systolic_bp": systolic_bp, "diastolic_bp": diastolic_bp, "spo2": spo2, "temperature": temperature}
    }

# ==========================================
# TIME-SERIES TREND ANALYSIS ENDPOINTS
# ==========================================
@app.get("/api/trends/{patient_id}/{hours}", response_model=schemas.MultiVitalTrendResponse)
def get_patient_trends(patient_id: int, hours: int = 24, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    cutoff_time = datetime.now() - timedelta(hours=hours)
    readings = db.query(models.SensorReading).filter(models.SensorReading.patient_id == patient_id, models.SensorReading.recorded_at >= cutoff_time).order_by(models.SensorReading.recorded_at).all()
    if not readings: raise HTTPException(status_code=404, detail="No readings available for this period")
    readings_data = [{"timestamp": r.recorded_at, "vital": vital_name, "value": getattr(r, vital_name)} for r in readings for vital_name in ["heart_rate", "spo2", "temperature", "systolic_bp", "diastolic_bp", "respiratory_rate"] if getattr(r, vital_name) is not None]
    return trend_analyzer.get_multi_vital_trend(readings_data, hours=hours)

@app.get("/api/trends/vital/{patient_id}/{vital_name}/{hours}", response_model=schemas.VitalTrendResponse)
def get_vital_trend_detail(patient_id: int, vital_name: str, hours: int = 24, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    cutoff_time = datetime.now() - timedelta(hours=hours)
    readings = db.query(models.SensorReading).filter(models.SensorReading.patient_id == patient_id, models.SensorReading.recorded_at >= cutoff_time).order_by(models.SensorReading.recorded_at).all()
    if not readings: raise HTTPException(status_code=404, detail="No readings available")
    readings_data = [{"timestamp": r.recorded_at, "vital": vital_name, "value": getattr(r, vital_name)} for r in readings if hasattr(r, vital_name) and getattr(r, vital_name) is not None]
    trend = trend_analyzer.get_trend_analysis(readings_data, vital_name, hours=hours)
    if "error" in trend: raise HTTPException(status_code=404, detail=trend["error"])
    return trend

# ==========================================
# SEPSIS RISK ASSESSMENT ENDPOINTS
# ==========================================
@app.post("/api/sepsis/assess", response_model=schemas.SepsisProbabilityResponse)
def assess_sepsis_risk(patient_id: int, vitals: dict, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    sepsis_result = sepsis_calculator.calculate_sepsis_probability(vitals)
    try:
        sepsis_log = models.SepsisRiskLog(
            patient_id=patient_id, qsofa_score=sepsis_result["qsofa_score"], sofa_score=sepsis_result["sofa_score"],
            sepsis_probability=sepsis_result["sepsis_probability_percent"], risk_level=sepsis_result["risk_level"],
            clinical_recommendation=sepsis_result["clinical_recommendation"], temperature=vitals.get("temperature"),
            heart_rate=vitals.get("heart_rate"), respiratory_rate=vitals.get("respiratory_rate"), systolic_bp=vitals.get("systolic_bp"),
            diastolic_bp=vitals.get("diastolic_bp"), spo2=vitals.get("spo2"), indicators_data=json.dumps(sepsis_result["indicators"]), assessment_time=datetime.now()
        )
        db.add(sepsis_log)
        db.commit()
    except Exception as e: print(f"Error storing sepsis log: {e}")
    
    if sepsis_result["risk_level"] in ["HIGH", "CRITICAL"]:
        device_tokens = notification_manager.get_active_device_tokens(patient_id, db, models)
        if device_tokens:
            notification_manager.send_critical_alert(patient_id, {"level": "SEPSIS_WARNING", "message": f"SEPSIS RISK: {sepsis_result['sepsis_probability_percent']}% - {sepsis_result['clinical_recommendation']}", "vital": "Multi-vital", "value": sepsis_result["sepsis_probability_percent"], "range": [0, 50]}, device_tokens)
    return sepsis_result

@app.get("/api/sepsis/history/{patient_id}", response_model=List[schemas.SepsisProbabilityResponse])
def get_sepsis_history(patient_id: int, days: int = 7, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    cutoff_time = datetime.now() - timedelta(days=days)
    logs = db.query(models.SepsisRiskLog).filter(models.SepsisRiskLog.patient_id == patient_id, models.SepsisRiskLog.created_at >= cutoff_time).order_by(models.SepsisRiskLog.created_at.desc()).all()
    results = []
    for log in logs:
        indicators = json.loads(log.indicators_data) if log.indicators_data else []
        results.append({ "sepsis_probability_percent": log.sepsis_probability, "risk_level": log.risk_level, "indicators": indicators, "sofa_score": log.sofa_score, "qsofa_score": log.qsofa_score, "clinical_recommendation": log.clinical_recommendation })
    return results

# ==========================================
# FIREBASE MOBILE NOTIFICATIONS ENDPOINTS
# ==========================================
@app.post("/api/notifications/register-device", response_model=schemas.DeviceTokenResponse)
def register_device_for_notifications(patient_id: int, device_data: schemas.DeviceTokenRequest, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    result = notification_manager.register_device_token(patient_id, device_data.device_token, device_data.device_type, db, models)
    if result["status"] == "error": raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.delete("/api/notifications/deregister-device/{device_token}", response_model=schemas.DeviceTokenResponse)
def deregister_device(device_token: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    result = notification_manager.deregister_device_token(device_token, db, models)
    if result["status"] == "error": raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/api/notifications/devices/{patient_id}")
def get_patient_devices(patient_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    devices = db.query(models.DeviceToken).filter(models.DeviceToken.patient_id == patient_id, models.DeviceToken.is_active == 1).all()
    return {"patient_id": patient_id, "device_count": len(devices), "devices": [{"id": d.id, "device_type": d.device_type, "device_model": d.device_model, "registered_at": d.registered_at.isoformat(), "last_used": d.last_used.isoformat() if d.last_used else None} for d in devices]}

@app.get("/api/notifications/history/{patient_id}", response_model=List[schemas.NotificationLogResponse])
def get_notification_history(patient_id: int, limit: int = 50, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    logs = db.query(models.NotificationLog).filter(models.NotificationLog.patient_id == patient_id).order_by(models.NotificationLog.created_at.desc()).limit(limit).all()
    return logs


# ==========================================
# ENDPOINT 8: PUBLIC EMERGENCY INTAKE (NEW)
# ==========================================
@app.post("/api/intake/submit", response_model=schemas.SelfReportedIntakeResponse)
def submit_patient_intake(intake: schemas.SelfReportedIntakeCreate, db: Session = Depends(get_db)):
    """Public endpoint for patients to self-report an incoming emergency."""
    new_intake = models.SelfReportedIntake(**intake.model_dump())
    db.add(new_intake)
    db.commit()
    db.refresh(new_intake)

    # Automatically send confirmation email to patient
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    if sender_email and sender_password and sender_email != "your_actual_email@gmail.com":
        try:
            msg = MIMEText(f"Dear {intake.name},\n\nYour emergency alert has been received by Exobios Clinical Command Center.\n\nReported Symptoms: {intake.symptoms}\n\nPlease proceed safely to the hospital or call emergency services (911/112) immediately if your condition is life-threatening.")
            msg['Subject'] = "Exobios Emergency Alert Received"
            msg['From'] = f"Exobios Triage <{sender_email}>"
            msg['To'] = intake.email
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send patient intake confirmation email: {e}")
            
    return new_intake

@app.get("/api/intake/pending", response_model=List[schemas.SelfReportedIntakeResponse])
def get_pending_intakes(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Secure endpoint for Dashboard to fetch active un-acknowledged incoming emergencies."""
    intakes = db.query(models.SelfReportedIntake).filter(models.SelfReportedIntake.status == "PENDING").order_by(models.SelfReportedIntake.created_at.desc()).all()
    return intakes

@app.post("/api/intake/{intake_id}/acknowledge", response_model=schemas.SelfReportedIntakeResponse)
def acknowledge_intake(intake_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Secure endpoint for Command Center to acknowledge and email the patient."""
    intake = db.query(models.SelfReportedIntake).filter(models.SelfReportedIntake.id == intake_id).first()
    if not intake:
        raise HTTPException(status_code=404, detail="Intake record not found")
        
    intake.status = "ACKNOWLEDGED"
    db.commit()
    db.refresh(intake)
    
    # Automatically send 'Ready' email to patient
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    if sender_email and sender_password and sender_email != "your_actual_email@gmail.com":
        try:
            msg = MIMEText(f"Dear {intake.name},\n\nThe medical team has acknowledged your emergency status and is actively preparing for your arrival.\n\nStatus: ACKNOWLEDGED.")
            msg['Subject'] = "Exobios Triage - Preparation Initiated"
            msg['From'] = f"Exobios Triage <{sender_email}>"
            msg['To'] = intake.email
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send patient ack email: {e}")
            
    return intake