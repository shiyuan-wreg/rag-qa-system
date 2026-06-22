# Agent Console AI Service

Python FastAPI AI service for the Agent Console project.

## Features

- Function Calling with real tools (weather, calculator, email)
- Reflection mode: draft -> reflect -> revise
- Zhipu GLM LLM client
- Internal auth via X-Internal-Key header

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in your Zhipu API key.

## Run

```bash
python run.py
```

## API

- `GET /health` - Health check (no auth)
- `POST /agent/chat` - Agent chat (requires X-Internal-Key header)
