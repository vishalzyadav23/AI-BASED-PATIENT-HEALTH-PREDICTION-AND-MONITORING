# backend/timeseries_analysis.py
"""
Advanced Time-Series Analysis with ARIMA Forecasting for Patient Health Trends
Provides 24h, 7d, 30d trend analysis and predictions
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import numpy as np
from collections import deque

class TimeSeriesAnalyzer:
    """
    Time-series analysis with ARIMA-inspired forecasting for health vitals
    """
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.readings_history = deque(maxlen=window_size)
    
    def add_reading(self, timestamp: datetime, vital_name: str, value: float):
        """Add a new vital reading to history"""
        self.readings_history.append({
            "timestamp": timestamp,
            "vital": vital_name,
            "value": value
        })
    
    def get_trend_analysis(self, readings: List[Dict], vital_name: str, hours: int = 24) -> Dict:
        """
        Analyze trend for a vital sign over specified hours
        Returns trend direction, slope, volatility, and ARIMA forecast
        """
        if not readings:
            return {"error": "No readings available"}
        
        # Filter readings for the vital and timeframe
        now = datetime.now()
        cutoff_time = now - timedelta(hours=hours)
        
        filtered = [
            r for r in readings 
            if r.get("vital") == vital_name and r.get("timestamp") >= cutoff_time
        ]
        
        if len(filtered) < 3:
            return {"error": f"Insufficient data for {vital_name} in {hours}h period"}
        
        values = np.array([r["value"] for r in filtered])
        timestamps = [r["timestamp"] for r in filtered]
        
        # Calculate trend metrics
        trend_data = {
            "vital": vital_name,
            "period_hours": hours,
            "data_points": len(filtered),
            "readings": values.tolist(),
            "timestamps": [str(t) for t in timestamps],
        }
        
        # 1. Mean and Std Dev
        trend_data["mean"] = float(np.mean(values))
        trend_data["std_dev"] = float(np.std(values))
        trend_data["min"] = float(np.min(values))
        trend_data["max"] = float(np.max(values))
        
        # 2. Trend Direction (Linear Regression Slope)
        x = np.arange(len(values))
        slope = self._calculate_slope(x, values)
        trend_data["slope"] = float(slope)
        
        if slope > 0.5:
            trend_data["trend"] = "INCREASING"
            trend_data["trend_severity"] = "HIGH" if slope > 2 else "MODERATE"
        elif slope < -0.5:
            trend_data["trend"] = "DECREASING"
            trend_data["trend_severity"] = "HIGH" if slope < -2 else "MODERATE"
        else:
            trend_data["trend"] = "STABLE"
            trend_data["trend_severity"] = "LOW"
        
        # 3. Volatility (Coefficient of Variation)
        if trend_data["mean"] != 0:
            trend_data["volatility"] = float(abs(trend_data["std_dev"] / trend_data["mean"]))
        else:
            trend_data["volatility"] = 0.0
        
        trend_data["volatility_level"] = "HIGH" if trend_data["volatility"] > 0.15 else "MODERATE" if trend_data["volatility"] > 0.08 else "LOW"
        
        # 4. ARIMA-inspired Forecast (next 6 readings)
        forecast = self._arima_forecast(values, steps=6)
        trend_data["forecast_next_6"] = forecast["predictions"]
        trend_data["forecast_upper_bound"] = forecast["upper"]
        trend_data["forecast_lower_bound"] = forecast["lower"]
        trend_data["forecast_confidence"] = forecast["confidence"]
        
        # 5. Rate of Change (latest vs oldest)
        if len(values) >= 2:
            roc = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
            trend_data["rate_of_change_percent"] = float(roc)
        
        # 6. Clinical Alert based on trend
        trend_data["clinical_alert"] = self._generate_trend_alert(trend_data, vital_name)
        
        return trend_data
    
    def _calculate_slope(self, x: np.ndarray, y: np.ndarray) -> float:
        """Calculate linear regression slope"""
        if len(x) < 2:
            return 0.0
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean) ** 2)
        if denominator == 0:
            return 0.0
        return numerator / denominator
    
    def _arima_forecast(self, values: np.ndarray, steps: int = 6) -> Dict:
        """
        Simple ARIMA-inspired forecasting using exponential smoothing + differencing
        Returns predictions with confidence intervals
        """
        if len(values) < 3:
            return {
                "predictions": [float(values[-1])] * steps,
                "upper": [float(values[-1] * 1.1)] * steps,
                "lower": [float(values[-1] * 0.9)] * steps,
                "confidence": 0.5
            }
        
        # Calculate differences (D=1)
        diffs = np.diff(values)
        
        # Exponential smoothing of differences
        alpha = 0.3
        smoothed_diff = diffs[0]
        for diff in diffs[1:]:
            smoothed_diff = alpha * diff + (1 - alpha) * smoothed_diff
        
        # Forecast
        predictions = []
        last_value = values[-1]
        
        for i in range(steps):
            # Add smoothed trend
            next_value = last_value + smoothed_diff
            predictions.append(float(next_value))
            last_value = next_value
        
        # Calculate prediction intervals (95% confidence)
        std_error = np.std(diffs) if len(diffs) > 0 else np.std(values) * 0.1
        
        upper = [p + 1.96 * std_error for p in predictions]
        lower = [p - 1.96 * std_error for p in predictions]
        
        return {
            "predictions": predictions,
            "upper": upper,
            "lower": lower,
            "confidence": 0.95
        }
    
    def _generate_trend_alert(self, trend_data: Dict, vital_name: str) -> Dict:
        """Generate clinical alert based on trend analysis"""
        alerts = []
        
        # Check trend severity
        if trend_data["trend"] == "INCREASING" and trend_data["trend_severity"] == "HIGH":
            if vital_name in ["heart_rate", "systolic_bp", "temperature"]:
                alerts.append({
                    "type": "RAPID_INCREASE",
                    "severity": "WARNING",
                    "message": f"{vital_name} rapidly increasing - monitor closely"
                })
        
        elif trend_data["trend"] == "DECREASING" and trend_data["trend_severity"] == "HIGH":
            if vital_name in ["spo2", "diastolic_bp"]:
                alerts.append({
                    "type": "RAPID_DECREASE",
                    "severity": "WARNING",
                    "message": f"{vital_name} rapidly decreasing - immediate action needed"
                })
        
        # Check volatility
        if trend_data["volatility_level"] == "HIGH":
            alerts.append({
                "type": "HIGH_VOLATILITY",
                "severity": "CAUTION",
                "message": f"{vital_name} showing high variability"
            })
        
        # Check if forecast goes out of bounds
        normal_ranges = {
            "heart_rate": (60, 100),
            "spo2": (95, 100),
            "temperature": (36.5, 37.5),
            "systolic_bp": (90, 130),
            "diastolic_bp": (60, 85),
            "respiratory_rate": (12, 20)
        }
        
        if vital_name in normal_ranges:
            min_val, max_val = normal_ranges[vital_name]
            forecast_values = trend_data["forecast_next_6"]
            
            if any(v > max_val for v in forecast_values):
                alerts.append({
                    "type": "FORECAST_EXCEED_UPPER",
                    "severity": "WARNING",
                    "message": f"Forecast predicts {vital_name} will exceed upper limit"
                })
            
            if any(v < min_val for v in forecast_values):
                alerts.append({
                    "type": "FORECAST_EXCEED_LOWER",
                    "severity": "WARNING",
                    "message": f"Forecast predicts {vital_name} will drop below lower limit"
                })
        
        return alerts if alerts else {"type": "NORMAL", "severity": "INFO", "message": "Trend within expected parameters"}
    
    def get_multi_vital_trend(self, readings: List[Dict], hours: int = 24) -> Dict:
        """Get trend analysis for all vitals in the reading"""
        vitals_to_analyze = ["heart_rate", "spo2", "temperature", "systolic_bp", "diastolic_bp", "respiratory_rate"]
        
        trends = {}
        for vital in vitals_to_analyze:
            trend = self.get_trend_analysis(readings, vital, hours)
            if "error" not in trend:
                trends[vital] = trend
        
        # Overall trend summary
        summary = {
            "period_hours": hours,
            "analysis_timestamp": datetime.now().isoformat(),
            "vital_trends": trends,
            "overall_status": "STABLE"
        }
        
        # Calculate overall status
        critical_alerts = sum(
            1 for vital_data in trends.values()
            for alert in (vital_data.get("clinical_alert", []) if isinstance(vital_data.get("clinical_alert"), list) else [vital_data.get("clinical_alert", {})])
            if alert.get("severity") == "WARNING"
        )
        
        if critical_alerts >= 2:
            summary["overall_status"] = "CRITICAL"
        elif critical_alerts >= 1:
            summary["overall_status"] = "WARNING"
        
        return summary


# Global instance
trend_analyzer = TimeSeriesAnalyzer()
