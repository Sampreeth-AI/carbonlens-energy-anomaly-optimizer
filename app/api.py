import io
import pandas as pd
from flask import Blueprint, jsonify, request
from app import db
from app.models import EnergyRun
from app.services.energy import analyze, demo_dataset, sustainability_report

api = Blueprint("api", __name__)


@api.get("/health")
def health(): return {"status": "ok", "service": "carbonlens-energy-optimizer"}


@api.get("/latest")
def latest():
    run = EnergyRun.query.order_by(EnergyRun.id.desc()).first()
    return jsonify(run.to_dict() if run else None)


def run_analysis(frame, source):
    data, anomalies, summary = analyze(frame)
    report = sustainability_report(anomalies, summary)
    run = EnergyRun(source_name=source, report=report, **summary)
    db.session.add(run); db.session.commit()
    points = [{"timestamp": row.timestamp.strftime("%d %b %H:%M"), "consumption": round(row.consumption_kwh, 2), "anomaly": bool(row.is_anomaly)} for row in data.tail(96).itertuples()]
    events = [{"timestamp": row.timestamp.strftime("%d %b %Y · %H:%M"), "consumption": round(row.consumption_kwh, 2), "excess": round(row.excess_kwh, 2), "score": round(row.anomaly_score, 3)} for row in anomalies.head(8).itertuples()]
    return jsonify({"run": run.to_dict(), "points": points, "events": events})


@api.post("/demo")
def demo(): return run_analysis(demo_dataset(), "14-day smart-meter demo")


@api.post("/analyze")
def upload():
    file = request.files.get("file")
    if not file or not file.filename.lower().endswith(".csv"): return jsonify({"error": "Please upload a CSV file."}), 400
    try:
        frame = pd.read_csv(io.BytesIO(file.read()))
        return run_analysis(frame, file.filename)
    except ValueError as error: return jsonify({"error": str(error)}), 400
    except Exception: return jsonify({"error": "The file could not be processed as an energy CSV."}), 400
