# Firebase Cloud Messaging Setup Guide

Complete setup instructions for mobile push notifications.

## Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add Project"** or **"Create Project"**
3. Enter project name: `Exobios-Health-Monitor`
4. Select your region/country
5. Create the project

## Step 2: Set Up Firebase for iOS

### 2.1 Register iOS App

1. In Firebase Console, click **"+ Add app"** → **iOS**
2. Enter iOS bundle ID: `com.exobios.health`
3. Download `GoogleService-Info.plist`
4. Follow the setup wizard

### 2.2 Enable Push Notifications

1. Go to **Project Settings** → **Cloud Messaging** tab
2. Scroll to **iOS** section
3. Upload your **APNs Certificate** (from Apple Developer Account)
   - [Generate APNs Certificate Guide](https://firebase.google.com/docs/cloud-messaging/ios/certs)

## Step 3: Set Up Firebase for Android

### 3.1 Register Android App

1. In Firebase Console, click **"+ Add app"** → **Android**
2. Enter Android package name: `com.exobios.health`
3. Enter SHA-1 fingerprint (get from `keytool` or Android Studio)
4. Download `google-services.json`

### 3.2 Configure Android App

Add to `build.gradle`:

```gradle
dependencies {
    implementation platform('com.google.firebase:firebase-bom:32.0.0')
    implementation 'com.google.firebase:firebase-messaging'
}
```

## Step 4: Generate Service Account Key

1. Go to **Project Settings** → **Service Accounts** tab
2. Click **"Generate New Private Key"**
3. Save the JSON file as `firebase_credentials.json`
4. Place it in the backend root directory (same as `main.py`)

**⚠️ SECURITY**: Never commit `firebase_credentials.json` to Git!

Add to `.gitignore`:

```
firebase_credentials.json
```

## Step 5: Set Environment Variables

Update your `.env` file:

```env
FIREBASE_CREDENTIALS_PATH=firebase_credentials.json
FIREBASE_PROJECT_ID=your-project-id
```

## Step 6: Install Backend Dependencies

```bash
pip install -r requirements.txt
```

Key packages:

- `firebase-admin==6.2.0` - Firebase Admin SDK
- `numpy==1.24.3` - For trend analysis
- `statsmodels==0.14.0` - For ARIMA forecasting

## Step 7: Test the Setup

### 7.1 Test Backend

```bash
# In backend directory
python -c "from firebase_notifications import notification_manager; print('Firebase initialized:', notification_manager.initialized)"
```

### 7.2 Send Test Notification

```bash
curl -X POST http://localhost:8000/api/notifications/test/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Mobile App Integration

### iOS (Swift)

```swift
import FirebaseMessaging

// Request notification permission
UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
    if granted {
        DispatchQueue.main.async {
            UIApplication.shared.registerForRemoteNotifications()
        }
    }
}

// Get FCM Token
Messaging.messaging().token { token, error in
    if let token = token {
        // Send to backend
        registerDevice(token: token, type: "iOS")
    }
}

// Handle notifications
func userNotificationCenter(_ center: UNUserNotificationCenter,
                          willPresent notification: UNNotification,
                          withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
    let data = notification.request.content.userInfo

    if let patientId = data["patient_id"] as? String,
       let alertLevel = data["alert_level"] as? String {
        // Handle high-priority alerts
        if alertLevel == "CRITICAL" {
            // Show alert immediately
            completionHandler([.banner, .sound, .badge])
        }
    }
}
```

### Android (Kotlin)

```kotlin
import com.google.firebase.messaging.FirebaseMessaging
import com.google.firebase.messaging.RemoteMessage
import com.google.firebase.messaging.FirebaseMessagingService

class MyFirebaseMessagingService : FirebaseMessagingService() {

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        // Send token to backend
        registerDevice(token, "Android")
    }

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)

        val title = remoteMessage.notification?.title ?: "Alert"
        val message = remoteMessage.notification?.body ?: ""
        val data = remoteMessage.data

        // Handle critical alerts
        val alertLevel = data["alert_level"]
        if (alertLevel == "CRITICAL") {
            showCriticalAlert(title, message, data)
        } else {
            showNormalNotification(title, message)
        }
    }
}

