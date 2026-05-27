# sensor_processor.py - Real-time Sensor Data Processing & Validation

from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class SensorReading:
    """Represents a single sensor reading"""
    timestamp: datetime
    heart_rate: int
    spo2: int
    temperature: float
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    respiratory_rate: Optional[int] = None
    patient_id: Optional[int] = None


@dataclass
class SensorAlert:
    """Represents a sensor-based alert"""
    timestamp: datetime
    alert_level: AlertLevel
    message: str
    affected_vital: str
    reading_value: float
    normal_range: Tuple[float, float]
    anomaly_type: str  # "out_of_range", "rapid_change", "flatline", "spike"


class SensorValidator:
    """Validates incoming sensor data for correctness and plausibility"""
    
    # Valid ranges for sensor readings
    VALID_RANGES = {
        "heart_rate": (30, 200),      # BPM
        "spo2": (50, 100),            # Percentage
        "temperature": (30, 42),      # Celsius
        "systolic_bp": (60, 200),     # mmHg
        "diastolic_bp": (30, 120),    # mmHg
        "respiratory_rate": (5, 40)   # Breaths per minute
    }
    
    # Normal ranges for alerts
    NORMAL_RANGES = {
        "heart_rate": (60, 100),
        "spo2": (95, 100),
        "temperature": (36.5, 37.5),
        "systolic_bp": (90, 120),
        "diastolic_bp": (60, 80),
        "respiratory_rate": (12, 20)
    }
    
    @staticmethod
    def validate_reading(reading: Dict) -> Tuple[bool, List[str]]:
        """
        Validate sensor reading data.
        Returns (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        required_fields = ["heart_rate", "spo2", "temperature"]
        for field in required_fields:
            if field not in reading:
                errors.append(f"Missing required field: {field}")
        
        # Validate ranges
        for vital, (min_val, max_val) in SensorValidator.VALID_RANGES.items():
            if vital in reading:
                value = reading[vital]
                if not isinstance(value, (int, float)):
                    errors.append(f"{vital} must be numeric")
                elif value < min_val or value > max_val:
                    errors.append(f"{vital} {value} outside valid range ({min_val}-{max_val})")
        
        return len(errors) == 0, errors


class AnomalyDetector:
    """Detects anomalies in sensor readings using statistical methods"""
    
    def __init__(self, window_size: int = 10):
        """
        Initialize anomaly detector.
        window_size: Number of recent readings to maintain for comparison
        """
        self.window_size = window_size
        self.reading_history = {
            "heart_rate": [],
            "spo2": [],
            "temperature": [],
            "systolic_bp": [],
            "diastolic_bp": []
        }
    
    def add_reading(self, reading: SensorReading) -> None:
        """Add a reading to history for anomaly detection"""
        self.reading_history["heart_rate"].append(reading.heart_rate)
        self.reading_history["spo2"].append(reading.spo2)
        self.reading_history["temperature"].append(reading.temperature)
        
        if reading.systolic_bp:
            self.reading_history["systolic_bp"].append(reading.systolic_bp)
        if reading.diastolic_bp:
            self.reading_history["diastolic_bp"].append(reading.diastolic_bp)
        
        # Keep only recent readings
        for vital in self.reading_history:
            if len(self.reading_history[vital]) > self.window_size:
                self.reading_history[vital].pop(0)
    
    def detect_anomalies(self, reading: SensorReading) -> List[Tuple[str, str, float]]:
        """
        Detect anomalies in current reading.
        Returns list of (vital_name, anomaly_type, severity_score)
        """
        anomalies = []
        
        # Check for rapid changes (delta from previous reading)
        if len(self.reading_history["heart_rate"]) > 1:
            hr_delta = abs(reading.heart_rate - self.reading_history["heart_rate"][-1])
            if hr_delta > 30:  # HR change > 30 BPM in short time
                anomalies.append(("heart_rate", "rapid_change", min(1.0, hr_delta / 50)))
        
        if len(self.reading_history["spo2"]) > 1:
            spo2_delta = abs(reading.spo2 - self.reading_history["spo2"][-1])
            if spo2_delta > 5:  # SpO2 change > 5% in short time
                anomalies.append(("spo2", "rapid_change", min(1.0, spo2_delta / 10)))
        
        if len(self.reading_history["temperature"]) > 1:
            temp_delta = abs(reading.temperature - self.reading_history["temperature"][-1])
            if temp_delta > 0.5:  # Temp change > 0.5°C in short time
                anomalies.append(("temperature", "rapid_change", min(1.0, temp_delta / 1.0)))
        
        # Check for statistical outliers using Z-score
        if len(self.reading_history["heart_rate"]) > 3:
            anomalies.extend(self._check_zscore_anomaly(
                "heart_rate", reading.heart_rate, threshold=2.5
            ))
        
        if len(self.reading_history["spo2"]) > 3:
            anomalies.extend(self._check_zscore_anomaly(
                "spo2", reading.spo2, threshold=2.5
            ))
        
        if len(self.reading_history["temperature"]) > 3:
            anomalies.extend(self._check_zscore_anomaly(
                "temperature", reading.temperature, threshold=2.5
            ))
        
        return anomalies
    
    def _check_zscore_anomaly(self, vital: str, value: float, threshold: float = 2.5) -> List[Tuple[str, str, float]]:
        """Check if value is an outlier using Z-score method"""
        history = self.reading_history[vital]
        
        if len(history) < 3:
            return []
        
        mean = statistics.mean(history)
        stdev = statistics.stdev(history) if len(history) > 1 else 0
        
        if stdev == 0:
            return []
        
        zscore = abs((value - mean) / stdev)
        
        if zscore > threshold:
            severity = min(1.0, zscore / (threshold * 2))
            return [(vital, "statistical_outlier", severity)]
        
        return []


class SensorDataProcessor:
    """Main processor for real-time sensor data"""
    
    def __init__(self):
        self.validator = SensorValidator()
        self.anomaly_detector = AnomalyDetector()
        self.alerts: List[SensorAlert] = []
        self.current_reading: Optional[SensorReading] = None
        self.reading_history: List[SensorReading] = []
        self.max_history_size = 1000
    
    def process_telemetry(self, data: Dict) -> Dict:
        """
        Process incoming telemetry data.
        Returns processed data with validation results and alerts.
        """
        result = {
            "status": "processed",
            "timestamp": datetime.now().isoformat(),
            "valid": False,
            "errors": [],
            "warnings": [],
            "alerts": [],
            "processed_data": None
        }
        
        # Validate data
        is_valid, errors = self.validator.validate_reading(data)
        result["valid"] = is_valid
        result["errors"] = errors
        
        if not is_valid:
            return result
        
        # Create sensor reading object
        reading = SensorReading(
            timestamp=datetime.now(),
            heart_rate=int(data["heart_rate"]),
            spo2=int(data["spo2"]),
            temperature=float(data["temperature"]),
            systolic_bp=data.get("systolic_bp"),
            diastolic_bp=data.get("diastolic_bp"),
            respiratory_rate=data.get("respiratory_rate"),
            patient_id=data.get("patient_id")
        )
        
        # Detect anomalies
        anomalies = self.anomaly_detector.detect_anomalies(reading)
        
        # Generate alerts based on anomalies and out-of-range values
        new_alerts = self._generate_alerts(reading, anomalies)
        self.alerts.extend(new_alerts)
        
        result["alerts"] = [
            {
                "level": alert.alert_level.value,
                "message": alert.message,
                "vital": alert.affected_vital,
                "value": alert.reading_value,
                "range": alert.normal_range
            }
            for alert in new_alerts
        ]
        
        # Update history
        self.anomaly_detector.add_reading(reading)
        self.current_reading = reading
        self.reading_history.append(reading)
        
        # Keep history size manageable
        if len(self.reading_history) > self.max_history_size:
            self.reading_history.pop(0)
        
        result["processed_data"] = {
            "heart_rate": reading.heart_rate,
            "spo2": reading.spo2,
            "temperature": reading.temperature,
            "systolic_bp": reading.systolic_bp,
            "diastolic_bp": reading.diastolic_bp,
            "respiratory_rate": reading.respiratory_rate,
            "timestamp": reading.timestamp.isoformat()
        }
        
        return result
    
    def _generate_alerts(self, reading: SensorReading, anomalies: List) -> List[SensorAlert]:
        """Generate alerts based on reading values and anomalies"""
        alerts = []
        
        # Check each vital against normal ranges
        vitals_to_check = [
            ("heart_rate", reading.heart_rate, self.validator.NORMAL_RANGES["heart_rate"]),
            ("spo2", reading.spo2, self.validator.NORMAL_RANGES["spo2"]),
            ("temperature", reading.temperature, self.validator.NORMAL_RANGES["temperature"]),
        ]
        
        if reading.systolic_bp:
            vitals_to_check.append(("systolic_bp", reading.systolic_bp, self.validator.NORMAL_RANGES["systolic_bp"]))
        if reading.diastolic_bp:
            vitals_to_check.append(("diastolic_bp", reading.diastolic_bp, self.validator.NORMAL_RANGES["diastolic_bp"]))
        
        # Check out-of-range values
        for vital_name, value, (min_normal, max_normal) in vitals_to_check:
            if value < min_normal:
                severity = self._calculate_severity_low(vital_name, value, min_normal)
                alert_level = AlertLevel.CRITICAL if severity > 0.7 else AlertLevel.WARNING
                
                alerts.append(SensorAlert(
                    timestamp=datetime.now(),
                    alert_level=alert_level,
                    message=f"LOW: {vital_name} is {value} (normal: {min_normal}-{max_normal})",
                    affected_vital=vital_name,
                    reading_value=value,
                    normal_range=(min_normal, max_normal),
                    anomaly_type="below_range"
                ))
            elif value > max_normal:
                severity = self._calculate_severity_high(vital_name, value, max_normal)
                alert_level = AlertLevel.CRITICAL if severity > 0.7 else AlertLevel.WARNING
                
                alerts.append(SensorAlert(
                    timestamp=datetime.now(),
                    alert_level=alert_level,
                    message=f"HIGH: {vital_name} is {value} (normal: {min_normal}-{max_normal})",
                    affected_vital=vital_name,
                    reading_value=value,
                    normal_range=(min_normal, max_normal),
                    anomaly_type="above_range"
                ))
        
        # Check anomalies
        for vital, anomaly_type, severity in anomalies:
            if severity > 0.6:
                alert_level = AlertLevel.CRITICAL if severity > 0.8 else AlertLevel.WARNING
                
                alerts.append(SensorAlert(
                    timestamp=datetime.now(),
                    alert_level=alert_level,
                    message=f"ANOMALY: {vital} - {anomaly_type} (severity: {severity:.2f})",
                    affected_vital=vital,
                    reading_value=getattr(reading, vital),
                    normal_range=(0, 0),
                    anomaly_type=anomaly_type
                ))
        
        return alerts
    
    def _calculate_severity_low(self, vital: str, value: float, min_normal: float) -> float:
        """Calculate severity score for below-range value"""
        if vital == "spo2":
            if value < 85:
                return 1.0
            elif value < 90:
                return 0.8
            elif value < 94:
                return 0.4
        elif vital == "heart_rate":
            if value < 40:
                return 1.0
            elif value < 50:
                return 0.7
        elif vital == "temperature":
            if value < 35:
                return 0.9
            elif value < 36:
                return 0.5
        
        return (min_normal - value) / min_normal
    
    def _calculate_severity_high(self, vital: str, value: float, max_normal: float) -> float:
        """Calculate severity score for above-range value"""
        if vital == "spo2":
            return 0.0  # SpO2 above 100 is not severe
        elif vital == "heart_rate":
            if value > 150:
                return 0.8
            elif value > 120:
                return 0.4
        elif vital == "temperature":
            if value > 40:
                return 0.95
            elif value > 39:
                return 0.7
            elif value > 38.5:
                return 0.4
        elif vital == "systolic_bp":
            if value > 180:
                return 0.9
            elif value > 160:
                return 0.7
            elif value > 140:
                return 0.4
        
        return min(1.0, (value - max_normal) / max_normal)
    
    def get_current_reading(self) -> Optional[Dict]:
        """Get the most recent sensor reading"""
        if not self.current_reading:
            return None
        
        return {
            "timestamp": self.current_reading.timestamp.isoformat(),
            "heart_rate": self.current_reading.heart_rate,
            "spo2": self.current_reading.spo2,
            "temperature": self.current_reading.temperature,
            "systolic_bp": self.current_reading.systolic_bp,
            "diastolic_bp": self.current_reading.diastolic_bp,
            "respiratory_rate": self.current_reading.respiratory_rate
        }
    
    def get_recent_alerts(self, minutes: int = 5) -> List[Dict]:
        """Get alerts from the past N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_alerts = [
            a for a in self.alerts if a.timestamp > cutoff_time
        ]
        
        return [
            {
                "timestamp": alert.timestamp.isoformat(),
                "level": alert.alert_level.value,
                "message": alert.message,
                "vital": alert.affected_vital,
                "value": alert.reading_value
            }
            for alert in recent_alerts
        ]
    
    def get_reading_statistics(self, minutes: int = 5) -> Dict:
        """Get statistics on readings from the past N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_readings = [
            r for r in self.reading_history if r.timestamp > cutoff_time
        ]
        
        if not recent_readings:
            return {"message": "No readings in specified timeframe"}
        
        def calc_stats(values: List) -> Dict:
            if not values:
                return {}
            return {
                "min": min(values),
                "max": max(values),
                "avg": statistics.mean(values),
                "median": statistics.median(values)
            }
        
        heart_rates = [r.heart_rate for r in recent_readings]
        spo2_values = [r.spo2 for r in recent_readings]
        temps = [r.temperature for r in recent_readings]
        
        return {
            "reading_count": len(recent_readings),
            "timeframe_minutes": minutes,
            "heart_rate": calc_stats(heart_rates),
            "spo2": calc_stats(spo2_values),
            "temperature": calc_stats(temps),
            "timestamp": datetime.now().isoformat()
        }
    
    def check_patient_status(self) -> Dict:
        """Check overall patient status based on recent readings"""
        if not self.current_reading:
            return {"status": "NO_DATA"}
        
        recent_alerts = self.get_recent_alerts(minutes=1)
        critical_alerts = [a for a in recent_alerts if a["level"] == "CRITICAL"]
        warning_alerts = [a for a in recent_alerts if a["level"] == "WARNING"]
        
        if critical_alerts:
            overall_status = "CRITICAL"
        elif warning_alerts:
            overall_status = "WARNING"
        else:
            overall_status = "STABLE"
        
        return {
            "status": overall_status,
            "critical_alerts": len(critical_alerts),
            "warning_alerts": len(warning_alerts),
            "current_reading": self.get_current_reading(),
            "recent_alerts": recent_alerts[:5]  # Last 5 alerts
        }


# Global processor instance
sensor_processor = SensorDataProcessor()
