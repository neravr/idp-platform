import os
import json
from fastapi import FastAPI, Request, HTTPException
from claude_handler import analyze_alert
from slack_notifier import send_slack_notification

app = FastAPI(title="IDP Incident Responder")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/webhook")
async def alertmanager_webhook(request: Request):
    """
    Receives AlertManager webhook POST requests.
    AlertManager sends a JSON body with a list of alerts.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    alerts = body.get("alerts", [])

    if not alerts:
        return {"message": "No alerts to process"}

    results = []

    for alert in alerts:
        alert_name = alert.get("labels", {}).get("alertname", "Unknown")
        status     = alert.get("status", "unknown")

        print(f"Processing alert: {alert_name} [{status}]")

        # Skip resolved alerts
        if status == "resolved":
            print(f"Skipping resolved alert: {alert_name}")
            results.append({"alert": alert_name, "status": "skipped_resolved"})
            continue

        # Get Claude's analysis
        try:
            analysis = analyze_alert(alert)
        except Exception as e:
            print(f"Claude analysis failed for {alert_name}: {e}")
            results.append({"alert": alert_name, "status": "analysis_failed", "error": str(e)})
            continue

        # Send to Slack
        sent = send_slack_notification(alert, analysis)

        results.append({
            "alert":    alert_name,
            "status":   "sent" if sent else "slack_failed",
            "severity": analysis.get("severity"),
            "summary":  analysis.get("summary"),
        })

    return {"processed": len(results), "results": results}


@app.post("/test")
async def test_alert(request: Request):
    """
    Test endpoint — send a fake alert to verify the pipeline works.
    """
    fake_alert = {
        "status": "firing",
        "labels": {
            "alertname":  "KubePodCrashLooping",
            "severity":   "critical",
            "namespace":  "payments",
            "pod":        "payments-api-7d9f8b-xk2p9",
            "container":  "payments-api",
        },
        "annotations": {
            "summary":     "Pod payments/payments-api-7d9f8b-xk2p9 is crash looping",
            "description": "Pod has restarted 8 times in the last 10 minutes"
        },
        "startsAt": "2026-04-26T10:00:00Z"
    }

    analysis = analyze_alert(fake_alert)
    sent     = send_slack_notification(fake_alert, analysis)

    return {
        "analysis": analysis,
        "slack_sent": sent
    }