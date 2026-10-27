"""Isolation Forest energy analysis and optional Azure OpenAI reporting."""
import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

EMISSION_FACTOR = 0.233  # kg CO2e / kWh — make reporting boundary explicit


def demo_dataset():
    rng = np.random.default_rng(42)
    timestamps = pd.date_range(datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(days=13), periods=336, freq="h")
    hour, weekday = timestamps.hour.to_numpy(), timestamps.dayofweek.to_numpy()
    profile = 1.05 + .18 * ((hour >= 7) & (hour <= 9)) + .42 * ((hour >= 18) & (hour <= 22)) + .12 * (weekday < 5)
    use = np.maximum(.35, profile + rng.normal(0, .09, len(timestamps)))
    for i, surge in {43: 2.3, 106: 1.8, 204: 2.8, 288: 2.1, 311: 1.7}.items(): use[i] += surge
    return pd.DataFrame({"timestamp": timestamps, "consumption_kwh": use.round(3)})


def prepare_dataframe(frame):
    columns = {str(c).strip().lower().replace(" ", "_"): c for c in frame.columns}
    energy_col = next((columns[k] for k in ("consumption_kwh", "energy_kwh", "global_active_power", "kwh", "consumption") if k in columns), None)
    if not energy_col: raise ValueError("CSV needs consumption_kwh, energy_kwh, kwh, or consumption.")
    time_col = next((columns[k] for k in ("timestamp", "datetime", "date_time", "date") if k in columns), None)
    data = pd.DataFrame({"consumption_kwh": pd.to_numeric(frame[energy_col], errors="coerce")}).dropna()
    data["timestamp"] = pd.to_datetime(frame.loc[data.index, time_col], errors="coerce") if time_col else pd.date_range(datetime.now() - timedelta(hours=len(data)), periods=len(data), freq="h")
    data = data.dropna().sort_values("timestamp").reset_index(drop=True)
    if len(data) < 12: raise ValueError("Please provide at least 12 valid energy readings.")
    return data


def analyze(frame, contamination=.04):
    data = prepare_dataframe(frame)
    data["hour"], data["day_of_week"] = data.timestamp.dt.hour, data.timestamp.dt.dayofweek
    features = data[["consumption_kwh", "hour", "day_of_week"]]
    model = IsolationForest(n_estimators=250, contamination=min(max(float(contamination), .01), .2), random_state=42)
    data["is_anomaly"] = model.fit_predict(features) == -1
    data["anomaly_score"] = -model.score_samples(features)
    baseline = float(data.loc[~data.is_anomaly, "consumption_kwh"].median())
    data["excess_kwh"] = np.where(data.is_anomaly, np.maximum(data.consumption_kwh - baseline, 0), 0)
    anomalies = data[data.is_anomaly].sort_values("anomaly_score", ascending=False)
    total, excess = float(data.consumption_kwh.sum()), float(data.excess_kwh.sum())
    return data, anomalies, {"total_rows": len(data), "anomaly_count": len(anomalies), "baseline_kwh": baseline, "total_kwh": total, "carbon_kg": total * EMISSION_FACTOR, "avoidable_carbon_kg": excess * EMISSION_FACTOR}


def sustainability_report(anomalies, summary):
    peak = anomalies.iloc[0] if not anomalies.empty else None
    timing = peak.timestamp.strftime("%a %d %b at %H:%M") if peak is not None else "the measured period"
    fallback = (f"This analysis reviewed {summary['total_rows']} meter readings and flagged {summary['anomaly_count']} unusual consumption events. Total use was {summary['total_kwh']:.1f} kWh, equivalent to {summary['carbon_kg']:.1f} kg CO2e using the configured grid factor. The largest event occurred {timing}. The anomalous demand represents an estimated {summary['avoidable_carbon_kg']:.1f} kg CO2e reduction opportunity. Prioritise checking overnight baseload, HVAC schedules, and equipment left running after occupancy; then compare the next reporting period against this baseline.")
    keys = ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_CHAT_DEPLOYMENT")
    if not all(os.getenv(key) for key in keys): return fallback
    try:
        from openai import AzureOpenAI
        client = AzureOpenAI(azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"], api_key=os.environ["AZURE_OPENAI_API_KEY"], api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"))
        result = client.chat.completions.create(model=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"], temperature=.25, messages=[{"role": "system", "content": "You are an EU energy-reporting sustainability analyst."}, {"role": "user", "content": f"Write a concise, plain-English energy sustainability update with three actions. Use only these estimated facts: {summary}; highest events: {anomalies[['timestamp','consumption_kwh','excess_kwh']].head(3).to_dict('records')}"}])
        return result.choices[0].message.content.strip() or fallback
    except Exception: return fallback
