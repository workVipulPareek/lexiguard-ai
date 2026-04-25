Get your key at: https://huggingface.co/settings/tokens

## Running the Application

Open two terminals with venv activated.

### Terminal 1 — Backend

```bash
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — Frontend

```bash
streamlit run ui/streamlit_app.py
```

Open browser at: http://localhost:8501

## Usage

1. Upload a `.txt` contract file using the UI
2. Type a question about the contract
3. Click **Analyze**
4. View:
   - Risk score (LOW / MEDIUM / HIGH)
   - Identified clause types
   - Compliance check results
   - Full analysis summary
   - Source clauses used for analysis

## API Endpoints

| Method | Endpoint  | Description              |
|--------|-----------|--------------------------|
| GET    | /         | Health check             |
| POST   | /upload   | Upload contract (.txt)   |
| POST   | /query    | Query uploaded contract  |

### Example API usage

```bash
# Upload
curl -X POST http://localhost:8000/upload \
  -F "file=@data/sample_contract.txt"

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the payment terms?", "filename": "sample_contract.txt"}'
```

## Agent Workflow