.PHONY: run-backend test lint

run-backend:
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

test:
PYTHONPATH=backend pytest -q
