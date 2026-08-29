# Self-Healing Jenkins Pipeline with AI-Powered Failure Diagnosis

A CI/CD pipeline that doesn't just fail silently — when a build breaks, it
automatically diagnoses *why* using the Claude API, and posts the diagnosis
straight to Slack within seconds.

## Why this exists

Most CI pipelines stop at "build failed — go read the logs." That's fine for
experienced engineers, but it costs time even then. This project explores a
small AIOps pattern: let an LLM read the failure log the moment it happens
and hand back a plain-English diagnosis and suggested fix, before a human
even opens the console output.

## Architecture

```
   git push
      |
      v
 +-----------+     +------------------+     +-------------------+
 |  Jenkins  | --> |  Build & Test    | --> |  Docker Image      |
 |  Pipeline |     |  (pytest)        |     |  Build             |
 +-----------+     +------------------+     +-------------------+
      |
      | on failure
      v
 +------------------+     +------------------+     +--------------+
 |  Extract error    | --> |  Claude API      | --> |  Slack       |
 |  log tail         |     |  (diagnosis)     |     |  notification|
 +------------------+     +------------------+     +--------------+
```

## Stack

- **Jenkins** — CI/CD orchestration (Declarative Pipeline)
- **Docker** — containerizing the demo app
- **Python / Flask** — the demo application under test
- **pytest** — test runner (one test is intentionally fragile for demo purposes)
- **Claude API (Anthropic)** — failure diagnosis
- **Slack Incoming Webhooks** — notification delivery

## How it works

1. A commit triggers the Jenkins pipeline.
2. The pipeline installs dependencies, runs tests, and builds a Docker image.
3. If any stage fails, Jenkins' `post { failure { ... } }` block runs
   `scripts/diagnose_failure.py`.
4. That script pulls the build's console log via the Jenkins REST API,
   extracts the last ~50 lines (where the actual error almost always is),
   and sends it to Claude with a scoped prompt asking for a diagnosis and a
   concrete fix.
5. The diagnosis is posted to a Slack channel automatically — no one has to
   go looking for it.

## Running it locally

1. Start Jenkins in Docker:
   ```bash
   docker run -d -p 8080:8080 -p 50000:50000 --name jenkins \
     -v jenkins_home:/var/jenkins_home \
     -v /var/run/docker.sock:/var/run/docker.sock \
     jenkins/jenkins:lts
   ```
2. Unlock Jenkins at `http://localhost:8080`, install suggested plugins,
   create an admin user.
3. Add two credentials in Jenkins (Manage Jenkins → Credentials):
   `ANTHROPIC_API_KEY` and `SLACK_WEBHOOK_URL`.
4. Create a Pipeline job pointing at this repo, with **Script Path** set to
   `Jenkinsfile`.
5. Click **Build Now**.

## Triggering a failure (for demo purposes)

Edit the message string in `app.py` so it no longer matches what
`test_app.py` expects, then commit and push. The next build will fail on
purpose, and the Slack message should appear within seconds of the failure.

## Demo

[Loom walkthrough link here]

## What I'd add next

- Auto-create a GitHub issue with the diagnosis, in addition to Slack
- Categorize failures (dependency error vs test failure vs build error) so
  the diagnosis prompt can be tailored per category
- Extend the pipeline to deploy to a local Kubernetes cluster (Minikube)
  after a successful build

---

Built by Leo — DevOps Engineer (Jenkins, Kubernetes, Chef) currently
pursuing AWS Certified DevOps Engineer – Professional.
