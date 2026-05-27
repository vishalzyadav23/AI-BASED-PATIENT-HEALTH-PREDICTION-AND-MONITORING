# backend/models.py
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    
    # NEW: PostgreSQL Profile Fields
    phone = Column(String, nullable=True)          
    pin_code = Column(String, nullable=True)       
    area_location = Column(String, nullable=True)  
    region = Column(String, nullable=True)         
    
    role = Column(String, default="Paramedic")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    sex = Column(String)
    abha_id = Column(String, nullable=True)
    
    # Medical History & Assessment
    past_history = Column(Text, nullable=True)
    current_medications = Column(Text, nullable=True)
    reported_symptoms = Column(Text, nullable=True)
    observed_signs = Column(Text, nullable=True)


class HealthPrediction(Base):
    __tablename__ = "health_predictions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    
    # Overall Risk Assessment
    overall_risk_score = Column(Integer, nullable=False)
    overall_category = Column(String, nullable=False)  # STABLE, MONITOR, ALERT, CRITICAL
    priority_level = Column(String, nullable=False)  # RESUSCITATION, EMERGENT, URGENT, SEMI-URGENT, NON-URGENT
    
    # Individual Risk Assessments (JSON stored as Text)
    cardiovascular_risk = Column(Integer, nullable=False)
    stroke_risk = Column(Integer, nullable=False)
    hypoxia_risk = Column(Integer, nullable=False)
    fever_risk = Column(Integer, nullable=False)
    
    # Vital Signs at time of prediction
    heart_rate = Column(Integer, nullable=True)
    systolic_bp = Column(Integer, nullable=True)
    diastolic_bp = Column(Integer, nullable=True)
    spo2 = Column(Integer, nullable=True)
    temperature = Column(Float, nullable=True)
    
    # Critical Factors (comma-separated)
    critical_factors = Column(Text, nullable=True)
    
    # AI Insights from Gemini
    ai_insights = Column(Text, nullable=True)
    ai_recommendations = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    
    # Vital Signs
    heart_rate = Column(Integer, nullable=False)
    spo2 = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    systolic_bp = Column(Integer, nullable=True)
    diastolic_bp = Column(Integer, nullable=True)
    respiratory_rate = Column(Integer, nullable=True)
    
    # Data Quality & Validation
    is_valid = Column(Integer, default=1)  # 1 = valid, 0 = invalid
    validation_errors = Column(Text, nullable=True)
    
    # Anomaly Detection
    has_anomalies = Column(Integer, default=0)  # 1 = has anomalies, 0 = normal
    anomalies = Column(Text, nullable=True)  # JSON string of detected anomalies
    
    # Timestamp
    recorded_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SensorAlert(Base):
    __tablename__ = "sensor_alerts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    sensor_reading_id = Column(Integer, nullable=True)
    
    # Alert Details
    alert_level = Column(String, nullable=False)  # INFO, WARNING, CRITICAL
    message = Column(Text, nullable=False)
    affected_vital = Column(String, nullable=False)
    reading_value = Column(Float, nullable=False)
    normal_range_min = Column(Float, nullable=True)
    normal_range_max = Column(Float, nullable=True)
    anomaly_type = Column(String, nullable=True)  # out_of_range, rapid_change, flatline, spike
    
    # Alert Status
    is_acknowledged = Column(Integer, default=0)
    acknowledged_by = Column(String, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)


class DeviceToken(Base):
    """Store mobile device tokens for push notifications"""
    __tablename__ = "device_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    device_token = Column(String, unique=True, nullable=False, index=True)
    device_type = Column(String, nullable=False)  # iOS, Android, Web
    device_model = Column(String, nullable=True)
    is_active = Column(Integer, default=1)
    
    # Timestamps
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    deregistered_at = Column(DateTime, nullable=True)


class NotificationLog(Base):
    """Log all sent notifications for audit trail"""
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    device_token_id = Column(Integer, nullable=True)
    
    # Notification Details
    notification_type = Column(String, nullable=False)  # CRITICAL_ALERT, ANOMALY, UNREVIEWED_ALERT, SEPSIS_WARNING
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    data_payload = Column(Text, nullable=True)  # JSON
    
    # Alert Reference
    alert_id = Column(Integer, nullable=True)
    sensor_reading_id = Column(Integer, nullable=True)
    
    # Delivery Status
    send_status = Column(String, nullable=False)  # SENT, FAILED, SIMULATED
    sent_to_devices = Column(Integer, nullable=True)
    failed_devices = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)


class SepsisRiskLog(Base):
    """Log sepsis risk assessments for tracking"""
    __tablename__ = "sepsis_risk_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    
    # Sepsis Scores
    qsofa_score = Column(Integer, nullable=False)
    sofa_score = Column(Integer, nullable=False)
    sepsis_probability = Column(Float, nullable=False)
    
    # Risk Level
    risk_level = Column(String, nullable=False)  # LOW, MILD, MODERATE, HIGH, CRITICAL
    clinical_recommendation = Column(Text, nullable=False)
    
    # Vital Signs at Assessment
    temperature = Column(Float, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    respiratory_rate = Column(Integer, nullable=True)
    systolic_bp = Column(Integer, nullable=True)
    diastolic_bp = Column(Integer, nullable=True)
    spo2 = Column(Integer, nullable=True)
    
    # Indicators (JSON)
    indicators_data = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    assessment_time = Column(DateTime, nullable=False)

# ==========================================
# NEW: PUBLIC SELF-REPORTING SYSTEM
# ==========================================
class SelfReportedIntake(Base):
    """Store incoming emergency requests from the public facing UI"""
    __tablename__ = "self_reported_intakes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    symptoms = Column(Text, nullable=False)
    
    # GPS Coordinates for ETA calculation
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Workflow tracking: PENDING, ACKNOWLEDGED, REDIRECTED
    status = Column(String, default="PENDING") 
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)