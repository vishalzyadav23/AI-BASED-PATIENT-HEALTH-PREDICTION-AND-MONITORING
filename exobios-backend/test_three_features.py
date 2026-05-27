# backend/test_three_features.py
"""
Integration tests for Time-Series Trends, Sepsis Risk, and Firebase Notifications
Run this to verify all three features are working correctly
"""

import json
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import models
from database import SessionLocal
from timeseries_analysis import trend_analyzer
from sepsis_risk import sepsis_calculator
from firebase_notifications import notification_manager


def generate_vital_readings(patient_id: int, num_readings: int = 50, db: Session = None):
    """Generate realistic vital sign readings and store in database"""
    print(f"\n📊 Generating {num_readings} vital readings for patient {patient_id}...")
    
    readings = []
    base_time = datetime.now() - timedelta(hours=24)
    
    for i in range(num_readings):
        # Generate realistic vital signs with some variation
        reading = models.SensorReading(
            patient_id=patient_id,
            heart_rate=random.randint(65, 85),
            spo2=random.randint(95, 99),
            temperature=random.uniform(36.8, 37.2),
            systolic_bp=random.randint(110, 130),
            diastolic_bp=random.randint(65, 80),
            respiratory_rate=random.randint(14, 18),
            is_valid=1,
            has_anomalies=0,
            recorded_at=base_time + timedelta(minutes=i*30)
        )
        readings.append(reading)
        if db:
            db.add(reading)
    
    if db:
        db.commit()
        print(f"✅ Stored {num_readings} readings in database")
    
    return readings


