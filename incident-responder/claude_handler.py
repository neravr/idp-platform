import os
import json
import anthropic
from system_prompt import SYSTEM_PROMPT

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def analyze_alert(alert: dict) -> dict:
    """
    Takes a Prometheus AlertManager alert dict and returns
    Claude's analysis as a structured dict.
    """
    # Extract key fields from the alert
    alert_name = alert.get("labels", {}).get("alertname", "Unknown")
    severity    = alert.get("labels", {}).get("severity", "unknown")
    namespace   = alert.get("labels", {}).get("namespace", "unknown")
    pod         = alert.get("labels", {}).get("pod", "unknown")
    node        = alert.get("labels", {}).get("node", "unknown")
    instance    = alert.get("labels", {}).get("instance", "unknown")
    summary     = alert.get("annotations", {}).get("summary", "No summary provided")
    description = alert.get("annotations", {}).get("description", "No description provided")
    starts_at   = alert.get("startsAt", "unknown")

    user_message = f"""
Alert received from Prometheus AlertManager:

Alert name:  {alert_name}
Severity:    {severity}
Namespace:   {namespace}
Pod:         {pod}
Node:        {node}
Instance:    {instance}
Started at:  {starts_at}

Summary:     {summary}
Description: {description}

Raw labels: {json.dumps(alert.get("labels", {}), indent=2)}
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "summary": f"Alert received: {alert_name}",
            "impact": "Could not parse AI response",
            "severity": severity,
            "investigation_steps": [],
            "raw_response": raw
        }