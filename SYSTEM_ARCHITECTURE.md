# 🎯 COMPLETE SYSTEM OVERVIEW

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HEALTHCARE SYSTEM                           │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────┐              ┌──────────────────────────┐
│      FRONTEND (Port 8080)     │              │    BACKEND (Port 8000)   │
│                              │              │                          │
│  ┌──────────────────────┐    │              │  ┌────────────────────┐  │
│  │  index.html          │◄───┼──────────────┼─►│  POST /api/login   │  │
│  │  (Login Page)        │    │   Request    │  │                    │  │
│  │  - Email input       │    │   Response   │  ├────────────────────┤  │
│  │  - Password input    │    │              │  │ POST /api/register │  │
│  │  - Sign In button    │    │              │  │                    │  │
│  │  - Reset link        │    │              │  ├────────────────────┤  │
│  │  - Create link       │    │              │  │POST /api/otp/send  │  │
│  └──────────────────────┘    │              │  │                    │  │
│           │                  │              │  ├────────────────────┤  │
│           │                  │              │  │POST /api/otp/verify│  │
│  ┌────────▼──────────────┐   │              │  │                    │  │
│  │ register.html         │◄──┼──────────────┼─►├────────────────────┤  │
│  │ (Registration Page)   │   │   Request    │  │POST /api/reset-pwd │  │
│  │ - First name input    │   │   Response   │  │                    │  │
│  │ - Last name input     │   │              │  └────────────────────┘  │
│  │ - Email input         │   │              │           │              │
│  │ - Age input           │   │              │           │              │
│  │ - Gender select       │   │              │  ┌────────▼────────────┐ │
│  │ - Password field      │   │              │  │   SQLite Database   │ │
│  │ - Strength indicator  │   │              │  │                     │ │
│  │ - Create button       │   │              │  │ • patient_accounts  │ │
│  └──────────────────────┘   │              │  │ • users             │ │
│           │                  │              │  │ • patients          │ │
│           │                  │              │  │ • sensor_readings   │ │
│  ┌────────▼──────────────┐   │              │  │ • health_predictions│ │
│  │ reset-password.html   │◄──┼──────────────┼─►│ • and more...       │ │
│  │ (Reset Wizard)        │   │              │  └─────────────────────┘ │
│  │ Step 1: Email         │   │              │                          │
│  │ Step 2: OTP (6 digits)│   │              │  ┌────────────────────┐  │
│  │ Step 3: New Password  │   │              │  │   Gmail SMTP       │  │
│  │                       │   │              │  │                    │  │
│  │ - Timer display       │   │              │  │  Sends OTP codes   │  │
│  │ - Resend option       │   │              │  │  via email         │  │
│  │ - Step indicators     │   │              │  └────────────────────┘  │
│  └──────────────────────┘   │              │                          │
│                              │              │                          │
│  ┌──────────────────────┐    │              │                          │
│  │ design-system.css    │    │              │                          │
│  │ (Master Stylesheet)  │    │              │                          │
│  │ - 40+ CSS variables  │    │              │                          │
│  │ - 10+ animations     │    │              │                          │
│  │ - Components         │    │              │                          │
│  │ - Responsive grid    │    │              │                          │
│  └──────────────────────┘    │              │                          │
│                              │              │                          │
│  Toast Notifications         │              │                          │
│  (Success/Error messages)    │              │                          │
│                              │              │                          │
└──────────────────────────────┘              └──────────────────────────┘
         Browser                                   FastAPI Server