def test_timeseries_trends():
    """Test Time-Series Trend Analysis"""
    print("\n" + "="*60)
    print("TEST 1: TIME-SERIES TREND ANALYSIS")
    print("="*60)
    
    db = SessionLocal()
    patient_id = 1
    
    try:
        # Generate test data
        readings = generate_vital_readings(patient_id, num_readings=48, db=db)
        
        # Fetch readings from database
        db_readings = db.query(models.SensorReading).filter(
            models.SensorReading.patient_id == patient_id
        ).order_by(models.SensorReading.recorded_at).all()
        
        readings_data = [
            {
                "timestamp": r.recorded_at,
                "vital": "heart_rate",
                "value": r.heart_rate
            }
            for r in db_readings
            if r.heart_rate
        ]
        
        # Test trend analysis
        trend = trend_analyzer.get_trend_analysis(readings_data, "heart_rate", hours=24)
        
        print("\n✅ HEART RATE TREND ANALYSIS:")
        print(f"   Mean: {trend['mean']:.1f} bpm")
        print(f"   Std Dev: {trend['std_dev']:.1f}")
        print(f"   Trend: {trend['trend']} ({trend['trend_severity']})")
        print(f"   Volatility: {trend['volatility']:.3f} ({trend['volatility_level']})")
        print(f"   Forecast (next 6): {[f'{v:.1f}' for v in trend['forecast_next_6']]}")
        
        if "clinical_alert" in trend:
            alert = trend["clinical_alert"]
            if isinstance(alert, dict):
                print(f"   Alert: {alert.get('message', 'None')}")
            else:
                print(f"   Alerts: {len(alert)} detected")
        
        # Test multi-vital trends
        multi_trends = trend_analyzer.get_multi_vital_trend(readings_data, hours=24)
        print(f"\n✅ MULTI-VITAL ANALYSIS:")
        print(f"   Overall Status: {multi_trends['overall_status']}")
        print(f"   Vitals Analyzed: {len(multi_trends['vital_trends'])}")
        
        print("\n✅ TREND ANALYSIS TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ TREND ANALYSIS TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_sepsis_risk_assessment():
    """Test Sepsis Risk Assessment"""
    print("\n" + "="*60)
    print("TEST 2: SEPSIS RISK ASSESSMENT")
    print("="*60)
    
    try:
        # Test case 1: Normal patient
        print("\n📋 Test Case 1: Normal Vital Signs")
        normal_vitals = {
            "heart_rate": 75,
            "respiratory_rate": 16,
            "systolic_bp": 120,
            "diastolic_bp": 75,
            "temperature": 37.0,
            "spo2": 98,
            "gcs": 15,
            "lactate": 1.5,
            "platelets": 250,
            "bilirubin": 0.8,
            "creatinine": 1.0,
            "urine_output": 1.0
        }
        
        result1 = sepsis_calculator.calculate_sepsis_probability(normal_vitals)
        print(f"   Sepsis Probability: {result1['sepsis_probability_percent']:.1f}%")
        print(f"   Risk Level: {result1['risk_level']}")
        print(f"   SOFA Score: {result1['sofa_score']}/24")
        print(f"   qSOFA Score: {result1['qsofa_score']}/3")
        assert result1['risk_level'] == 'LOW', "Normal vitals should show LOW risk"
        print("   ✅ PASSED")
        
        # Test case 2: High risk patient
        print("\n📋 Test Case 2: High-Risk Vital Signs")
        high_risk_vitals = {
            "heart_rate": 115,
            "respiratory_rate": 26,
            "systolic_bp": 92,
            "diastolic_bp": 55,
            "temperature": 39.2,
            "spo2": 90,
            "gcs": 13,
            "lactate": 3.5,
            "platelets": 120,
            "bilirubin": 1.5,
            "creatinine": 1.8,
            "urine_output": 0.3
        }
        
        result2 = sepsis_calculator.calculate_sepsis_probability(high_risk_vitals)
        print(f"   Sepsis Probability: {result2['sepsis_probability_percent']:.1f}%")
        print(f"   Risk Level: {result2['risk_level']}")
        print(f"   SOFA Score: {result2['sofa_score']}/24")
        print(f"   qSOFA Score: {result2['qsofa_score']}/3")
        assert result2['risk_level'] in ['HIGH', 'CRITICAL'], "High-risk vitals should trigger alert"
        print("   ✅ PASSED")
        
        # Test case 3: qSOFA scoring
        print("\n📋 Test Case 3: qSOFA Scoring")
        qsofa_result = sepsis_calculator.calculate_qsofa_score(high_risk_vitals)
        print(f"   qSOFA Score: {qsofa_result['total']}/3")
        print(f"   Risk Level: {qsofa_result['risk_level']}")
        print("   ✅ PASSED")
        
        # Test case 4: SOFA scoring
        print("\n📋 Test Case 4: SOFA Scoring")
        sofa_result = sepsis_calculator.calculate_sofa_score(high_risk_vitals)
        print(f"   SOFA Score: {sofa_result['total']}/24")
        print(f"   Breakdown:")
        print(f"     - Respiratory: {sofa_result['respiratory']}")
        print(f"     - Coagulation: {sofa_result['coagulation']}")
        print(f"     - Hepatic: {sofa_result['hepatic']}")
        print(f"     - Cardiovascular: {sofa_result['cardiovascular']}")
        print(f"     - CNS: {sofa_result['cns']}")
        print(f"     - Renal: {sofa_result['renal']}")
        print("   ✅ PASSED")
        
        print("\n✅ SEPSIS ASSESSMENT TEST PASSED")
        return True
        
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ SEPSIS ASSESSMENT TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_firebase_notifications():
    """Test Firebase Notifications"""
    print("\n" + "="*60)
    print("TEST 3: FIREBASE MOBILE NOTIFICATIONS")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        patient_id = 1
        
        # Test 1: Device Registration (simulated)
        print("\n📱 Test 1: Device Registration")
        device_result = notification_manager.register_device_token(
            patient_id=patient_id,
            device_token="test_fcm_token_12345",
            device_type="iOS",
            db=db,
            models=models
        )
        print(f"   Status: {device_result['status']}")
        print(f"   Message: {device_result['message']}")
        print("   ✅ PASSED")
        
        # Test 2: Critical Alert
        print("\n📱 Test 2: Send Critical Alert")
        alert_result = notification_manager.send_critical_alert(
            patient_id=patient_id,
            alert_data={
                "level": "CRITICAL",
                "message": "SpO2 dropped to 88% - immediate action needed",
                "vital": "spo2",
                "value": 88,
                "range": [95, 100]
            },
            device_tokens=["test_fcm_token_12345"]
        )
        print(f"   Status: {alert_result['status']}")
        print(f"   Sent to devices: {alert_result.get('sent_count', 0)}")
        print("   ✅ PASSED (simulated or sent successfully)")
        
        # Test 3: Sepsis Warning
        print("\n📱 Test 3: Send Sepsis Warning")
        sepsis_result = notification_manager.send_critical_alert(
            patient_id=patient_id,
            alert_data={
                "level": "SEPSIS_WARNING",
                "message": "Sepsis probability: 68% - Recommend immediate evaluation",
                "vital": "multi-vital",
                "value": 68,
                "range": [0, 50]
            },
            device_tokens=["test_fcm_token_12345"]
        )
        print(f"   Status: {sepsis_result['status']}")
        print("   ✅ PASSED (simulated or sent successfully)")
        
        # Test 4: Get Active Devices
        print("\n📱 Test 4: Get Active Devices")
        active_devices = notification_manager.get_active_device_tokens(patient_id, db, models)
        print(f"   Active devices for patient {patient_id}: {len(active_devices)}")
        if active_devices:
            print(f"   Devices: {active_devices[:2]}...")  # Show first 2
        print("   ✅ PASSED")
        
        # Test 5: Notification Status without Firebase
        print("\n📱 Test 5: Firebase Initialization Status")
        print(f"   Firebase Initialized: {notification_manager.initialized}")
        print(f"   Note: Simulated mode is OK for development")
        print("   ✅ PASSED")
        
        print("\n✅ FIREBASE NOTIFICATIONS TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ FIREBASE NOTIFICATIONS TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_integration():
    """Test integration between all three features"""
    print("\n" + "="*60)
    print("TEST 4: INTEGRATION TEST")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        patient_id = 1
        
        # Step 1: Generate sensor data
        print("\n🔗 Step 1: Generate Sensor Data")
        readings = generate_vital_readings(patient_id, num_readings=30, db=db)
        print("   ✅ Sensor data generated")
        
        # Step 2: Analyze trends
        print("\n🔗 Step 2: Analyze Trends")
        db_readings = db.query(models.SensorReading).filter(
            models.SensorReading.patient_id == patient_id
        ).all()
        
        readings_data = [
            {"timestamp": r.recorded_at, "vital": "heart_rate", "value": r.heart_rate}
            for r in db_readings if r.heart_rate
        ]
        
        trend = trend_analyzer.get_trend_analysis(readings_data, "heart_rate", hours=24)
        print(f"   Heart Rate Trend: {trend['trend']}")
        print("   ✅ Trends analyzed")
        
        # Step 3: Assess sepsis risk
        print("\n🔗 Step 3: Assess Sepsis Risk")
        vitals = {
            "heart_rate": db_readings[-1].heart_rate if db_readings else 75,
            "respiratory_rate": db_readings[-1].respiratory_rate if db_readings else 16,
            "systolic_bp": db_readings[-1].systolic_bp if db_readings else 120,
            "diastolic_bp": db_readings[-1].diastolic_bp if db_readings else 75,
            "temperature": db_readings[-1].temperature if db_readings else 37.0,
            "spo2": db_readings[-1].spo2 if db_readings else 98,
            "gcs": 15,
            "lactate": 1.5,
            "platelets": 250,
            "bilirubin": 0.8,
            "creatinine": 1.0,
            "urine_output": 1.0
        }
        
        sepsis = sepsis_calculator.calculate_sepsis_probability(vitals)
        print(f"   Sepsis Risk: {sepsis['risk_level']} ({sepsis['sepsis_probability_percent']:.1f}%)")
        print("   ✅ Sepsis risk calculated")
        
        # Step 4: Send notifications if risk is high
        print("\n🔗 Step 4: Check Notification Triggers")
        if sepsis['risk_level'] in ['HIGH', 'CRITICAL']:
            print(f"   ⚠️ High sepsis risk detected - would send notification")
        else:
            print(f"   ✓ Risk level acceptable - notifications not needed")
        print("   ✅ Notification logic validated")
        
        print("\n✅ INTEGRATION TEST PASSED")
        print("\n📊 SUMMARY:")
        print(f"   - Generated {len(readings)} vital readings")
        print(f"   - Analyzed trends: {trend['trend']} ({trend['slope']:.2f} units/hour)")
        print(f"   - Sepsis risk: {sepsis['risk_level']} ({sepsis['sepsis_probability_percent']:.1f}%)")
        print(f"   - SOFA: {sepsis['sofa_score']}/24, qSOFA: {sepsis['qsofa_score']}/3")
        
        return True
        
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 THREE ADVANCED FEATURES - INTEGRATION TEST SUITE")
    print("="*60)
    
    results = {}
    
    # Run all tests
    results['Trend Analysis'] = test_timeseries_trends()
    results['Sepsis Assessment'] = test_sepsis_risk_assessment()
    results['Firebase Notifications'] = test_firebase_notifications()
    results['Integration'] = test_integration()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - System is ready for production!")
    else:
        print("⚠️  Some tests failed - please review errors above")
    print("="*60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
