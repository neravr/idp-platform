import os
import json
import sys
import urllib.request
import urllib.error

def trigger_provision(config: dict):
    token  = os.environ["GITHUB_TOKEN"]
    owner  = os.environ["GITHUB_REPO_OWNER"]
    repo   = os.environ["GITHUB_REPO_NAME"]
    branch = os.environ.get("GITHUB_REF_NAME", "main")

    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/provision.yml/dispatches"

    payload = json.dumps({
        "ref": branch,
        "inputs": {
            "team_name":        config["team_name"],
            "environment_tier": config["environment_tier"],
            "app_template":     config["app_template"],
        }
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization":        f"Bearer {token}",
            "Accept":               "application/vnd.github+json",
            "Content-Type":         "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 204:
                print(f"provision.yml triggered successfully.")
                print(f"  Team:     {config['team_name']}")
                print(f"  Tier:     {config['environment_tier']}")
                print(f"  Template: {config['app_template']}")
            else:
                print(f"Unexpected status: {resp.status}")
                sys.exit(1)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"GitHub API error {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    raw = sys.stdin.read().strip()
    try:
        config = json.loads(raw)
    except json.JSONDecodeError:
        print(f"Invalid config JSON: {raw}", file=sys.stderr)
        sys.exit(1)
    trigger_provision(config)