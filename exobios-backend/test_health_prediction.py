# test_health_prediction.py - Test script for health prediction endpoints

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "test_token"  # Replace with actual token after login

# Helper function to make authenticated requests
def make_request(method, endpoint, data=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}{endpoint}"
    
    if method == "POST":
        response = requests.post(url, json=data, headers=headers)
    elif method == "GET":
        response = requests.get(url, headers=headers)
    
    return response


def test_comprehensive_prediction():
    """Test comprehensive health prediction endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Comprehensive Health Prediction")
    print("="*60)
    
    payload = {
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
    
    print(f"\nRequest Payload:")
    print(json.dumps(payload, indent=2))
    
    response = make_request("POST", "/api/predict/health", payload)
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body:")
    print(json.dumps(response.json(), indent=2))
    
    return response.json() if response.status_code == 200 else None


def test_critical_patient():
    """Test with critical patient"""
    print("\n" + "="*60)
    print("TEST 2: Critical Patient (Low Oxygen, High HR)")
    print("="*60)
    
    payload = {
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
    }
    
    print(f"\nRequest Payload:")
    print(json.dumps(payload, indent=2))
    
    response = make_request("POST", "/api/predict/health", payload)
    
    print(f"\nResponse Status: {response.status_code}")
    result = response.json()
    print(f"Overall Risk Score: {result.get('overall_risk_score')}/100")
    print(f"Priority Level: {result.get('priority_level')}")
    print(f"Critical Factors: {result.get('critical_factors')}")
    
    return result


def test_stable_patient():
    """Test with stable patient"""
    print("\n" + "="*60)
    print("TEST 3: Stable Patient")
    print("="*60)
    
    payload = {
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
    }
    
    print(f"\nRequest Payload:")
    print(json.dumps(payload, indent=2))
    
    response = make_request("POST", "/api/predict/health", payload)
    
    print(f"\nResponse Status: {response.status_code}")
    result = response.json()
    print(f"Overall Risk Score: {result.get('overall_risk_score')}/100")
    print(f"Priority Level: {result.get('priority_level')}")
    print(f"Overall Category: {result.get('overall_category')}")
    
    return result


def test_prediction_history():
    """Test retrieving prediction history"""
    print("\n" + "="*60)
    print("TEST 4: Get Prediction History")
    print("="*60)
    
    response = make_request("GET", "/api/predict/history/1")
    
    print(f"\nResponse Status: {response.status_code}")
    if response.status_code == 200:
        predictions = response.json()
        print(f"Found {len(predictions)} predictions for patient 1")
        for i, pred in enumerate(predictions[:3]):
            print(f"\n  Prediction {i+1}:")
            print(f"    Risk Score: {pred['overall_risk_score']}/100")
            print(f"    Category: {pred['overall_category']}")
            print(f"    Created: {pred['created_at']}")


def test_latest_prediction():
    """Test getting latest prediction"""
    print("\n" + "="*60)
    print("TEST 5: Get Latest Prediction")
    print("="*60)
    
    response = make_request("GET", "/api/predict/latest/1")
    
    print(f"\nResponse Status: {response.status_code}")
    if response.status_code == 200:
        pred = response.json()
        print(f"Latest Prediction for Patient 1:")
        print(f"  Risk Score: {pred['overall_risk_score']}/100")
        print(f"  Priority Level: {pred['priority_level']}")
        print(f"  Created: {pred['created_at']}")


def test_risk_factors_analysis():
    """Test risk factor analysis without saving"""
    print("\n" + "="*60)
    print("TEST 6: Risk Factors Analysis (No DB Save)")
    print("="*60)
    
    payload = {
        "patient_id": 4,
        "age": 58,
        "sex": "female",
        "heart_rate": 95,
        "systolic_bp": 155,
        "diastolic_bp": 98,
        "spo2": 96,
        "temperature": 37.0,
        "symptoms": "Headache, dizziness",
        "medical_history": "Hypertension on medication"
    }
    
    response = make_request("POST", "/api/predict/risk-factors", payload)
    
    print(f"\nResponse Status: {response.status_code}")
    if response.status_code == 200:
        assessment = response.json()
        print(f"Overall Risk Score: {assessment['overall_risk_score']}/100")
        print(f"Priority Level: {assessment['priority_level']}")
        print(f"\nIndividual Risk Assessments:")
        for assessment_item in assessment['individual_assessments']:
            print(f"  - {assessment_item['condition']}: {assessment_item['score']}/100 ({assessment_item['category']})")


def test_quick_triage():
    """Test quick field triage endpoint"""
    print("\n" + "="*60)
    print("TEST 7: Quick Field Triage Assessment")
    print("="*60)
    
    params = "?heart_rate=88&systolic_bp=145&diastolic_bp=92&spo2=97&temperature=37.2&age=65"
    
    response = make_request("GET", f"/api/predict/quick-triage{params}")
    
    print(f"\nResponse Status: {response.status_code}")
    if response.status_code == 200:
        triage = response.json()
        print(f"Risk Score: {triage['risk_score']}/100")
        print(f"Priority Level: {triage['priority_level']} (Color: {triage['priority_color']})")
        print(f"Alerts: {triage['alerts'] if triage['alerts'] else 'None'}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("HEALTH PREDICTION MODEL - API TEST SUITE")
    print("="*60)
    
    try:
        # Test 1: Comprehensive prediction
        test_comprehensive_prediction()
        
        # Test 2: Critical patient
        test_critical_patient()
        
        # Test 3: Stable patient
        test_stable_patient()
        
        # Test 4: Prediction history
        test_prediction_history()
        
        # Test 5: Latest prediction
        test_latest_prediction()
        
        # Test 6: Risk factors analysis
        test_risk_factors_analysis()
        
        # Test 7: Quick triage
        test_quick_triage()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to server.")
        print("Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"\nERROR: {str(e)}")


if __name__ == "__main__":
    main()
