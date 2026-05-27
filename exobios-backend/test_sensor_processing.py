# test_sensor_processing.py - Test script for sensor data processing

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_KEY = "test_token"

def make_request(method, endpoint, data=None, params=None):
    """Make authenticated API request"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}{endpoint}"
    
    if method == "POST":
        response = requests.post(url, json=data, headers=headers)
    elif method == "PUT":
        response = requests.put(url, json=data, headers=headers)
    elif method == "GET":
        response = requests.get(url, headers=headers, params=params)
    
    return response


def test_normal_reading():
    """Test with normal vital signs"""
    print("\n" + "="*70)
    print("TEST 1: Normal Reading")
    print("="*70)
    
    payload = {
        "patient_id": 1,
        "heart_rate": 72,
        "spo2": 98,
        "temperature": 37.0,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "respiratory_rate": 16
    }
    
    print(f"\nSending vital signs: {payload}")
    response = make_request("POST", "/api/telemetry/stream", payload)
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    
    print(f"Valid: {result['valid']}")
    print(f"Alerts: {len(result['alerts'])}")
    if result['alerts']:
        for alert in result['alerts']:
            print(f"  - [{alert['level']}] {alert['message']}")
    else:
        print("  No alerts - Patient stable")
    
    return result


def test_high_bp():
    """Test with elevated blood pressure"""
    print("\n" + "="*70)
    print("TEST 2: Elevated Blood Pressure (Warning)")
    print("="*70)
    
    payload = {
        "patient_id": 2,
        "heart_rate": 88,
        "spo2": 96,
        "temperature": 37.1,
        "systolic_bp": 155,
        "diastolic_bp": 98,
        "respiratory_rate": 18
    }
    
    print(f"\nSending vital signs with high BP: {payload}")
    response = make_request("POST", "/api/telemetry/stream", payload)
    
    result = response.json()
    print(f"Valid: {result['valid']}")
    print(f"Alerts: {len(result['alerts'])}")
    for alert in result['alerts']:
        print(f"  - [{alert['level']}] {alert['message']}")
    
    return result


def test_low_oxygen():
    """Test with low oxygen saturation"""
    print("\n" + "="*70)
    print("TEST 3: Low Oxygen (Critical)")
    print("="*70)
    
    payload = {
        "patient_id": 3,
        "heart_rate": 125,
        "spo2": 82,
        "temperature": 37.5,
        "systolic_bp": 140,
        "diastolic_bp": 90,
        "respiratory_rate": 24
    }
    
    print(f"\nSending vital signs with low O2: {payload}")
    response = make_request("POST", "/api/telemetry/stream", payload)
    
    result = response.json()
    print(f"Valid: {result['valid']}")
    print(f"Alerts: {len(result['alerts'])}")
    for alert in result['alerts']:
        print(f"  - [{alert['level']}] {alert['message']}")
    
    return result


def test_fever():
    """Test with high fever"""
    print("\n" + "="*70)
    print("TEST 4: High Fever")
    print("="*70)
    
    payload = {
        "patient_id": 1,
        "heart_rate": 110,
        "spo2": 97,
        "temperature": 40.2,
        "systolic_bp": 135,
        "diastolic_bp": 88,
        "respiratory_rate": 20
    }
    
    print(f"\nSending vital signs with fever: {payload}")
    response = make_request("POST", "/api/telemetry/stream", payload)
    
    result = response.json()
    print(f"Valid: {result['valid']}")
    print(f"Alerts: {len(result['alerts'])}")
    for alert in result['alerts']:
        print(f"  - [{alert['level']}] {alert['message']}")
    
    return result


def test_invalid_reading():
    """Test with invalid data"""
    print("\n" + "="*70)
    print("TEST 5: Invalid Data")
    print("="*70)
    
    payload = {
        "patient_id": 4,
        "heart_rate": 250,  # Invalid - outside valid range
        "spo2": 110,        # Invalid - max is 100
        "temperature": 45   # Invalid - max is 42
    }
    
    print(f"\nSending invalid vital signs: {payload}")
    response = make_request("POST", "/api/telemetry/stream", payload)
    
    result = response.json()
    print(f"Valid: {result['valid']}")
    print(f"Errors: {result['errors']}")
    
    return result


def test_critical_condition():
    """Test with multiple critical values"""
    print("\n" + "="*70)
    print("TEST 6: Critical Condition (Multiple Issues)")
    print("="*70)
    
    payload = {
        "patient_id": 5,
        "heart_rate": 165,
        "spo2": 78,
        "temperature": 41.0,
        "systolic_bp": 185,
        "diastolic_bp": 112,
        "respiratory_rate": 32
    }
    
    print(f"\nSending critical vital signs: {payload}")
    response = make_request("POST", "/api/telemetry/stream", payload)
    
    result = response.json()
    print(f"Valid: {result['valid']}")
    print(f"Alert Count: {len(result['alerts'])}")
    
    critical_alerts = [a for a in result['alerts'] if a['level'] == 'CRITICAL']
    warning_alerts = [a for a in result['alerts'] if a['level'] == 'WARNING']
    
    print(f"Critical Alerts: {len(critical_alerts)}")
    for alert in critical_alerts:
        print(f"  🔴 {alert['message']}")
    
    print(f"Warning Alerts: {len(warning_alerts)}")
    for alert in warning_alerts:
        print(f"  🟠 {alert['message']}")
    
    return result


def test_get_current_telemetry():
    """Test getting current telemetry"""
    print("\n" + "="*70)
    print("TEST 7: Get Current Telemetry")
    print("="*70)
    
    response = make_request("GET", "/api/telemetry/current")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Current Reading:")
        print(f"  Heart Rate: {data['heart_rate']} bpm")
        print(f"  SpO2: {data['spo2']}%")
        print(f"  Temperature: {data['temperature']}°C")
    else:
        print(f"Error: {response.json()}")


def test_sensor_history():
    """Test retrieving sensor history"""
    print("\n" + "="*70)
    print("TEST 8: Get Sensor History")
    print("="*70)
    
    response = make_request("GET", "/api/sensor/history/1", params={"limit": 10})
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        readings = response.json()
        print(f"Found {len(readings)} readings for patient 1")
        for i, reading in enumerate(readings[:3]):
            print(f"\n  Reading {i+1}:")
            print(f"    HR: {reading['heart_rate']}, SpO2: {reading['spo2']}, Temp: {reading['temperature']}")
            print(f"    Valid: {reading['is_valid']}, Anomalies: {reading['has_anomalies']}")
    else:
        print(f"Error: {response.json()}")


def test_sensor_statistics():
    """Test sensor statistics"""
    print("\n" + "="*70)
    print("TEST 9: Get Sensor Statistics")
    print("="*70)
    
    response = make_request("GET", "/api/sensor/statistics/1", params={"minutes": 5})
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"\nStatistics (Last {stats['timeframe_minutes']} minutes):")
        print(f"  Reading Count: {stats['reading_count']}")
        
        print(f"\n  Heart Rate:")
        print(f"    Min: {stats['heart_rate'].get('min', 'N/A')}, Max: {stats['heart_rate'].get('max', 'N/A')}")
        print(f"    Avg: {stats['heart_rate'].get('avg', 'N/A')}, Median: {stats['heart_rate'].get('median', 'N/A')}")
        
        print(f"\n  SpO2:")
        print(f"    Min: {stats['spo2'].get('min', 'N/A')}, Max: {stats['spo2'].get('max', 'N/A')}")
        print(f"    Avg: {stats['spo2'].get('avg', 'N/A')}, Median: {stats['spo2'].get('median', 'N/A')}")
    else:
        print(f"Error: {response.json()}")


def test_sensor_alerts():
    """Test retrieving sensor alerts"""
    print("\n" + "="*70)
    print("TEST 10: Get Sensor Alerts")
    print("="*70)
    
    response = make_request("GET", "/api/sensor/alerts/1", params={"limit": 20})
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        alerts = response.json()
        print(f"Found {len(alerts)} alerts for patient 1")
        
        for i, alert in enumerate(alerts[:5]):
            ack_status = "✓ Acknowledged" if alert['is_acknowledged'] else "⚠ Not Acknowledged"
            print(f"\n  Alert {i+1} ({ack_status}):")
            print(f"    Level: {alert['alert_level']}")
            print(f"    Message: {alert['message']}")
            print(f"    Vital: {alert['affected_vital']}")
    else:
        print(f"Error: {response.json()}")


def test_patient_status():
    """Test getting patient status"""
    print("\n" + "="*70)
    print("TEST 11: Get Patient Sensor Status")
    print("="*70)
    
    response = make_request("GET", "/api/sensor/patient-status/1")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        status = response.json()
        
        status_colors = {
            "STABLE": "🟢",
            "WARNING": "🟠",
            "CRITICAL": "🔴"
        }
        
        color = status_colors.get(status['status'], "⚪")
        print(f"\nPatient Status: {color} {status['status']}")
        print(f"  Critical Alerts: {status['critical_alerts']}")
        print(f"  Warning Alerts: {status['warning_alerts']}")
        
        if status['current_reading']:
            print(f"\n  Current Reading:")
            cr = status['current_reading']
            print(f"    HR: {cr['heart_rate']}, SpO2: {cr['spo2']}, Temp: {cr['temperature']}")
    else:
        print(f"Error: {response.json()}")


def test_acknowledge_alert():
    """Test acknowledging an alert"""
    print("\n" + "="*70)
    print("TEST 12: Acknowledge Alert")
    print("="*70)
    
    # First, get an alert ID
    response = make_request("GET", "/api/sensor/alerts/1", params={"limit": 1})
    
    if response.status_code == 200:
        alerts = response.json()
        if alerts:
            alert_id = alerts[0]['id']
            
            payload = {"personnel_id": "P001"}
            response = make_request("PUT", f"/api/sensor/alerts/{alert_id}/acknowledge", payload)
            
            print(f"Status Code: {response.status_code}")
            result = response.json()
            print(f"Result: {result}")
        else:
            print("No alerts found to acknowledge")
    else:
        print(f"Error fetching alerts: {response.json()}")


def test_rapid_change_detection():
    """Test rapid change anomaly detection"""
    print("\n" + "="*70)
    print("TEST 13: Rapid Change Detection")
    print("="*70)
    
    # Send normal reading
    print("\n1. Sending normal reading...")
    payload1 = {
        "patient_id": 6,
        "heart_rate": 72,
        "spo2": 98,
        "temperature": 37.0,
        "systolic_bp": 120,
        "diastolic_bp": 80
    }
    response = make_request("POST", "/api/telemetry/stream", payload1)
    print(f"   Status: {response.json()['valid']}")
    
    # Wait a moment
    time.sleep(1)
    
    # Send rapid change
    print("\n2. Sending reading with rapid heart rate change...")
    payload2 = {
        "patient_id": 6,
        "heart_rate": 125,  # +53 BPM - rapid increase
        "spo2": 98,
        "temperature": 37.0,
        "systolic_bp": 120,
        "diastolic_bp": 80
    }
    response = make_request("POST", "/api/telemetry/stream", payload2)
    result = response.json()
    
    print(f"   Status: {result['valid']}")
    print(f"   Alerts: {len(result['alerts'])}")
    for alert in result['alerts']:
        print(f"     - [{alert['level']}] {alert['message']}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("SENSOR DATA PROCESSING - API TEST SUITE")
    print("="*70)
    
    try:
        test_normal_reading()
        test_high_bp()
        test_low_oxygen()
        test_fever()
        test_invalid_reading()
        test_critical_condition()
        test_get_current_telemetry()
        test_sensor_history()
        test_sensor_statistics()
        test_sensor_alerts()
        test_patient_status()
        test_acknowledge_alert()
        test_rapid_change_detection()
        
        print("\n" + "="*70)
        print("ALL TESTS COMPLETED")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to server.")
        print("Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
