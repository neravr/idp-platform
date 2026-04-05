import os
import json
import sys
import anthropic
from system_prompt import SYSTEM_PROMPT

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def parse_request(user_input: str, conversation: list = None) -> dict:
    messages = conversation or []
    messages.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    raw = response.content[0].text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        return {"status": "error", "raw": raw}

    messages.append({"role": "assistant", "content": raw})
    result["_messages"] = messages
    return result


def run():
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        print("IDP AI Provisioner - describe the environment you need:")
        user_input = input("> ").strip()

    conversation = []
    max_turns = 3

    for turn in range(max_turns):
        result = parse_request(user_input, conversation)
        conversation = result.get("_messages", conversation)

        if result["status"] == "ready":
            config = result["config"]
            print(json.dumps(config))
            return config

        elif result["status"] == "clarify":
            if len(sys.argv) > 1:
                print(f"CLARIFICATION_NEEDED: {result['question']}", file=sys.stderr)
                sys.exit(2)
            else:
                print(f"\n{result['question']}")
                user_input = input("> ").strip()

        elif result["status"] == "off_topic":
            print(f"Not understood: {result.get('message', '')}")
            sys.exit(1)

    print("Could not parse request. Use provision.yml directly.")
    sys.exit(1)


if __name__ == "__main__":
    run()