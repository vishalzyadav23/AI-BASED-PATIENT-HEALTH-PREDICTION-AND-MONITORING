# backend/patient_management.py
"""
Patient Management Module - Handles patient profiles, medical history, emergency contacts, and caregiver access
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import models
import schemas
import security
from database import get_db

router = APIRouter(prefix="/api", tags=["Patient Management"])

# ==========================================
# CAREGIVER AUTHENTICATION ENDPOINTS
# ==========================================

class CaregiverLoginRequest(BaseModel):
    email: str
    password: str

class CaregiverRegisterRequest(BaseModel):
    email: str
    name: str
    password: str
    phone: Optional[str] = None
    caregiver_type: str = "Family"  # Family, Professional, Friend, Other

@router.post("/caregivers/register", response_model=schemas.CaregiverResponse)
def register_caregiver(request: CaregiverRegisterRequest, db: Session = Depends(get_db)):
    """Register a new caregiver account"""
    
    # Check if caregiver already exists
    existing = db.query(models.Caregiver).filter(
        models.Caregiver.email == request.email
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new caregiver
    hashed_password = security.get_password_hash(request.password)
    caregiver = models.Caregiver(
        email=request.email,
        name=request.name,
        phone=request.phone,
        hashed_password=hashed_password,
        caregiver_type=request.caregiver_type,
        is_active=1,
        is_verified=1  # Auto-verified for now
    )
    
    db.add(caregiver)
    db.commit()
    db.refresh(caregiver)
    
    return caregiver

@router.post("/caregivers/login", response_model=schemas.Token)
def login_caregiver(request: CaregiverLoginRequest, db: Session = Depends(get_db)):
    """Login caregiver and return JWT token"""
    
    caregiver = db.query(models.Caregiver).filter(
        models.Caregiver.email == request.email
    ).first()
    
    if not caregiver or not security.verify_password(request.password, caregiver.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not caregiver.is_active:
        raise HTTPException(status_code=403, detail="Caregiver account is inactive")
    
    # Create JWT token using email as subject
    access_token = security.create_access_token(data={"sub": caregiver.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_current_user(token: str, db: Session) -> models.User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = security.verify_access_token(token)
    if payload is None:
        raise credentials_exception
    personnel_id: str = payload.get("sub")
    if personnel_id is None:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.personnel_id == personnel_id).first()
    if user is None:
        raise credentials_exception
    return user

def check_patient_access(patient_id: int, current_user_id: int, db: Session, is_caregiver: bool = False):
    """Check if user has access to patient data"""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    if is_caregiver:
        # Check if caregiver has access to this patient
        access = db.query(models.PatientAccess).filter(
            models.PatientAccess.patient_id == patient_id,
            models.PatientAccess.caregiver_id == current_user_id,
            models.PatientAccess.is_active == 1
        ).first()
        if not access:
            raise HTTPException(status_code=403, detail="You do not have access to this patient")
        return access
    
    return patient


# ==========================================
# PATIENT PROFILE ENDPOINTS
# ==========================================

@router.post("/patients", response_model=schemas.PatientResponse)
def create_patient(
    patient: schemas.PatientCreate,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Create a new patient record (Paramedic only)"""
    current_user = get_current_user(token, db)
    
    if current_user.role != "Paramedic":
        raise HTTPException(status_code=403, detail="Only Paramedics can create patients")
    
    db_patient = models.Patient(
        name=patient.name,
        age=patient.age,
        sex=patient.sex,
        abha_id=patient.abha_id,
        past_history=patient.past_history,
        current_medications=patient.current_medications,
        reported_symptoms=patient.reported_symptoms,
        observed_signs=patient.observed_signs
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.get("/patients/{patient_id}", response_model=schemas.PatientDetailedProfile)
def get_patient_profile(
    patient_id: int,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get complete patient profile with medical history and emergency contacts"""
    current_user = get_current_user(token, db)
    
    patient = check_patient_access(patient_id, current_user.id, db)
    
    # Get medical history
    medical_history = db.query(models.PatientMedicalHistory).filter(
        models.PatientMedicalHistory.patient_id == patient_id
    ).first()
    
    # Get emergency contacts
    emergency_contacts = db.query(models.EmergencyContact).filter(
        models.EmergencyContact.patient_id == patient_id
    ).order_by(models.EmergencyContact.priority).all()
    
    # Get caregivers with access
    caregivers_access = db.query(models.PatientAccess).filter(
        models.PatientAccess.patient_id == patient_id,
        models.PatientAccess.is_active == 1
    ).all()
    
    caregivers_list = []
    for access in caregivers_access:
        caregiver = db.query(models.Caregiver).filter(
            models.Caregiver.id == access.caregiver_id
        ).first()
        if caregiver:
            caregivers_list.append({
                "caregiver_id": caregiver.id,
                "name": caregiver.name,
                "email": caregiver.email,
                "relationship": access.relationship,
                "permission_level": access.permission_level,
                "can_receive_alerts": access.can_receive_alerts,
                "can_view_sensitive_data": access.can_view_sensitive_data
            })
    
    # Get latest health prediction
    latest_prediction = db.query(models.HealthPrediction).filter(
        models.HealthPrediction.patient_id == patient_id
    ).order_by(models.HealthPrediction.created_at.desc()).first()
    
    # Get latest sensor reading
    latest_reading = db.query(models.SensorReading).filter(
        models.SensorReading.patient_id == patient_id
    ).order_by(models.SensorReading.created_at.desc()).first()
    
    return schemas.PatientDetailedProfile(
        id=patient.id,
        name=patient.name,
        age=patient.age,
        sex=patient.sex,
        abha_id=patient.abha_id,
        medical_history=medical_history,
        emergency_contacts=emergency_contacts,
        caregivers=caregivers_list,
        latest_prediction=latest_prediction,
        latest_sensor_reading=latest_reading
    )


@router.get("/patients", response_model=List[schemas.PatientResponse])
def list_patients(
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """List all patients (Paramedics see all, Caregivers see only their patients)"""
    current_user = get_current_user(token, db)
    
    if current_user.role == "Paramedic":
        # Paramedics can see all patients
        patients = db.query(models.Patient).offset(skip).limit(limit).all()
    elif current_user.role == "Caregiver":
        # Caregivers can only see their assigned patients
        caregiver = db.query(models.Caregiver).filter(
            models.Caregiver.email == current_user.personnel_id
        ).first()
        if not caregiver:
            raise HTTPException(status_code=404, detail="Caregiver profile not found")
        
        patient_ids = db.query(models.PatientAccess.patient_id).filter(
            models.PatientAccess.caregiver_id == caregiver.id,
            models.PatientAccess.is_active == 1
        ).all()
        
        patient_ids = [p[0] for p in patient_ids]
        patients = db.query(models.Patient).filter(
            models.Patient.id.in_(patient_ids)
        ).offset(skip).limit(limit).all()
    else:
        raise HTTPException(status_code=403, detail="Invalid user role")
    
    return patients


# ==========================================
# MEDICAL HISTORY ENDPOINTS
# ==========================================

@router.post("/patients/{patient_id}/medical-history", response_model=schemas.PatientMedicalHistoryResponse)
def add_medical_history(
    patient_id: int,
    history: schemas.PatientMedicalHistoryCreate,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Add or update patient medical history"""
    current_user = get_current_user(token, db)
    patient = check_patient_access(patient_id, current_user.id, db)
    
    # Check if medical history already exists
    existing_history = db.query(models.PatientMedicalHistory).filter(
        models.PatientMedicalHistory.patient_id == patient_id
    ).first()
    
    if existing_history:
        # Update existing
        existing_history.chronic_conditions = history.chronic_conditions
        existing_history.allergies = history.allergies
        existing_history.previous_surgeries = history.previous_surgeries
        existing_history.family_history = history.family_history
        existing_history.medications = history.medications
        existing_history.immunization_status = history.immunization_status
        existing_history.blood_type = history.blood_type
        existing_history.height_cm = history.height_cm
        existing_history.weight_kg = history.weight_kg
        existing_history.smoking_status = history.smoking_status
        existing_history.alcohol_consumption = history.alcohol_consumption
        existing_history.notes = history.notes
        existing_history.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_history)
        return existing_history
    
    # Create new
    new_history = models.PatientMedicalHistory(
        patient_id=patient_id,
        chronic_conditions=history.chronic_conditions,
        allergies=history.allergies,
        previous_surgeries=history.previous_surgeries,
        family_history=history.family_history,
        medications=history.medications,
        immunization_status=history.immunization_status,
        blood_type=history.blood_type,
        height_cm=history.height_cm,
        weight_kg=history.weight_kg,
        smoking_status=history.smoking_status,
        alcohol_consumption=history.alcohol_consumption,
        notes=history.notes
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)
    return new_history


@router.get("/patients/{patient_id}/medical-history", response_model=schemas.PatientMedicalHistoryResponse)
def get_medical_history(
    patient_id: int,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get patient medical history"""
    current_user = get_current_user(token, db)
    patient = check_patient_access(patient_id, current_user.id, db)
    
    history = db.query(models.PatientMedicalHistory).filter(
        models.PatientMedicalHistory.patient_id == patient_id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="Medical history not found")
    
    return history


# ==========================================
# EMERGENCY CONTACT ENDPOINTS
# ==========================================

@router.post("/patients/{patient_id}/emergency-contacts", response_model=schemas.EmergencyContactResponse)
def add_emergency_contact(
    patient_id: int,
    contact: schemas.EmergencyContactCreate,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Add emergency contact for patient"""
    current_user = get_current_user(token, db)
    patient = check_patient_access(patient_id, current_user.id, db)
    
    new_contact = models.EmergencyContact(
        patient_id=patient_id,
        name=contact.name,
        relationship=contact.relationship,
        phone_primary=contact.phone_primary,
        phone_secondary=contact.phone_secondary,
        email=contact.email,
        address=contact.address,
        city=contact.city,
        state=contact.state,
        pin_code=contact.pin_code,
        priority=contact.priority,
        notes=contact.notes
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


@router.get("/patients/{patient_id}/emergency-contacts", response_model=List[schemas.EmergencyContactResponse])
def get_emergency_contacts(
    patient_id: int,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get all emergency contacts for patient"""
    current_user = get_current_user(token, db)
    patient = check_patient_access(patient_id, current_user.id, db)
    
    contacts = db.query(models.EmergencyContact).filter(
        models.EmergencyContact.patient_id == patient_id
    ).order_by(models.EmergencyContact.priority).all()
    
    return contacts


@router.put("/patients/emergency-contacts/{contact_id}", response_model=schemas.EmergencyContactResponse)
def update_emergency_contact(
    contact_id: int,
    contact_update: schemas.EmergencyContactBase,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Update emergency contact"""
    current_user = get_current_user(token, db)
    
    contact = db.query(models.EmergencyContact).filter(
        models.EmergencyContact.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Emergency contact not found")
    
    # Verify access to patient
    patient = check_patient_access(contact.patient_id, current_user.id, db)
    
    contact.name = contact_update.name
    contact.relationship = contact_update.relationship
    contact.phone_primary = contact_update.phone_primary
    contact.phone_secondary = contact_update.phone_secondary
    contact.email = contact_update.email
    contact.address = contact_update.address
    contact.city = contact_update.city
    contact.state = contact_update.state
    contact.pin_code = contact_update.pin_code
    contact.priority = contact_update.priority
    contact.notes = contact_update.notes
    contact.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/patients/emergency-contacts/{contact_id}")
def delete_emergency_contact(
    contact_id: int,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Delete emergency contact"""
    current_user = get_current_user(token, db)
    
    contact = db.query(models.EmergencyContact).filter(
        models.EmergencyContact.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Emergency contact not found")
    
    # Verify access to patient
    patient = check_patient_access(contact.patient_id, current_user.id, db)
    
    db.delete(contact)
    db.commit()
    
    return {"message": "Emergency contact deleted successfully"}


# ==========================================
# CAREGIVER & ACCESS MANAGEMENT ENDPOINTS
# ==========================================

@router.post("/patients/{patient_id}/invite-caregiver", response_model=schemas.InviteCaregiverResponse)
def invite_caregiver(
    patient_id: int,
    invitation: schemas.InviteCaregiverRequest,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Invite a caregiver to access patient data"""
    current_user = get_current_user(token, db)
    patient = check_patient_access(patient_id, current_user.id, db)
    
    # Check if caregiver already exists
    caregiver = db.query(models.Caregiver).filter(
        models.Caregiver.email == invitation.caregiver_email
    ).first()
    
    if not caregiver:
        # Create new caregiver account (without password yet)
        caregiver = models.Caregiver(
            email=invitation.caregiver_email,
            name=invitation.caregiver_email,  # Will be updated when they accept
            hashed_password="",  # Will be set during verification
            caregiver_type="Family",
            is_active=0,  # Inactive until they verify
            is_verified=0
        )
        db.add(caregiver)
        db.commit()
        db.refresh(caregiver)
    
    # Check if access already exists
    existing_access = db.query(models.PatientAccess).filter(
        models.PatientAccess.patient_id == patient_id,
        models.PatientAccess.caregiver_id == caregiver.id
    ).first()
    
    if existing_access and existing_access.is_active == 1:
        raise HTTPException(status_code=400, detail="This caregiver already has access to this patient")
    
    # Create or reactivate access
    if existing_access:
        existing_access.is_active = 1
        existing_access.relationship = invitation.relationship
        existing_access.can_receive_alerts = 1 if invitation.can_receive_alerts else 0
        existing_access.can_view_sensitive_data = 1 if invitation.can_view_sensitive_data else 0
        existing_access.created_at = datetime.utcnow()
        db.commit()
        access = existing_access
    else:
        access = models.PatientAccess(
            patient_id=patient_id,
            caregiver_id=caregiver.id,
            relationship=invitation.relationship,
            can_receive_alerts=1 if invitation.can_receive_alerts else 0,
            can_view_sensitive_data=1 if invitation.can_view_sensitive_data else 0,
            permission_level="VIEW",
            is_active=1,
            approved_by=current_user.personnel_id,
            approved_at=datetime.utcnow()
        )
        db.add(access)
        db.commit()
        db.refresh(access)
    
    return schemas.InviteCaregiverResponse(
        status="success",
        message=f"Invitation sent to {invitation.caregiver_email}",
        invitation_sent_to=invitation.caregiver_email,
        created_at=datetime.utcnow()
    )


@router.get("/patients/{patient_id}/caregivers", response_model=List[dict])
def get_patient_caregivers(
    patient_id: int,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get all caregivers with access to patient"""
    current_user = get_current_user(token, db)
    patient = check_patient_access(patient_id, current_user.id, db)
    
    caregivers_access = db.query(models.PatientAccess).filter(
        models.PatientAccess.patient_id == patient_id,
        models.PatientAccess.is_active == 1
    ).all()
    
    result = []
    for access in caregivers_access:
        caregiver = db.query(models.Caregiver).filter(
            models.Caregiver.id == access.caregiver_id
        ).first()
        if caregiver:
            result.append({
                "caregiver_id": caregiver.id,
                "name": caregiver.name,
                "email": caregiver.email,
                "phone": caregiver.phone,
                "relationship": access.relationship,
                "permission_level": access.permission_level,
                "can_receive_alerts": access.can_receive_alerts,
                "can_view_sensitive_data": access.can_view_sensitive_data,
                "created_at": access.created_at
            })
    
    return result


@router.delete("/patients/{patient_id}/caregivers/{caregiver_id}")
def revoke_caregiver_access(
    patient_id: int,
    caregiver_id: int,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Revoke caregiver access to patient"""
    current_user = get_current_user(token, db)
    patient = check_patient_access(patient_id, current_user.id, db)
    
    access = db.query(models.PatientAccess).filter(
        models.PatientAccess.patient_id == patient_id,
        models.PatientAccess.caregiver_id == caregiver_id
    ).first()
    
    if not access:
        raise HTTPException(status_code=404, detail="Caregiver access not found")
    
    access.is_active = 0
    access.revoked_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Caregiver access revoked successfully"}


# ==========================================
# CAREGIVER PORTAL ENDPOINTS
# ==========================================

@router.get("/caregiver/my-patients", response_model=List[schemas.CaregiverPatientOverview])
def caregiver_get_my_patients(
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get all patients assigned to caregiver"""
    current_user = get_current_user(token, db)
    
    # Find caregiver
    caregiver = db.query(models.Caregiver).filter(
        models.Caregiver.email == current_user.personnel_id
    ).first()
    
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver profile not found")
    
    # Get all active patient accesses
    patient_accesses = db.query(models.PatientAccess).filter(
        models.PatientAccess.caregiver_id == caregiver.id,
        models.PatientAccess.is_active == 1
    ).all()
    
    result = []
    for access in patient_accesses:
        patient = db.query(models.Patient).filter(
            models.Patient.id == access.patient_id
        ).first()
        
        if patient:
            # Get latest prediction
            latest_prediction = db.query(models.HealthPrediction).filter(
                models.HealthPrediction.patient_id == patient.id
            ).order_by(models.HealthPrediction.created_at.desc()).first()
            
            # Get latest reading
            latest_reading = db.query(models.SensorReading).filter(
                models.SensorReading.patient_id == patient.id
            ).order_by(models.SensorReading.created_at.desc()).first()
            
            # Get medical history if caregiver has permission
            allergies = None
            blood_type = None
            chronic_conditions = None
            if access.can_view_sensitive_data:
                med_history = db.query(models.PatientMedicalHistory).filter(
                    models.PatientMedicalHistory.patient_id == patient.id
                ).first()
                if med_history:
                    allergies = med_history.allergies
                    blood_type = med_history.blood_type
                    chronic_conditions = med_history.chronic_conditions
            
            overview = schemas.CaregiverPatientOverview(
                patient_id=patient.id,
                patient_name=patient.name,
                patient_age=patient.age,
                patient_sex=patient.sex,
                relationship_to_patient=access.relationship,
                current_risk_level=latest_prediction.overall_category if latest_prediction else None,
                latest_reading_timestamp=latest_reading.recorded_at if latest_reading else None,
                latest_vitals={
                    "heart_rate": latest_reading.heart_rate,
                    "spo2": latest_reading.spo2,
                    "temperature": latest_reading.temperature,
                    "systolic_bp": latest_reading.systolic_bp,
                    "diastolic_bp": latest_reading.diastolic_bp
                } if latest_reading else None,
                allergies=allergies,
                blood_type=blood_type,
                chronic_conditions=chronic_conditions,
                can_view_sensitive_data=access.can_view_sensitive_data == 1,
                can_receive_alerts=access.can_receive_alerts == 1
            )
            result.append(overview)
    
    return result


@router.get("/caregiver/patient/{patient_id}/history")
def caregiver_get_patient_history(
    patient_id: int,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get patient health history (predictions and readings) for caregiver"""
    current_user = get_current_user(token, db)
    
    # Find caregiver
    caregiver = db.query(models.Caregiver).filter(
        models.Caregiver.email == current_user.personnel_id
    ).first()
    
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver profile not found")
    
    # Check access
    access = db.query(models.PatientAccess).filter(
        models.PatientAccess.patient_id == patient_id,
        models.PatientAccess.caregiver_id == caregiver.id,
        models.PatientAccess.is_active == 1
    ).first()
    
    if not access:
        raise HTTPException(status_code=403, detail="You do not have access to this patient")
    
    # Get recent predictions
    predictions = db.query(models.HealthPrediction).filter(
        models.HealthPrediction.patient_id == patient_id
    ).order_by(models.HealthPrediction.created_at.desc()).limit(limit).all()
    
    # Get recent readings
    readings = db.query(models.SensorReading).filter(
        models.SensorReading.patient_id == patient_id
    ).order_by(models.SensorReading.created_at.desc()).limit(limit).all()
    
    return {
        "predictions": predictions,
        "readings": readings,
        "total_predictions": len(predictions),
        "total_readings": len(readings)
    }
