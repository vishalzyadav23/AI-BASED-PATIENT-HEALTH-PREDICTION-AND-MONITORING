# backend/sepsis_risk.py
"""
Sepsis Early Detection System
Implements SOFA (Sequential Organ Failure Assessment) and qSOFA (quick SOFA) scoring
Along with sepsis likelihood prediction
"""

from typing import Dict, List
from datetime import datetime


class SepsisRiskCalculator:
    """
    Calculates sepsis risk using SOFA and qSOFA scoring systems
    """
    
    def __init__(self):
        self.normal_ranges = {
            "systolic_bp": (90, 130),
            "diastolic_bp": (60, 85),
            "heart_rate": (60, 100),
            "respiratory_rate": (12, 20),
            "temperature": (36.5, 37.5),
            "spo2": (95, 100),
            "lactate": (0.5, 2.0),  # mmol/L
            "creatinine": (0.6, 1.2),  # mg/dL (baseline assumed 0.6-1.2)
            "platelets": (150, 400),  # K/µL (thousand per microliter)
            "bilirubin": (0.1, 1.2),  # mg/dL
            "gcs": (15, 15),  # Glasgow Coma Scale
            "urine_output": (0.5, None)  # mL/kg/hr, baseline >0.5
        }
    
    def calculate_sofa_score(self, patient_vitals: Dict) -> Dict:
        """
        Calculate SOFA (Sequential Organ Failure Assessment) score
        SOFA score ranges from 0-24 (higher = worse)
        Score >= 2 indicates organ dysfunction
        
        Components:
        1. Respiratory (PaO2/FiO2 ratio) - estimated from SpO2
        2. Coagulation (Platelets)
        3. Hepatic (Bilirubin)
        4. Cardiovascular (Mean Arterial Pressure + vasopressor use)
        5. CNS (Glasgow Coma Scale)
        6. Renal (Creatinine + Urine Output)
        """
        
        sofa_scores = {
            "respiratory": 0,
            "coagulation": 0,
            "hepatic": 0,
            "cardiovascular": 0,
            "cns": 0,
            "renal": 0,
            "total": 0
        }
        
        # 1. RESPIRATORY SCORE (based on SpO2 - approximate PaO2/FiO2)
        spo2 = patient_vitals.get("spo2", 95)
        if spo2 < 75:  # Very low
            sofa_scores["respiratory"] = 4
        elif spo2 < 80:
            sofa_scores["respiratory"] = 3
        elif spo2 < 90:
            sofa_scores["respiratory"] = 2
        elif spo2 < 95:
            sofa_scores["respiratory"] = 1
        else:
            sofa_scores["respiratory"] = 0
        
        # 2. COAGULATION SCORE (Platelets - K/µL)
        platelets = patient_vitals.get("platelets", 200)
        if platelets < 20:
            sofa_scores["coagulation"] = 4
        elif platelets < 50:
            sofa_scores["coagulation"] = 3
        elif platelets < 100:
            sofa_scores["coagulation"] = 2
        elif platelets < 150:
            sofa_scores["coagulation"] = 1
        else:
            sofa_scores["coagulation"] = 0
        
        # 3. HEPATIC SCORE (Bilirubin - mg/dL)
        bilirubin = patient_vitals.get("bilirubin", 0.8)
        if bilirubin >= 12:
            sofa_scores["hepatic"] = 4
        elif bilirubin >= 6:
            sofa_scores["hepatic"] = 3
        elif bilirubin >= 2:
            sofa_scores["hepatic"] = 2
        elif bilirubin >= 1.2:
            sofa_scores["hepatic"] = 1
        else:
            sofa_scores["hepatic"] = 0
        
        # 4. CARDIOVASCULAR SCORE (MAP + Vasopressor use)
        systolic = patient_vitals.get("systolic_bp", 110)
        diastolic = patient_vitals.get("diastolic_bp", 70)
        map_value = (systolic + 2 * diastolic) / 3
        
        # Assuming no vasopressor use initially
        if map_value < 70:
            sofa_scores["cardiovascular"] = 4
        elif map_value < 75:
            sofa_scores["cardiovascular"] = 3
        elif map_value < 85:
            sofa_scores["cardiovascular"] = 2
        elif map_value < 90:
            sofa_scores["cardiovascular"] = 1
        else:
            sofa_scores["cardiovascular"] = 0
        
        # 5. CNS SCORE (Glasgow Coma Scale)
        gcs = patient_vitals.get("gcs", 15)
        if gcs <= 5:
            sofa_scores["cns"] = 4
        elif gcs <= 7:
            sofa_scores["cns"] = 3
        elif gcs <= 10:
            sofa_scores["cns"] = 2
        elif gcs < 15:
            sofa_scores["cns"] = 1
        else:
            sofa_scores["cns"] = 0
        
        # 6. RENAL SCORE (Creatinine + Urine Output)
        creatinine = patient_vitals.get("creatinine", 0.9)
        urine_output = patient_vitals.get("urine_output", 1.0)
        
        # Creatinine component (mg/dL)
        if creatinine >= 5.0:
            renal_creat_score = 4
        elif creatinine >= 3.5:
            renal_creat_score = 3
        elif creatinine >= 2.0:
            renal_creat_score = 2
        elif creatinine >= 1.2:
            renal_creat_score = 1
        else:
            renal_creat_score = 0
        
        # Urine output component (mL/kg/hr)
        if urine_output < 0.2:
            renal_urine_score = 4
        elif urine_output < 0.5:
            renal_urine_score = 3
        else:
            renal_urine_score = 0
        
        sofa_scores["renal"] = max(renal_creat_score, renal_urine_score)
        
        # Calculate total SOFA score
        sofa_scores["total"] = sum([
            sofa_scores["respiratory"],
            sofa_scores["coagulation"],
            sofa_scores["hepatic"],
            sofa_scores["cardiovascular"],
            sofa_scores["cns"],
            sofa_scores["renal"]
        ])
        
        return sofa_scores
    
    def calculate_qsofa_score(self, patient_vitals: Dict) -> Dict:
        """
        Calculate qSOFA (quick SOFA) - rapid bedside assessment
        qSOFA score 0-3 (each criterion = 1 point if present)
        Score >= 2 associated with increased mortality outside ICU
        
        Criteria:
        1. Altered Mental Status (GCS < 15)
        2. Systolic BP <= 100 mmHg
        3. Respiratory Rate >= 22
        """
        
        qsofa_score = 0
        criteria = []
        
        # 1. Altered Mental Status
        gcs = patient_vitals.get("gcs", 15)
        if gcs < 15:
            qsofa_score += 1
            criteria.append({"criterion": "Altered Mental Status", "present": True, "value": gcs})
        else:
            criteria.append({"criterion": "Altered Mental Status", "present": False, "value": gcs})
        
        # 2. Hypotension
        systolic_bp = patient_vitals.get("systolic_bp", 110)
        if systolic_bp <= 100:
            qsofa_score += 1
            criteria.append({"criterion": "Systolic BP <= 100", "present": True, "value": systolic_bp})
        else:
            criteria.append({"criterion": "Systolic BP <= 100", "present": False, "value": systolic_bp})
        
        # 3. Tachypnea
        respiratory_rate = patient_vitals.get("respiratory_rate", 16)
        if respiratory_rate >= 22:
            qsofa_score += 1
            criteria.append({"criterion": "Respiratory Rate >= 22", "present": True, "value": respiratory_rate})
        else:
            criteria.append({"criterion": "Respiratory Rate >= 22", "present": False, "value": respiratory_rate})
        
        return {
            "total": qsofa_score,
            "criteria": criteria,
            "risk_level": self._qsofa_risk_interpretation(qsofa_score)
        }
    
    def calculate_sepsis_probability(self, patient_vitals: Dict, history_vitals: List[Dict] = None) -> Dict:
        """
        Calculate probability of sepsis using multiple indicators
        Combines qSOFA, SOFA, lactate, fever/hypothermia, tachycardia, tachypnea
        """
        
        sepsis_indicators = []
        probability_score = 0
        max_possible = 0
        
        # 1. qSOFA Criteria (weight: 25)
        qsofa = self.calculate_qsofa_score(patient_vitals)
        qsofa_weight = 25
        max_possible += qsofa_weight
        qsofa_contribution = (qsofa["total"] / 3) * qsofa_weight
        probability_score += qsofa_contribution
        sepsis_indicators.append({
            "indicator": "qSOFA Score",
            "value": qsofa["total"],
            "weight": qsofa_weight,
            "contribution": qsofa_contribution,
            "risk": qsofa["risk_level"]
        })
        
        # 2. Temperature (Fever/Hypothermia) (weight: 20)
        temp = patient_vitals.get("temperature", 37.0)
        temp_weight = 20
        max_possible += temp_weight
        if temp > 38.5 or temp < 36.0:
            probability_score += temp_weight
            temp_status = "ABNORMAL"
        elif temp > 38.0 or temp < 36.5:
            probability_score += temp_weight * 0.5
            temp_status = "BORDERLINE"
        else:
            temp_status = "NORMAL"
        sepsis_indicators.append({
            "indicator": "Temperature",
            "value": temp,
            "status": temp_status,
            "weight": temp_weight
        })
        
        # 3. Heart Rate (Tachycardia) (weight: 15)
        hr = patient_vitals.get("heart_rate", 70)
        hr_weight = 15
        max_possible += hr_weight
        if hr > 100:
            probability_score += hr_weight
            hr_status = "TACHYCARDIC"
        elif hr > 90:
            probability_score += hr_weight * 0.5
            hr_status = "ELEVATED"
        else:
            hr_status = "NORMAL"
        sepsis_indicators.append({
            "indicator": "Heart Rate (Tachycardia)",
            "value": hr,
            "status": hr_status,
            "weight": hr_weight
        })
        
        # 4. Respiratory Rate (Tachypnea) (weight: 15)
        rr = patient_vitals.get("respiratory_rate", 16)
        rr_weight = 15
        max_possible += rr_weight
        if rr > 20:
            probability_score += rr_weight
            rr_status = "TACHYPNEIC"
        elif rr > 18:
            probability_score += rr_weight * 0.5
            rr_status = "ELEVATED"
        else:
            rr_status = "NORMAL"
        sepsis_indicators.append({
            "indicator": "Respiratory Rate (Tachypnea)",
            "value": rr,
            "status": rr_status,
            "weight": rr_weight
        })
        
        # 5. Hypoxemia (weight: 15)
        spo2 = patient_vitals.get("spo2", 97)
        spo2_weight = 15
        max_possible += spo2_weight
        if spo2 < 92:
            probability_score += spo2_weight
            spo2_status = "SEVERE_HYPOXEMIA"
        elif spo2 < 94:
            probability_score += spo2_weight * 0.5
            spo2_status = "HYPOXEMIA"
        else:
            spo2_status = "NORMAL"
        sepsis_indicators.append({
            "indicator": "Oxygen Saturation (SpO2)",
            "value": spo2,
            "status": spo2_status,
            "weight": spo2_weight
        })
        
        # 6. Lactate (if available) (weight: 10)
        lactate = patient_vitals.get("lactate", 1.0)
        lactate_weight = 10
        max_possible += lactate_weight
        if lactate > 4.0:
            probability_score += lactate_weight
            lactate_status = "ELEVATED"
        elif lactate > 2.0:
            probability_score += lactate_weight * 0.5
            lactate_status = "BORDERLINE"
        else:
            lactate_status = "NORMAL"
        sepsis_indicators.append({
            "indicator": "Lactate Level",
            "value": lactate,
            "status": lactate_status,
            "weight": lactate_weight
        })
        
        # Calculate percentage
        sepsis_probability = (probability_score / max_possible * 100) if max_possible > 0 else 0
        
        return {
            "sepsis_probability_percent": round(sepsis_probability, 2),
            "risk_level": self._probability_risk_level(sepsis_probability),
            "indicators": sepsis_indicators,
            "sofa_score": self.calculate_sofa_score(patient_vitals)["total"],
            "qsofa_score": qsofa["total"],
            "clinical_recommendation": self._get_sepsis_recommendation(sepsis_probability, qsofa["total"])
        }
    
    def _qsofa_risk_interpretation(self, score: int) -> str:
        """Interpret qSOFA score"""
        if score >= 2:
            return "HIGH RISK - Possible sepsis, immediate evaluation recommended"
        elif score == 1:
            return "MODERATE RISK - Monitor closely"
        else:
            return "LOW RISK - Standard care"
    
    def _probability_risk_level(self, probability: float) -> str:
        """Interpret sepsis probability score"""
        if probability >= 70:
            return "CRITICAL"
        elif probability >= 50:
            return "HIGH"
        elif probability >= 30:
            return "MODERATE"
        elif probability >= 15:
            return "MILD"
        else:
            return "LOW"
    
    def _get_sepsis_recommendation(self, probability: float, qsofa_score: int) -> str:
        """Get clinical recommendation based on sepsis risk"""
        if probability >= 70 or qsofa_score >= 2:
            return "URGENT: Initiate sepsis protocol immediately. Blood cultures, lactate, IV fluids, broad-spectrum antibiotics. Call physician."
        elif probability >= 50:
            return "HIGH PRIORITY: Evaluate for sepsis. Consider blood cultures and lactate measurement. Close monitoring required."
        elif probability >= 30:
            return "MODERATE: Monitor vital signs closely. Prepare for sepsis evaluation if condition worsens."
        else:
            return "LOW RISK: Continue routine monitoring."


# Global instance
sepsis_calculator = SepsisRiskCalculator()