```

---

## Feature Implementation Map

```
┌─────────────────────────────────────────────────────────────┐
│                   AUTHENTICATION SYSTEM                      │
└─────────────────────────────────────────────────────────────┘

        SIGN IN
        ┌──────┐
        │Login │
        └──┬───┘
           │
        ┌──▼──────────────────┐
        │ index.html          │
        │ ┌────────────────┐  │
        │ │Email input     │  │
        │ │Password input  │  │
        │ │Sign In button  │  │
        │ └─────────────┬──┘  │
        │               │     │
        └────────────┬──┴─────┘
                     │
            ┌────────▼────────┐
            │ POST /api/login │
            ├─────────────────┤
            │ Email check     │
            │ Pass verification
            │ Token generation
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │ localStorage    │
            │ Store token     │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │ Redirect to     │
            │ dashboard.html  │
            │ ✅ Success      │
            └─────────────────┘


        REGISTER
        ┌──────────┐
        │ Create   │
        │ Account  │
        └──┬───────┘
           │
        ┌──▼──────────────────┐
        │ register.html       │
        │ ┌────────────────┐  │
        │ │First name      │  │
        │ │Last name       │  │
        │ │Email           │  │
        │ │Age             │  │
        │ │Gender          │  │
        │ │Password        │  │
        │ │Confirm password│  │
        │ │Create button   │  │
        │ └─────────────┬──┘  │
        │               │     │
        └───────────┬───┴─────┘
                    │
          ┌─────────▼──────────┐
          │ Validate Form      │
          │ ✓ Email format     │
          │ ✓ Pass strength    │
          │ ✓ Pass match       │
          └──────────┬─────────┘
                     │
          ┌──────────▼──────────┐
          │POST /api/register   │
          ├──────────────────────┤
          │Check email exists   │
          │Hash password        │
          │Create PatientAccount
          │Save to database     │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │ Success Message     │
          │ Redirect to login   │
          │ ✅ Account created  │
          └─────────────────────┘


        RESET PASSWORD
        ┌──────────┐
        │ Forgot   │
        │Password  │
        └──┬───────┘
           │
        ┌──▼──────────────────┐
        │reset-password.html  │
        │                     │
        │ STEP 1: Email       │
        │ ┌────────────────┐  │
        │ │Email input     │  │
        │ │Send OTP button │  │
        │ └─────────────┬──┘  │
        │               │     │
        └───────────┬───┴─────┘
                    │
          ┌─────────▼──────────┐
          │POST /api/otp/send  │
          ├──────────────────────┤
          │Generate OTP code   │
          │Send via Gmail SMTP │
          │Store in memory     │
          │Set 5min timer      │
          └──────────┬──────────┘
                     │
        ┌────────────▼──────────┐
        │ STEP 2: Verify OTP   │
        │ ┌────────────────┐   │
        │ │6 digit inputs  │   │
        │ │Timer countdown │   │
        │ │Verify button   │   │
        │ │Resend link     │   │
        │ └─────────────┬──┘   │
        │               │      │
        └───────────┬───┴──────┘
                    │
          ┌─────────▼──────────┐
          │POST /api/otp/verify│
          ├──────────────────────┤
          │Check OTP matches   │
          │Check not expired   │
          │Delete OTP          │
          └──────────┬──────────┘
                     │
        ┌────────────▼──────────┐
        │ STEP 3: New Password │
        │ ┌────────────────┐   │
        │ │New password    │   │
        │ │Strength bar    │   │
        │ │Confirm pass    │   │
        │ │Reset button    │   │
        │ └─────────────┬──┘   │
        │               │      │
        └───────────┬───┴──────┘
                    │
          ┌─────────▼──────────┐
          │Validate Password   │
          │✓ 8+ characters     │
          │✓ Match confirmed   │
          └──────────┬─────────┘
                     │
          ┌──────────▼──────────┐
          │POST /api/reset-pass │
          ├──────────────────────┤
          │Hash new password   │
          │Update database     │
          │Delete OTP          │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │ Success Message     │
          │ Redirect to login   │
          │ ✅ Password reset   │
          └─────────────────────┘
```

---

## Data Flow Diagram

```
User Input
    ↓
┌─────────────────────────┐
│ Frontend Validation     │ ← Check format, required fields, min/max
├─────────────────────────┤
│ • Email validation      │
│ • Password strength     │
│ • Match confirmation    │
│ • Age bounds            │
└────────────┬────────────┘
             ↓
        Toast shows error
        or allows submit
             │
         (if valid)
             ↓
    ┌────────────────────┐
    │ API Request (fetch)│
    │ POST to backend    │
    └────────┬───────────┘
             ↓
    ┌────────────────────┐
    │ Backend Processing │ ← Receives JSON
    ├────────────────────┤
    │ • Parse request    │
    │ • Validate again   │
    │ • Check database   │
    │ • Hash/verify pass │
    │ • Generate token   │
    └────────┬───────────┘
             ↓
    ┌────────────────────┐
    │ Database Operation │
    ├────────────────────┤
    │ • Check duplicates │
    │ • Create record    │
    │ • Update password  │
    │ • Store data       │
    └────────┬───────────┘
             ↓
    ┌────────────────────┐
    │ JSON Response      │ ← Success/Error message
    └────────┬───────────┘
             ↓
    ┌────────────────────┐
    │ Frontend receives  │
    ├────────────────────┤
    │ • Parse response   │
    │ • Show toast       │
    │ • Store token      │
    │ • Redirect page    │
    └────────────────────┘
             ↓
        ✅ Task complete
