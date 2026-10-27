# CarbonLens — Energy Anomaly & Carbon Footprint Optimizer

A polished Flask dashboard that detects unusual building or household energy consumption with **Isolation Forest**, quantifies estimated carbon exposure, and creates a plain-English sustainability brief. It is designed as a portfolio project showing practical Python, Pandas, scikit-learn, Flask, and optional Azure OpenAI integration.

## What it does

- Analyses smart-meter CSV data using Isolation Forest across consumption, hour, and weekday features.
- Flags operational outliers and estimates excess kWh and avoidable CO2e.
- Produces an executive-ready sustainability update using Azure OpenAI when configured, with a robust local fallback.
- Includes a polished 14-day synthetic smart-meter demo, so the app works immediately after deployment.
- Provides Render Blueprint configuration plus a health endpoint.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

Open `http://127.0.0.1:5000`, then select **Run live demo**.

## CSV format

The energy column must be named `consumption_kwh`, `energy_kwh`, `kwh`, or `consumption`. Include `timestamp` (recommended); without it the app will construct an hourly timeline.

```csv
timestamp,consumption_kwh
2026-10-01 00:00:00,0.87
2026-10-01 01:00:00,0.82
2026-10-01 18:00:00,1.74
```

## Azure OpenAI (optional)

Set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, and `AZURE_OPENAI_CHAT_DEPLOYMENT` in `.env` or Render environment variables. No key is required for the dashboard or local narrative generator.

## Deploy to Render

1. Push this repository to GitHub.
2. In Render select **New → Blueprint**, connect the repo, and select `render.yaml`.
3. Optionally add the Azure OpenAI variables in the Render dashboard.

The SQLite database is ephemeral on Render's free filesystem; the app's analysis dashboard remains fully usable without persistence.

## Technical note

The default 0.233 kg CO2e/kWh factor is a demonstration value. Use the verified grid factor and reporting boundary required by your organisation before making regulated disclosures.
