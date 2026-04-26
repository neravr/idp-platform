import os
import json
import urllib.request
import urllib.error

SEVERITY_EMOJI = {
    "critical": "🔴",
    "warning":  "🟡",
    "info":     "🔵",
}

def send_slack_notification(alert: dict, analysis: dict) -> bool:
    """
    Sends a formatted Slack message with the alert details
    and Claude's analysis.
    """
    webhook_url = os.environ["SLACK_WEBHOOK_URL"]

    alert_name  = alert.get("labels", {}).get("alertname", "Unknown")
    namespace   = alert.get("labels", {}).get("namespace", "unknown")
    pod         = alert.get("labels", {}).get("pod", "unknown")
    severity    = analysis.get("severity", "unknown")
    emoji       = SEVERITY_EMOJI.get(severity, "⚪")

    # Build investigation steps text
    steps_text = ""
    for step in analysis.get("investigation_steps", []):
        steps_text += f"*{step['step']}.* {step['description']}\n"
        if step.get("command"):
            steps_text += f"```{step['command']}```\n"

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {alert_name}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Severity:*\n{severity.upper()}"},
                    {"type": "mrkdwn", "text": f"*Namespace:*\n{namespace}"},
                    {"type": "mrkdwn", "text": f"*Pod:*\n{pod}"},
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*What's happening:*\n{analysis.get('summary', 'N/A')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Impact:*\n{analysis.get('impact', 'N/A')}"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Investigation steps:*\n{steps_text}"
                }
            }
        ]
    }

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        print(f"Slack error {e.code}: {e.read().decode()}")
        return False