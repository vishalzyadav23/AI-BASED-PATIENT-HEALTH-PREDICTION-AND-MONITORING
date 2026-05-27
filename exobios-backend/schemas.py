# backend/schemas.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Union
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    personnel_id: Optional[str] = None

# --- User/Paramedic Schemas ---
class UserBase(BaseModel):
    personnel_id: str
    name: str
    # NEW: Progressive Profiling Fields
    phone: Optional[str] = None
    pin_code: Optional[str] = None
    area_location: Optional[str] = None
    region: Optional[str] = None
    
    role: Optional[str] = "Paramedic"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True

# --- Patient Schemas ---
class PatientBase(BaseModel):
    name: str
    age: int
    sex: str
    abha_id: Optional[str] = None
    past_history: Optional[str] = None
    current_medications: Optional[str] = None
    reported_symptoms: Optional[str] = None
    observed_signs: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int

    class Config:
        from_attributes = True


# --- Health Prediction Schemas ---
class RiskAssessment(BaseModel):
    score: int
    category: str
    risk_factors: List[str]
    condition: str


class HealthPredictionRequest(BaseModel):
    patient_id: int
    age: int
    sex: str
    heart_rate: int
    systolic_bp: int
    diastolic_bp: int
    spo2: int
    temperature: float
    symptoms: Optional[str] = ""
    medical_history: Optional[str] = ""


class HealthPredictionResponse(BaseModel):
    id: int
    patient_id: int
    overall_risk_score: int
    overall_category: str  # STABLE, MONITOR, ALERT, CRITICAL
    priority_level: str  # RESUSCITATION, EMERGENT, URGENT, SEMI-URGENT, NON-URGENT
    
    cardiovascular_risk: int
    stroke_risk: int
    hypoxia_risk: int
    fever_risk: int
    
    heart_rate: Optional[int]
    systolic_bp: Optional[int]
    diastolic_bp: Optional[int]
    spo2: Optional[int]
    temperature: Optional[float]
    
    critical_factors: Optional[str]
    ai_insights: Optional[str]
    ai_recommendations: Optional[str]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ComprehensiveAssessment(BaseModel):
    timestamp: str
    overall_risk_score: int
    overall_category: str
    individual_assessments: List[RiskAssessment]
    critical_factors: List[str]
    vital_signs: dict
    patient_info: dict
    priority_level: Optional[str] = None
    ai_insights: Optional[str] = None


# --- Sensor Data Schemas ---
class SensorReadingCreate(BaseModel):
    patient_id: int
    heart_rate: int
    spo2: int
    temperature: float
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    respiratory_rate: Optional[int] = None


class SensorReadingResponse(BaseModel):
    id: int
    patient_id: int
    heart_rate: int
    spo2: int
    temperature: float
    systolic_bp: Optional[int]
    diastolic_bp: Optional[int]
    respiratory_rate: Optional[int]
    is_valid: int
    validation_errors: Optional[str]
    has_anomalies: int
    anomalies: Optional[str]
    recorded_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class SensorAlertResponse(BaseModel):
    id: int
    patient_id: int
    sensor_reading_id: Optional[int]
    alert_level: str  # INFO, WARNING, CRITICAL
    message: str
    affected_vital: str
    reading_value: float
    normal_range_min: Optional[float]
    normal_range_max: Optional[float]
    anomaly_type: Optional[str]
    is_acknowledged: int
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SensorProcessingResult(BaseModel):
    status: str
    timestamp: str
    valid: bool
    errors: List[str]
    warnings: List[str]
    alerts: List[dict]
    processed_data: Optional[dict]


class PatientStatusResponse(BaseModel):
    status: str  # STABLE, WARNING, CRITICAL, NO_DATA
    critical_alerts: int
    warning_alerts: int
    current_reading: Optional[dict]
    recent_alerts: List[dict]


class ReadingStatistics(BaseModel):
    reading_count: int
    timeframe_minutes: int
    heart_rate: dict
    spo2: dict
    temperature: dict
    timestamp: str


# ========================================
# TIME-SERIES TREND ANALYSIS SCHEMAS
# ========================================

class TrendAlert(BaseModel):
    type: str
    severity: str
    message: str


class ForecastData(BaseModel):
    predictions: List[float]
    upper: List[float]
    lower: List[float]
    confidence: float


class VitalTrendResponse(BaseModel):
    vital: str
    period_hours: int
    data_points: int
    mean: float
    std_dev: float
    min: float
    max: float
    slope: float
    trend: str  # INCREASING, DECREASING, STABLE
    trend_severity: str
    volatility: float
    volatility_level: str
    rate_of_change_percent: float
    forecast_next_6: List[float]
    forecast_upper_bound: List[float]
    forecast_lower_bound: List[float]
    forecast_confidence: float
    clinical_alert: Union[dict, List[dict]]


class MultiVitalTrendResponse(BaseModel):
    period_hours: int
    analysis_timestamp: str
    vital_trends: Dict[str, VitalTrendResponse]
    overall_status: str  # STABLE, WARNING, CRITICAL


# ========================================
# SEPSIS RISK ASSESSMENT SCHEMAS
# ========================================

class SOFAComponent(BaseModel):
    respiratory: int
    coagulation: int
    hepatic: int
    cardiovascular: int
    cns: int
    renal: int
    total: int


class QSOFACriteria(BaseModel):
    criterion: str
    present: bool
    value: float


class QSOFAResponse(BaseModel):
    total: int
    criteria: List[QSOFACriteria]
    risk_level: str


class SepsisIndicator(BaseModel):
    indicator: str
    value: float
    weight: int
    contribution: Optional[float] = None
    status: Optional[str] = None
    risk: Optional[str] = None


class SepsisProbabilityResponse(BaseModel):
    sepsis_probability_percent: float
    risk_level: str  # LOW, MILD, MODERATE, HIGH, CRITICAL
    indicators: List[SepsisIndicator]
    sofa_score: int
    qsofa_score: int
    clinical_recommendation: str


# ========================================
# FIREBASE MOBILE NOTIFICATIONS SCHEMAS
# ========================================

class DeviceTokenRequest(BaseModel):
    device_token: str
    device_type: str  # iOS, Android, Web
    device_model: Optional[str] = None


class DeviceTokenResponse(BaseModel):
    status: str
    message: str
    device_id: Optional[int] = None


class NotificationResponse(BaseModel):
    status: str  # success, error, simulated, warning
    message: str
    sent_count: int
    failed_count: Optional[int] = None
    notification: Optional[dict] = None


class NotificationLogResponse(BaseModel):
    id: int
    patient_id: int
    notification_type: str
    title: str
    message: str
    send_status: str
    sent_to_devices: Optional[int]
    created_at: datetime
    sent_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ========================================
# PUBLIC EMERGENCY INTAKE SCHEMAS (NEW)
# ========================================

class SelfReportedIntakeCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    symptoms: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class SelfReportedIntakeResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    symptoms: str
    latitude: Optional[float]
    longitude: Optional[float]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True