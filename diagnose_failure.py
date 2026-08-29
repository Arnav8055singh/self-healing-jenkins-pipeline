import sys
import os
import requests

JENKINS_URL = os.environ.get("JENKINS_URL", "http://localhost:8080")
JENKINS_USER = os.environ.get("JENKINS_USER", "")
JENKINS_TOKEN = os.environ.get("JENKINS_API_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

GEMINI_MODEL = "gemini-3.6-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)


def get_console_log(job_name, build_number):
    url = f"{JENKINS_URL}/job/{job_name}/{build_number}/consoleText"
    auth = (JENKINS_USER, JENKINS_TOKEN) if JENKINS_USER else None
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response.text


def extract_error_snippet(log_text, max_lines=50):
    lines = log_text.strip().split("\n")
    return "\n".join(lines[-max_lines:])


def diagnose_with_gemini(error_snippet):
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "You are a DevOps assistant. A Jenkins CI build just "
                            "failed. Here is the tail of the console log:\n\n"
                            f"{error_snippet}\n\n"
                            "In 4-6 sentences: (1) diagnose what most likely "
                            "caused the failure, (2) suggest one concrete fix. "
                            "Be specific and concise."
                        )
                    }
                ]
            }
        ]
    }
    response = requests.post(
        GEMINI_URL,
        headers={"Content-Type": "application/json"},
        json=payload,
    )
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def send_to_slack(job_name, build_number, diagnosis):
    message = {
        "text": (
            f"*Build Failed:* `{job_name}` #{build_number}\n\n"
            f"*AI Diagnosis:*\n{diagnosis}"
        )
    }
    requests.post(SLACK_WEBHOOK_URL, json=message)


def main():
    job_name = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("JOB_NAME", "unknown-job")
    build_number = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("BUILD_NUMBER", "0")

    print(f"Diagnosing failure for {job_name} #{build_number}...")
    log_text = get_console_log(job_name, build_number)
    error_snippet = extract_error_snippet(log_text)
    diagnosis = diagnose_with_gemini(error_snippet)

    print("Diagnosis:\n", diagnosis)

    if SLACK_WEBHOOK_URL:
        send_to_slack(job_name, build_number, diagnosis)
        print("Sent diagnosis to Slack.")
    else:
        print("No SLACK_WEBHOOK_URL set -- diagnosis printed above only.")


if __name__ == "__main__":
    main()