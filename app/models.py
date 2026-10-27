"""Database models for saved energy analyses."""
from datetime import datetime
from app import db


class EnergyRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_name = db.Column(db.String(160), nullable=False, default="Demo smart-meter dataset")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total_rows = db.Column(db.Integer, nullable=False)
    anomaly_count = db.Column(db.Integer, nullable=False)
    baseline_kwh = db.Column(db.Float, nullable=False)
    total_kwh = db.Column(db.Float, nullable=False)
    carbon_kg = db.Column(db.Float, nullable=False)
    avoidable_carbon_kg = db.Column(db.Float, nullable=False)
    report = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {"id": self.id, "source_name": self.source_name, "created_at": self.created_at.strftime("%d %b %Y · %H:%M"), "total_rows": self.total_rows, "anomaly_count": self.anomaly_count, "baseline_kwh": round(self.baseline_kwh, 2), "total_kwh": round(self.total_kwh, 2), "carbon_kg": round(self.carbon_kg, 2), "avoidable_carbon_kg": round(self.avoidable_carbon_kg, 2), "report": self.report}