// In MainActivity
FirebaseMessaging.getInstance().token.addOnCompleteListener(OnCompleteListener { task ->
    if (task.isSuccessful) {
        val token = task.result
        registerDevice(token, "Android")
    }
})
```

### React Native

```javascript
import messaging from "@react-native-firebase/messaging";

// Request permission and get token
async function getFirebaseToken() {
  try {
    const token = await messaging().getToken();
    // Send to backend
    registerDevice(token, "ReactNative");
  } catch (error) {
    console.error("Firebase token error:", error);
  }
}

// Handle notifications
messaging().onMessage(async (remoteMessage) => {
  const { data } = remoteMessage;

  if (data.alert_level === "CRITICAL") {
    // Show critical alert
    Alert.alert("CRITICAL ALERT", data.message, [
      { text: "View", onPress: () => navigateToPatient(data.patient_id) },
    ]);
  }
});
```

## API Reference

### Register Device

```bash
POST /api/notifications/register-device
Content-Type: application/json
Authorization: Bearer {token}

{
  "device_token": "FCM_TOKEN_HERE",
  "device_type": "iOS",
  "device_model": "iPhone 14"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Device token registered for iOS",
  "device_id": 1
}
```

### Get Patient Devices

```bash
GET /api/notifications/devices/{patient_id}
Authorization: Bearer {token}
```

### Send Test Notification

```bash
POST /api/notifications/test/{patient_id}
Authorization: Bearer {token}
```

### Get Notification History

```bash
GET /api/notifications/history/{patient_id}?limit=50
Authorization: Bearer {token}
```

## Notification Types

1. **CRITICAL_ALERT** - Patient in critical condition
   - Sound: High-priority alert
   - Priority: Immediate
   - Action: Open patient dashboard

2. **ANOMALY** - Anomaly detected in vital signs
   - Sound: Warning tone
   - Priority: High
   - Action: View vital history

3. **UNREVIEWED_ALERT** - Staff alerts awaiting review
   - Sound: Notification tone
   - Priority: Normal
   - Action: View alerts list

4. **SEPSIS_WARNING** - High sepsis risk detected
   - Sound: Critical alert
   - Priority: Urgent
   - Action: Initiate sepsis protocol

## Troubleshooting

### Firebase Not Initialized

- Check `firebase_credentials.json` exists in backend directory
- Verify `FIREBASE_CREDENTIALS_PATH` in `.env`
- Check JSON file has correct permissions (readable)

### Notifications Not Received

- Verify device tokens are properly registered
- Check device notifications are enabled in OS settings
- Verify APNs certificate (iOS) or Google Cloud Messaging (Android)
- Check notification logs: `GET /api/notifications/history/{patient_id}`

### Invalid FCM Token

- Device tokens may expire
- Refresh token if not received for 30+ days
- Implement token refresh on app startup

### Rate Limiting

- Firebase has rate limits per project
- Free tier: ~2M notifications/day
- Upgrade to Blaze plan for higher limits

## Production Checklist

- [ ] Firebase project created and configured
- [ ] Service account key generated and secured
- [ ] iOS APNs certificate uploaded
- [ ] Android FCM configured
- [ ] Mobile apps integrate Firebase SDK
- [ ] Backend environment variables set
- [ ] Database tables created (migrations run)
- [ ] Test notifications work on both platforms
- [ ] Notification logs are being stored
- [ ] Critical alerts trigger properly
- [ ] Device tokens refresh mechanism implemented
- [ ] Security: Credentials not in git/version control

## Security Best Practices

1. **Credential Management**
   - Store `firebase_credentials.json` securely
   - Use environment variables, not hardcoded paths
   - Rotate keys periodically

2. **Authentication**
   - All notification endpoints require JWT token
   - Verify user has permission to patient's data

3. **Data Privacy**
   - Don't send sensitive data in push bodies
   - Use deep links to show full details in-app
   - Encrypt data in transit (HTTPS only)

4. **Rate Limiting**
   - Implement throttling for alerts
   - Don't send notifications more than once per minute per device
   - Aggregate multiple alerts into single notification

## Support & Documentation

- [Firebase Cloud Messaging Docs](https://firebase.google.com/docs/cloud-messaging)
- [Firebase iOS Setup](https://firebase.google.com/docs/cloud-messaging/ios/client)
- [Firebase Android Setup](https://firebase.google.com/docs/cloud-messaging/android/client)
- [FCM Message Format](https://firebase.google.com/docs/cloud-messaging/concept-options)
