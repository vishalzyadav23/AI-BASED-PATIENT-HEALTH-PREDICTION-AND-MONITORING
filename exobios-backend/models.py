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


# ==========================================
# NEW: PATIENT MANAGEMENT SYSTEM
# ==========================================

class PatientMedicalHistory(Base):
    """Detailed medical history and pre-existing conditions for each patient"""
    __tablename__ = "patient_medical_history"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    
    # Chronic Conditions (comma-separated or JSON)
    chronic_conditions = Column(Text, nullable=True)  # e.g., "Diabetes, Hypertension, Asthma"
    
    # Allergies & Intolerances
    allergies = Column(Text, nullable=True)  # e.g., "Penicillin, Peanuts"
    
    # Previous Surgeries
    previous_surgeries = Column(Text, nullable=True)  # e.g., "Appendectomy (2015), Knee Surgery (2020)"
    
    # Family History (genetic risk factors)
    family_history = Column(Text, nullable=True)  # e.g., "Heart disease (Father), Diabetes (Mother)"
    
    # Current Medications (more detailed than Patient table)
    medications = Column(Text, nullable=True)  # JSON format recommended
    
    # Immunization Status
    immunization_status = Column(Text, nullable=True)  # e.g., "COVID-19 (2x), Flu (Yes)"
    
    # Blood Type
    blood_type = Column(String, nullable=True)  # O+, A-, etc.
    
    # Height & Weight (for BMI calculation)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    
    # Lifestyle Information
    smoking_status = Column(String, nullable=True)  # Never, Former, Current
    alcohol_consumption = Column(String, nullable=True)  # Never, Occasional, Regular, Heavy
    
    # Notes from healthcare provider
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmergencyContact(Base):
    """Emergency contact information for patients"""
    __tablename__ = "emergency_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    
    # Contact Information
    name = Column(String, nullable=False)
    relationship = Column(String, nullable=False)  # Father, Mother, Spouse, Sibling, Friend, Other
    phone_primary = Column(String, nullable=False)
    phone_secondary = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # Address Information
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pin_code = Column(String, nullable=True)
    
    # Priority Level
    priority = Column(Integer, default=1)  # 1 = Primary, 2 = Secondary, 3 = Tertiary
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Caregiver(Base):
    """Family members and caregivers who can access patient data"""
    __tablename__ = "caregivers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User Information (similar to User model)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    
    # Relationship to patient(s)
    # Note: Relationship to specific patient stored in PatientAccess table
    
    # Caregiver Type
    caregiver_type = Column(String, nullable=False)  # Family, Professional, Friend, Other
    
    # Contact Information
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pin_code = Column(String, nullable=True)
    
    # Account Status
    is_active = Column(Integer, default=1)  # 1 = Active, 0 = Inactive/Blocked
    
    # Verification
    is_verified = Column(Integer, default=0)  # 1 = Email verified, 0 = Not verified
    verification_token = Column(String, nullable=True)
    verification_token_expires_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PatientAccess(Base):
    """Relationship between caregivers and patients they can access"""
    __tablename__ = "patient_access"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    caregiver_id = Column(Integer, nullable=False, index=True)
    
    # Relationship (to the patient)
    relationship = Column(String, nullable=False)  # Mother, Father, Spouse, Child, Doctor, Nurse, etc.
    
    # Permission Level
    permission_level = Column(String, default="VIEW")  # VIEW (read-only), MANAGE (can update), EDIT_ALERTS (can manage alerts)
    
    # Can this caregiver receive alerts?
    can_receive_alerts = Column(Integer, default=1)  # 1 = Yes, 0 = No
    
    # Can this caregiver view sensitive data? (medications, allergies, etc.)
    can_view_sensitive_data = Column(Integer, default=1)  # 1 = Yes, 0 = No
    
    # Access Status
    is_active = Column(Integer, default=1)  # 1 = Active, 0 = Revoked
    
    # Who approved this access?
    approved_by = Column(String, nullable=True)  # Patient email or Paramedic ID
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)