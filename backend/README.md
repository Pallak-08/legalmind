See the main project README at [`../README.md`](../README.md).

Quick commands:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then paste GROQ_API_KEY

uvicorn app.main:app --reload --port 8000  # serve
pytest tests/                              # unit tests
python -m tests.eval                       # retrieval eval (no Groq key needed)
```
