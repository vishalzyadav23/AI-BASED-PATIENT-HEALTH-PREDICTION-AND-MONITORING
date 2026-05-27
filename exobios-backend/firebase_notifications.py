# backend/firebase_notifications.py
"""
Firebase Cloud Messaging (FCM) Integration for Mobile Push Notifications
Handles device token management and push notifications for critical alerts
"""

import firebase_admin
from firebase_admin import credentials, messaging
from typing import List, Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class FirebaseNotificationManager:
    """
    Manages Firebase Cloud Messaging for mobile notifications
    Supports iOS and Android push notifications
    """
    
    def __init__(self):
        """Initialize Firebase Admin SDK"""
        self.app = None
        self.initialized = False
        
        try:
            # Try to initialize Firebase if credentials file exists
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json")
            
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                self.app = firebase_admin.initialize_app(cred)
                self.initialized = True
                print("✓ Firebase initialized successfully")
            else:
                print(f"⚠ Firebase credentials not found at {cred_path}")
                print("  Push notifications will be simulated. Set up Firebase for production.")
                self.initialized = False
        except Exception as e:
            print(f"⚠ Firebase initialization failed: {e}")
            self.initialized = False
    
    def register_device_token(self, patient_id: int, device_token: str, device_type: str, db=None, models=None):
        """
        Register a device token for a patient
        
        Args:
            patient_id: Patient ID
            device_token: FCM device token
            device_type: "iOS" or "Android"
            db: Database session
            models: SQLAlchemy models
        """
        try:
            if db and models:
                # Store in database
                device = models.DeviceToken(
                    patient_id=patient_id,
                    device_token=device_token,
                    device_type=device_type,
                    is_active=True,
                    registered_at=datetime.now()
                )
                db.add(device)
                db.commit()
                return {
                    "status": "success",
                    "message": f"Device token registered for {device_type}",
                    "device_id": device.id
                }
            else:
                return {
                    "status": "warning",
                    "message": "Database not configured, token simulated"
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def send_critical_alert(self, patient_id: int, alert_data: Dict, device_tokens: List[str]) -> Dict:
        """
        Send critical alert notification to patient's devices
        
        Args:
            patient_id: Patient ID
            alert_data: Alert details {level, message, vital, value}
            device_tokens: List of FCM device tokens
        """
        if not device_tokens:
            return {
                "status": "warning",
                "message": "No active devices for this patient",
                "sent_count": 0
            }
        
        notification_body = {
            "title": f"🚨 CRITICAL ALERT - Patient {patient_id}",
            "body": alert_data.get("message", "Critical health alert"),
            "sound": "default",
            "priority": "high"
        }
        
        data_payload = {
            "patient_id": str(patient_id),
            "alert_level": alert_data.get("level", "CRITICAL"),
            "vital": alert_data.get("vital", "Unknown"),
            "value": str(alert_data.get("value", "")),
            "normal_range": f"{alert_data.get('range', [0, 0])[0]}-{alert_data.get('range', [0, 0])[1]}",
            "timestamp": datetime.now().isoformat(),
            "action": "open_patient_details"
        }
        
        if not self.initialized:
            # Simulate notification
            return {
                "status": "simulated",
                "message": "Firebase not configured. Notification would be sent to",
                "devices": device_tokens,
                "sent_count": len(device_tokens),
                "notification": notification_body
            }
        
        try:
            # Send to multiple devices
            sent_count = 0
            failed_tokens = []
            
            for token in device_tokens:
                try:
                    message = messaging.MulticastMessage(
                        notification=messaging.Notification(
                            title=notification_body["title"],
                            body=notification_body["body"]
                        ),
                        data=data_payload,
                        tokens=[token],
                        android=messaging.AndroidConfig(
                            priority="high",
                            notification=messaging.AndroidNotification(
                                sound="default",
                                click_action="CRITICAL_ALERT"
                            )
                        ),
                        webpush=messaging.WebpushConfig(
                            fcm_options=messaging.WebpushFCMOptions(link="https://yourapp.com/alerts")
                        )
                    )
                    
                    response = messaging.send_multicast(message)
                    if response.success_count > 0:
                        sent_count += response.success_count
                    if response.failure_count > 0:
                        failed_tokens.append(token)
                
                except Exception as e:
                    failed_tokens.append(token)
            
            return {
                "status": "success",
                "sent_count": sent_count,
                "failed_count": len(failed_tokens),
                "failed_tokens": failed_tokens,
                "message": f"Notification sent to {sent_count} devices"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send notification: {str(e)}",
                "sent_count": 0
            }
    
    def send_anomaly_alert(self, patient_id: int, anomaly_data: Dict, device_tokens: List[str]) -> Dict:
        """Send anomaly detection alert"""
        notification_body = {
            "title": f"⚠️ ANOMALY DETECTED - Patient {patient_id}",
            "body": anomaly_data.get("message", "Anomaly detected in vital signs"),
            "sound": "default",
            "priority": "high"
        }
        
        data_payload = {
            "patient_id": str(patient_id),
            "alert_level": "WARNING",
            "vital": anomaly_data.get("vital", "Unknown"),
            "anomaly_type": anomaly_data.get("type", "Unknown"),
            "timestamp": datetime.now().isoformat(),
            "action": "open_vital_history"
        }
        
        if not self.initialized:
            return {
                "status": "simulated",
                "message": "Anomaly notification would be sent",
                "sent_count": len(device_tokens)
            }
        
        try:
            for token in device_tokens:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=notification_body["title"],
                        body=notification_body["body"]
                    ),
                    data=data_payload,
                    token=token
                )
                messaging.send(message)
            
            return {
                "status": "success",
                "sent_count": len(device_tokens),
                "message": "Anomaly alerts sent successfully"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def send_unreviewed_alert_notification(self, patient_id: int, alert_count: int, device_tokens: List[str]) -> Dict:
        """Send reminder about unreviewed alerts"""
        notification_body = {
            "title": f"📋 Unreviewed Alerts - Patient {patient_id}",
            "body": f"{alert_count} alert(s) awaiting review",
            "sound": "default",
            "priority": "normal"
        }
        
        data_payload = {
            "patient_id": str(patient_id),
            "alert_level": "INFO",
            "unreviewed_count": str(alert_count),
            "timestamp": datetime.now().isoformat(),
            "action": "open_alerts"
        }
        
        if not self.initialized:
            return {
                "status": "simulated",
                "message": "Unreviewed alert reminder would be sent",
                "sent_count": len(device_tokens)
            }
        
        try:
            for token in device_tokens:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=notification_body["title"],
                        body=notification_body["body"]
                    ),
                    data=data_payload,
                    token=token
                )
                messaging.send(message)
            
            return {
                "status": "success",
                "sent_count": len(device_tokens),
                "message": "Reminder sent successfully"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def deregister_device_token(self, device_token: str, db=None, models=None) -> Dict:
        """Deregister a device token"""
        try:
            if db and models:
                device = db.query(models.DeviceToken).filter(
                    models.DeviceToken.device_token == device_token
                ).first()
                
                if device:
                    device.is_active = False
                    db.commit()
                    return {
                        "status": "success",
                        "message": "Device token deregistered"
                    }
            
            return {
                "status": "warning",
                "message": "Device token not found"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_active_device_tokens(self, patient_id: int, db=None, models=None) -> List[str]:
        """Get all active device tokens for a patient"""
        if not db or not models:
            return []
        
        try:
            devices = db.query(models.DeviceToken).filter(
                models.DeviceToken.patient_id == patient_id,
                models.DeviceToken.is_active == True
            ).all()
            
            return [device.device_token for device in devices]
        except Exception as e:
            print(f"Error fetching device tokens: {e}")
            return []


# Global instance
notification_manager = FirebaseNotificationManager()
