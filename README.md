# TemporalCodeBuilder

A proof-of-concept CI/CD pipeline orchestrated by [Temporal](https://temporal.io/), using [LocalStack](https://localstack.cloud/) to emulate AWS infrastructure locally. The pipeline automatically detects code changes, runs tests, builds Docker images, and provisions infrastructure via Terraform — with support for both fully automatic and human-approval deployment modes.

---

## Architecture Overview

The project has three layers:

- **Workflows** — Temporal workflows define the overall pipeline logic and control flow
- **Activities** — Individual tasks (git, Python, Docker, Terraform) executed by the worker
- **Local Infrastructure** — Temporal server and LocalStack (AWS emulation) run via Docker Compose

**Execution Flow:**

```
Starter Script
    └─→ Temporal Server
            └─→ Worker (cicd_worker.py)
                    ├─→ check_for_changes     # Fetch & compare commits
                    ├─→ refresh_repo          # Clone or pull latest
                    ├─→ install_packages      # pip install
                    ├─→ perform_tests         # pytest
                    ├─→ build_image           # docker build
                    ├─→ terraform_plan        # tflocal init + plan
                    ├─→ [approval gate]       # Signal required (approval mode only)
                    ├─→ terraform_apply       # tflocal apply
                    └─→ notify_users          # Slack/Teams/etc. (placeholder)
```

---

## Project Structure

```
TemporalCodeBuilder/
├── builder/
│   ├── activities/
│   │   ├── git_acts.py          # check_for_changes, refresh_repo (GitPython)
│   │   ├── python_acts.py       # install_packages, build_image, perform_tests
│   │   ├── terraform_acts.py    # terraform_plan, terraform_apply (tflocal)
│   │   └── utitily_acts.py      # notify_users (placeholder)
│   └── workflows/
│       └── cicd_flow.py         # Main CicdWorkflow definition
│
├── approval_starter.py          # Start workflow with manual approval gate
├── autodeploy_starter.py        # Start workflow with automatic deployment
├── cicd_worker.py               # Worker process — registers and runs activities
├── compose.yaml                 # Docker Compose for Temporal + LocalStack
├── local_setup.sh               # One-shot local environment setup script
└── requirements.txt             # Python dependencies
```

---

## Prerequisites

- Python 3.12+
- Docker & Docker Compose
- A **LocalStack Pro** auth token set as `LS_AUTH_TOKEN` in your environment
  - LocalStack offers a [2-week free trial](https://localstack.cloud/)

All other dependencies (`temporalio`, `terraform-local`, `gitpython`) are installed by the setup script.

---

## Setup & Running

Start up steps (assuming root dir & Windows environment):

* Install required builder packages and start LocalStack and Temporal server:
    ```bash
    ./local_setup.sh
    ```
    This script will set up your virtual environment, install packages, and start required servers. The only dependency is `LS_AUTH_TOKEN`, which needs to be set in your environment to run the LocalStack Pro image.

* Start the worker in a terminal:
    ```bash
    python cicd_worker.py
    ```

* Submit jobs as needed:
    * For non-production/automatic environments there's a schedule version:
        ```bash
        python autodeploy_starter.py
        ```
        Every 5 minutes it searches for new changes and will automatically deploy as discovered.

    * For more controlled environments there is a one-off job for deploys that requires approval:
        ```bash
        python approval_starter.py
        ```
        In the Temporal UI a signal needs to be sent to continue the deploy after the plan stage to avoid unexpected changes from deploying. This signal has a 10-minute timeout to avoid state drift.

---

## Manual Approval Flow

When using `approval_starter.py`, the workflow pauses after `terraform_plan` and waits for an explicit approval signal before applying changes:

1. Open the **Temporal UI** at [http://localhost:8233](http://localhost:8233)
2. Find the running workflow (ID pattern: `total-build-<uuid>`)
3. Send a signal named `approve` with a payload containing the approver's name
4. The workflow will resume and execute `terraform_apply` followed by `notify_users`

> **Note:** If no signal is received within **10 minutes**, the workflow times out to prevent infrastructure state drift.

---

## Key Configuration

| Setting | Value |
|---|---|
| Temporal host | `localhost:7233` |
| Temporal UI | `http://localhost:8233` |
| Task queue | `cicd-queue` |
| LocalStack endpoint | `http://localhost:4566` |
| Approval timeout | 10 minutes |

---

## Dependencies

**Python packages** (`requirements.txt`):

| Package | Purpose |
|---|---|
| `temporalio` | Temporal Python SDK |
| `terraform-local` | `tflocal` CLI for LocalStack |
| `gitpython` | Git operations in Python |

**Docker services** (`compose.yaml`):

| Service | Image | Purpose |
|---|---|---|
| Temporal | `temporalio/temporal:latest` | Workflow orchestration server (ports 7233, 8233) |
| LocalStack | `localstack/localstack-pro:latest` | Local AWS emulation (port 4566) |
