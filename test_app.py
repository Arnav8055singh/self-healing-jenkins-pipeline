from app import app


def test_home():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_health():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200


# This test checks exact wording. For your demo, break it on purpose by
# changing the message in app.py (e.g. typo the string) — that mismatch
# will fail this test and trigger the pipeline's failure/diagnosis path.
def test_message_content():
    client = app.test_client()
    response = client.get("/")
    assert "Self-Healing Pipeline Demo" in response.json["message"]
