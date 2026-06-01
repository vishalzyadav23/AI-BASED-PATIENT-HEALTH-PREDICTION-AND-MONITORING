# 🚀 QUICK START GUIDE - RUN YOUR PROJECT IN 5 MINUTES

## ⚡ TL;DR - Start Here

### Terminal 1: Start Backend

```bash
cd exobios-backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Start Frontend

```bash
cd exobios-frontend
# Option A: Use Python server
python -m http.server 8080

# Option B: Just open in browser
# Double-click: index.html
```

### Browser

```
Open: http://localhost:8080
Or: http://localhost/exobios-frontend/index.html
```

---

## 📋 DETAILED SETUP

### Prerequisites

- Python 3.8+ installed
- Browser (Chrome, Firefox, Safari, Edge)
- Terminal/Command Prompt

### Step 1: Backend Setup

```bash
# Navigate to backend folder
cd exobios-backend

# Create virtual environment (if needed)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Backend Configuration

Check `.env` file exists with:

```
GEMINI_API_KEY=your_key_here
SENDER_EMAIL=your_email@gmail.com
APP_PASSWORD=your_app_password
```

### Step 3: Start Backend

```bash
# Make sure you're in exobios-backend folder
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**

```
Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 4: Start Frontend (New Terminal)

```bash
cd exobios-frontend
python -m http.server 8080
```

**Expected output:**

```
Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

### Step 5: Open in Browser

Go to:

- **Frontend:** http://localhost:8080
- **Backend API Docs:** http://localhost:8000/docs
- **Backend ReDoc:** http://localhost:8000/redoc

---

## 🧪 TEST YOUR SETUP

### Test 1: Frontend Loads

1. Open http://localhost:8080 in browser
2. You should see the HealthSync Pro login page
3. Check browser console (F12) - no errors?

### Test 2: Backend Responds

1. Open http://localhost:8000/docs in browser
2. You should see Swagger API documentation
3. Try clicking "Try it out" on any endpoint

### Test 3: WebSocket Works

1. Open developer tools (F12)
2. Go to Console tab
3. Run:

```javascript
const ws = new WebSocket("ws://localhost:8000/api/telemetry/ws");
ws.onmessage = (e) => console.log(e.data);
```

4. You should see data flowing in console

---

## 📱 USING THE APPLICATION

### Patient Login

1. Go to http://localhost:8080
2. For demo, use:
   - Email: `demo@exobios.com`
   - Password: `demo123`
3. Click "Sign In"

### Caregiver Login

1. Go to http://localhost:8080/caregiver-login.html
2. For demo, use credentials from demo data
3. Click "Sign In"

### View Dashboard

1. After login, you'll see the patient dashboard
2. Real-time vitals update via WebSocket
3. View health predictions
4. Check trends and history

---

## 🔧 TROUBLESHOOTING

### Backend Won't Start

```bash
# Error: Port 8000 already in use
# Solution: Kill the process on port 8000 or use different port
python -m uvicorn main:app --reload --port 8001

# Error: Module not found
# Solution: Ensure all dependencies installed
pip install -r requirements.txt
```

### Frontend Won't Load

```
Error: CSS not loading / styling looks wrong
- Check: design-system.css is in exobios-frontend folder
- Solution: Copy design-system.css if missing
```

### API Not Responding

```
Error: Failed to fetch / Connection refused
- Check: Backend is running (Terminal 1)
- Check: Backend URL is http://localhost:8000
- Check: CORS is enabled in main.py (it is by default)
```

### Database Error

```
Error: "No such table"
- Solution: Database will auto-create tables on first run
- Check: exobios_local.db file exists after running
```

---

## 📊 PROJECT STRUCTURE

```
AI BASED PATIENT HEALTH PREDICTION AND MONITORING/
├── exobios-backend/              # Python FastAPI Backend
│   ├── main.py                   # Main server
│   ├── database.py               # Database config
│   ├── models.py                 # Data models
│   ├── requirements.txt           # Dependencies
│   ├── .env                      # Configuration
│   └── [other modules]
│
├── exobios-frontend/             # HTML/CSS/JS Frontend
│   ├── index.html                # Patient login
│   ├── dashboard.html            # Patient dashboard
│   ├── caregiver-login.html      # Caregiver login
│   ├── design-system.css         # Master styles
│   └── [other HTML pages]
│
└── README.md                     # Project info
```

---

## ✅ CHECKLIST

- [ ] Python 3.8+ installed
- [ ] Backend folder: exobios-backend exists
- [ ] Frontend folder: exobios-frontend exists
- [ ] .env file in backend folder
- [ ] requirements.txt in backend folder
- [ ] design-system.css in frontend folder
- [ ] All HTML files in frontend folder

---

## 🎯 KEY URLS

| Purpose           | URL                                        |
| ----------------- | ------------------------------------------ |
| Patient Login     | http://localhost:8080                      |
| Caregiver Login   | http://localhost:8080/caregiver-login.html |
| Patient Dashboard | http://localhost:8080/dashboard.html       |
| API Documentation | http://localhost:8000/docs                 |
| API ReDoc         | http://localhost:8000/redoc                |
| WebSocket         | ws://localhost:8000/api/telemetry/ws       |
| Health Prediction | http://localhost:8000/api/predict          |

---

## 🚨 COMMON ERRORS & FIXES

### "ModuleNotFoundError: No module named 'fastapi'"

```bash
pip install fastapi uvicorn
```

### "Address already in use"

```bash
# Change port
python -m uvicorn main:app --port 8001
```

### "No such file or directory: '.env'"

```bash
# .env file missing, create it with required vars:
GEMINI_API_KEY=your_key
SENDER_EMAIL=your_email@gmail.com
APP_PASSWORD=your_password
```

### CSS/Styles not loading

```
Make sure these files are in exobios-frontend/:
- design-system.css
- All HTML files
```

---

## 💡 TIPS

1. **Keep both terminals running** - One for backend, one for frontend
2. **Use Chrome DevTools** (F12) to debug
3. **Check console** for JavaScript errors
4. **API docs auto-generated** at http://localhost:8000/docs
5. **Database auto-creates** on first run
6. **Hot reload enabled** - Changes auto-refresh

---

## 🎓 NEXT STEPS AFTER STARTUP

1. **Test the login** - Try signing in
2. **Check dashboard** - View patient vitals
3. **Test predictions** - Run health assessment
4. **Monitor WebSocket** - Watch real-time updates
5. **Review API docs** - Explore available endpoints

---

## 📞 STILL HAVING ISSUES?

1. Check PROJECT_AUDIT_REPORT.md for detailed info
2. Verify all files are in correct folders
3. Check that ports 8000 and 8080 are available
4. Ensure Python packages installed: `pip list | grep fastapi`
5. Review .env file configuration

---

**You're all set! 🎉 Now run those terminal commands above and access your project!**