```

---

## Component Hierarchy

```
index.html
    ├─ HTML Structure
    │   ├─ Header/Meta
    │   ├─ Hero Section
    │   ├─ Login Form
    │   │   ├─ Email Input
    │   │   ├─ Password Input
    │   │   ├─ Submit Button
    │   │   ├─ Clear Button
    │   │   └─ Footer Links
    │   └─ Toast Container
    │
    ├─ CSS (design-system.css)
    │   ├─ Colors (40+ variables)
    │   ├─ Spacing (8-point scale)
    │   ├─ Typography (3 fonts)
    │   ├─ Components (.btn, .card, .form-group)
    │   ├─ Animations (10+ keyframes)
    │   └─ Responsive (3 breakpoints)
    │
    └─ JavaScript
        ├─ Form Submission Handler
        ├─ API Communication (fetch)
        ├─ Toast Notification Function
        ├─ Error Handling
        └─ Demo Login Function


register.html (Similar structure)
    ├─ 6+ form fields
    ├─ Password strength indicator
    ├─ Submit handler
    └─ Toast notifications


reset-password.html
    ├─ 3-step wizard
    │   ├─ Step 1: Email
    │   ├─ Step 2: OTP (6 digits)
    │   └─ Step 3: Password
    ├─ Step indicators
    ├─ Timer countdown
    ├─ Multiple API calls
    └─ Toast notifications


design-system.css
    ├─ CSS Variables (root)
    │   ├─ Colors (primary, accent, danger, etc.)
    │   ├─ Spacing (sp-xs through sp-3xl)
    │   ├─ Shadows (shadow-sm through shadow-xl)
    │   └─ Radii (radius-sm through radius-2xl)
    ├─ Component Classes
    │   ├─ .btn (8 variants)
    │   ├─ .card (with header/footer)
    │   ├─ .form-group
    │   ├─ .badge
    │   └─ .medical-bg
    ├─ Animation Keyframes
    │   ├─ @keyframes fadeIn
    │   ├─ @keyframes slideUp
    │   ├─ @keyframes slideInLeft
    │   ├─ @keyframes slideInRight
    │   ├─ @keyframes slideInToast
    │   ├─ @keyframes slideOutToast
    │   ├─ @keyframes pulse-warning
    │   ├─ @keyframes pulse-critical
    │   ├─ @keyframes spin
    │   └─ @keyframes float
    ├─ Responsive Utilities
    │   ├─ Mobile (320-640px)
    │   ├─ Tablet (641-1024px)
    │   └─ Desktop (1025px+)
    └─ Accessibility
        ├─ Focus states
        ├─ Semantic HTML
        └─ Color contrast
```

---

## API Endpoint Details

```
📝 POST /api/register
├─ Input: {email, password, first_name, last_name, age, gender}
├─ Process: Validate → Hash → Create → Store
├─ Output: {message, user_id}
├─ Error: 400 if email exists
└─ Response Time: <100ms

🔐 POST /api/login
├─ Input: {email, password}
├─ Process: Find user → Verify password → Generate token
├─ Output: {access_token, token_type, user_id}
├─ Error: 401 if credentials invalid
└─ Response Time: <50ms

📧 POST /api/otp/send
├─ Input: {email}
├─ Process: Generate code → Send email → Store code
├─ Output: {message}
├─ Error: 500 if email fails
└─ Response Time: <1000ms

✓ POST /api/otp/verify
├─ Input: {email, otp}
├─ Process: Check code → Verify match → Delete code
├─ Output: {message}
├─ Error: 400 if code invalid/expired
└─ Response Time: <50ms

🔑 POST /api/reset-password
├─ Input: {email, new_password}
├─ Process: Hash → Update → Store
├─ Output: {message}
├─ Error: 404 if user not found
└─ Response Time: <100ms
```

---

## Security Flow

```
User enters password
    ↓
Frontend validates locally
    ├─ Min 8 characters
    ├─ Has uppercase
    ├─ Has lowercase
    └─ Has numbers/special
    ↓
Send via HTTPS (in production)
    ↓
Backend receives
    ├─ Validates again
    └─ Rejects if invalid
    ↓
Password hashing
    ├─ Use bcrypt
    ├─ Salt rounds: 10
    └─ Hash stored in DB
    ↓
Plain text never stored
    ↓
Login verification
    ├─ User enters password
    ├─ Backend hashes it
    ├─ Compare with stored hash
    └─ No password reveals
    ↓
JWT Token issued
    ├─ Signed with secret
    ├─ Includes user ID
    ├─ Expires in 24 hours
    └─ Sent to frontend
    ↓
Frontend stores in localStorage
    ├─ For persistence
    └─ Sent with each API call
```

---

**Complete system overview showing all components, flows, and relationships!**
