# health_prediction.py - ML Models for Health Risk Prediction
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple

class HealthPredictionModel:
    """
    Comprehensive health prediction model using vital signs and patient data.
    Implements multiple predictive algorithms for different health conditions.
    """
    
    def __init__(self):
        # Risk thresholds for various conditions
        self.bp_normal = (90, 120, 60, 80)  # systolic min/max, diastolic min/max
        self.heart_rate_normal = (60, 100)
        self.spo2_normal = (95, 100)
        self.temp_normal = (36.5, 37.5)
        
    def calculate_cardiovascular_risk(self, 
                                     heart_rate: int, 
                                     systolic_bp: int, 
                                     diastolic_bp: int,
                                     age: int,
                                     sex: str) -> Dict:
        """
        Calculate cardiovascular disease risk using Framingham Risk Score approach.
        Returns risk score (0-100) and category.
        """
        risk_score = 0
        risk_factors = []
        
        # Heart rate abnormality
        if heart_rate < 60 or heart_rate > 100:
            risk_score += 15
            risk_factors.append(f"Abnormal heart rate: {heart_rate} bpm")
        
        # Blood pressure assessment
        if systolic_bp >= 140 or diastolic_bp >= 90:
            risk_score += 20
            risk_factors.append(f"Stage 2 Hypertension: {systolic_bp}/{diastolic_bp} mmHg")
        elif systolic_bp >= 130 or diastolic_bp >= 80:
            risk_score += 10
            risk_factors.append(f"Stage 1 Hypertension: {systolic_bp}/{diastolic_bp} mmHg")
        
        # Age risk (simplified)
        if age > 50:
            risk_score += min(10, (age - 50) // 5)
            risk_factors.append(f"Age-related risk: {age} years")
        
        # Sex adjustment
        if sex.lower() == "male":
            risk_score += 5
        
        # Cap score at 100
        risk_score = min(100, risk_score)
        
        # Determine risk category
        if risk_score < 20:
            category = "LOW"
        elif risk_score < 40:
            category = "MODERATE"
        elif risk_score < 60:
            category = "HIGH"
        else:
            category = "VERY HIGH"
        
        return {
            "score": risk_score,
            "category": category,
            "risk_factors": risk_factors,
            "condition": "Cardiovascular Disease"
        }
    
    def calculate_diabetes_risk(self, age: int, bmi: float = None) -> Dict:
        """
        Calculate Type 2 Diabetes risk.
        """
        risk_score = 0
        risk_factors = []
        
        # Age-based risk
        if age > 45:
            risk_score += 20
            risk_factors.append(f"Age {age} (45+ years higher risk)")
        
        # BMI assessment (if provided)
        if bmi:
            if bmi >= 30:
                risk_score += 25
                risk_factors.append(f"Obesity: BMI {bmi}")
            elif bmi >= 25:
                risk_score += 15
                risk_factors.append(f"Overweight: BMI {bmi}")
        
        risk_score = min(100, risk_score)
        
        if risk_score < 20:
            category = "LOW"
        elif risk_score < 40:
            category = "MODERATE"
        else:
            category = "HIGH"
        
        return {
            "score": risk_score,
            "category": category,
            "risk_factors": risk_factors,
            "condition": "Type 2 Diabetes"
        }
    
    def calculate_stroke_risk(self, 
                             heart_rate: int,
                             systolic_bp: int, 
                             diastolic_bp: int,
                             age: int) -> Dict:
        """
        Calculate stroke risk using simplified CHADS2 Score approach.
        """
        risk_score = 0
        risk_factors = []
        
        # Age component (age > 75 = 2 points, 65-74 = 1 point)
        if age >= 75:
            risk_score += 15
            risk_factors.append(f"Age {age} (75+ years)")
        elif age >= 65:
            risk_score += 10
            risk_factors.append(f"Age {age} (65-74 years)")
        
        # Hypertension
        if systolic_bp >= 140:
            risk_score += 15
            risk_factors.append(f"Hypertension: {systolic_bp}/{diastolic_bp} mmHg")
        
        # Heart rate irregularity indicator
        if heart_rate > 120 or heart_rate < 40:
            risk_score += 20
            risk_factors.append(f"Severe heart rate abnormality: {heart_rate} bpm")
        
        risk_score = min(100, risk_score)
        
        if risk_score < 15:
            category = "LOW"
        elif risk_score < 35:
            category = "MODERATE"
        elif risk_score < 60:
            category = "HIGH"
        else:
            category = "VERY HIGH"
        
        return {
            "score": risk_score,
            "category": category,
            "risk_factors": risk_factors,
            "condition": "Stroke"
        }
    
    def calculate_hypoxia_risk(self, spo2: int) -> Dict:
        """
        Calculate risk based on blood oxygen saturation.
        """
        risk_score = 0
        risk_factors = []
        
        if spo2 >= 95:
            risk_score = 5
            category = "LOW"
            risk_factors.append(f"Normal SpO2: {spo2}%")
        elif spo2 >= 90:
            risk_score = 30
            category = "MODERATE"
            risk_factors.append(f"Mild hypoxia: {spo2}%")
        elif spo2 >= 85:
            risk_score = 65
            category = "HIGH"
            risk_factors.append(f"Moderate hypoxia: {spo2}%")
        else:
            risk_score = 95
            category = "VERY HIGH"
            risk_factors.append(f"Severe hypoxia: {spo2}%")
        
        return {
            "score": risk_score,
            "category": category,
            "risk_factors": risk_factors,
            "condition": "Hypoxia"
        }
    
    def calculate_fever_risk(self, temperature: float) -> Dict:
        """
        Calculate infection/fever risk.
        """
        risk_score = 0
        risk_factors = []
        
        if temperature < 36.5:
            risk_score = 20
            category = "MODERATE"
            risk_factors.append(f"Hypothermia: {temperature}°C")
        elif temperature <= 37.5:
            risk_score = 0
            category = "NORMAL"
            risk_factors.append(f"Normal temperature: {temperature}°C")
        elif temperature <= 38.5:
            risk_score = 20
            category = "MODERATE"
            risk_factors.append(f"Mild fever: {temperature}°C")
        elif temperature <= 39.5:
            risk_score = 50
            category = "HIGH"
            risk_factors.append(f"High fever: {temperature}°C")
        else:
            risk_score = 85
            category = "VERY HIGH"
            risk_factors.append(f"Dangerously high fever: {temperature}°C")
        
        return {
            "score": risk_score,
            "category": category,
            "risk_factors": risk_factors,
            "condition": "Infection/Fever"
        }
    
    def comprehensive_health_assessment(self,
                                       age: int,
                                       sex: str,
                                       heart_rate: int,
                                       systolic_bp: int,
                                       diastolic_bp: int,
                                       spo2: int,
                                       temperature: float,
                                       symptoms: str = "",
                                       medical_history: str = "",
                                       patient_id: str = None) -> Dict:
        """
        Perform comprehensive health assessment across multiple conditions.
        Returns all risk assessments and an overall health score.
        """
        
        assessments = []
        overall_risk = 0
        
        # Calculate individual risks
        cv_risk = self.calculate_cardiovascular_risk(heart_rate, systolic_bp, diastolic_bp, age, sex)
        assessments.append(cv_risk)
        
        stroke_risk = self.calculate_stroke_risk(heart_rate, systolic_bp, diastolic_bp, age)
        assessments.append(stroke_risk)
        
        hypoxia_risk = self.calculate_hypoxia_risk(spo2)
        assessments.append(hypoxia_risk)
        
        fever_risk = self.calculate_fever_risk(temperature)
        assessments.append(fever_risk)
        
        # Calculate overall risk as average of top 3 concerns
        scores = [a["score"] for a in assessments]
        overall_risk = int(np.mean(sorted(scores, reverse=True)[:3]))
        
        # Determine overall category
        if overall_risk < 20:
            overall_category = "STABLE"
        elif overall_risk < 40:
            overall_category = "MONITOR"
        elif overall_risk < 60:
            overall_category = "ALERT"
        else:
            overall_category = "CRITICAL"
        
        # Extract critical factors
        critical_factors = [f"{a['risk_factors'][0]}" for a in assessments if a["score"] > 40 and a["risk_factors"]]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_risk_score": overall_risk,
            "overall_category": overall_category,
            "individual_assessments": assessments,
            "critical_factors": critical_factors[:3],  # Top 3 critical factors
            "vital_signs": {
                "heart_rate": heart_rate,
                "systolic_bp": systolic_bp,
                "diastolic_bp": diastolic_bp,
                "spo2": spo2,
                "temperature": temperature
            },
            "patient_info": {
                "patient_id": patient_id,
                "age": age,
                "sex": sex,
                "symptoms": symptoms,
                "medical_history": medical_history
            }
        }
    
    def get_priority_level(self, overall_risk_score: int) -> Tuple[str, str]:
        """
        Get emergency priority level (like ESI - Emergency Severity Index).
        """
        if overall_risk_score >= 80:
            return "RESUSCITATION", "red"
        elif overall_risk_score >= 60:
            return "EMERGENT", "orange"
        elif overall_risk_score >= 40:
            return "URGENT", "yellow"
        elif overall_risk_score >= 20:
            return "SEMI-URGENT", "blue"
        else:
            return "NON-URGENT", "green"


# Initialize global model instance
prediction_model = HealthPredictionModel()