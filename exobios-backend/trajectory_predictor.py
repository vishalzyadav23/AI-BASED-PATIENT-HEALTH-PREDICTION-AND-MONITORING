# backend/trajectory_predictor.py
from datetime import datetime, timedelta

class TrajectoryPredictor:
    def __init__(self):
        # Critical thresholds that trigger a predictive warning
        self.CRITICAL_THRESHOLDS = {
            "heart_rate": {"max": 105, "min": 40},
            "systolic_bp": {"max": 150, "min": 90},
            "spo2": {"max": 100, "min": 92}
        }

    def _calculate_slope(self, y_values):
        """Calculates the trend slope using basic Linear Regression."""
        n = len(y_values)
        if n < 2:
            return 0, y_values[-1] if y_values else 0
            
        x_values = list(range(n)) # Days 1, 2, 3, etc.
        
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x_squared = sum(x ** 2 for x in x_values)
        
        # Prevent division by zero
        denominator = (n * sum_x_squared) - (sum_x ** 2)
        if denominator == 0:
            return 0, y_values[-1]
            
        slope = ((n * sum_xy) - (sum_x * sum_y)) / denominator
        intercept = (sum_y - (slope * sum_x)) / n
        
        return slope, intercept

    def predict_future_vitals(self, historical_data: list, days_ahead: int = 2):
        """
        Takes a list of dictionaries containing historical vitals.
        Returns the projected vitals for the next X days and any triggered warnings.
        """
        if len(historical_data) < 3:
            return {"status": "insufficient_data", "message": "Need at least 3 readings to predict trends."}

        # Extract individual arrays for the math
        hr_history = [d["heart_rate"] for d in historical_data]
        bp_history = [d["systolic_bp"] for d in historical_data]
        spo2_history = [d["spo2"] for d in historical_data]

        # Calculate the mathematical trajectory
        hr_slope, hr_intercept = self._calculate_slope(hr_history)
        bp_slope, bp_intercept = self._calculate_slope(bp_history)
        spo2_slope, spo2_intercept = self._calculate_slope(spo2_history)

        current_day_index = len(historical_data) - 1
        target_day_index = current_day_index + days_ahead

        # Predict the exact numbers for Day 5/6
        predicted_hr = int((hr_slope * target_day_index) + hr_intercept)
        predicted_bp = int((bp_slope * target_day_index) + bp_intercept)
        predicted_spo2 = int((spo2_slope * target_day_index) + spo2_intercept)

        alerts = []
        is_critical = False

        # Check if the future predictions cross the danger lines
        if predicted_hr >= self.CRITICAL_THRESHOLDS["heart_rate"]["max"]:
            alerts.append(f"HR trending toward CRITICAL high ({predicted_hr} BPM)")
            is_critical = True
        
        if predicted_bp >= self.CRITICAL_THRESHOLDS["systolic_bp"]["max"]:
            alerts.append(f"BP trending toward CRITICAL hypertension ({predicted_bp} mmHg)")
            is_critical = True
            
        if predicted_spo2 <= self.CRITICAL_THRESHOLDS["spo2"]["min"]:
            alerts.append(f"SpO2 trending toward DANGEROUS hypoxia ({predicted_spo2}%)")
            is_critical = True

        return {
            "status": "success",
            "current_trajectory": {
                "heart_rate_slope": round(hr_slope, 2),
                "bp_slope": round(bp_slope, 2),
                "spo2_slope": round(spo2_slope, 2)
            },
            "predicted_vitals": {
                "days_ahead": days_ahead,
                "heart_rate": predicted_hr,
                "systolic_bp": predicted_bp,
                "spo2": predicted_spo2
            },
            "predictive_alerts": alerts,
            "is_critical_trajectory": is_critical
        }

# Instantiate the engine
trajectory_engine = TrajectoryPredictor()