# Document Insight

Document Insight is a document analysis workspace for records, compliance, and information-heavy environments.

## Overview
The application supports initial document triage by combining text extraction, sensitivity heuristics, and optional AI analysis. Users can upload a supported file, review extracted content, generate a structured summary, surface possible risk indicators, and download the resulting JSON output for downstream handling.

## Features
- Upload PDF, DOCX, TXT, MD, CSV, and JSON files
- Extract text for review
- Estimate document type from filename and content
- Detect potential sensitivity indicators using local heuristics
- Run AI analysis with Anthropic or OpenAI
- Return:
  - executive summary
  - key points
  - entities
  - risk flags
  - recommended actions
  - search tags
- Export structured analysis as JSON

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## API keys
You can either paste an API key into the sidebar or set an environment variable.

### PowerShell
```powershell
$env:ANTHROPIC_API_KEY="your_key_here"
# or
$env:OPENAI_API_KEY="your_key_here"
```
