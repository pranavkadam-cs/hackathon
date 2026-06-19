# Multi-Modal Evidence Review — Solution

## Overview

A damage claim verification system that analyzes images and claim transcripts to determine whether submitted evidence supports, contradicts, or is insufficient for each claim.

## Architecture

```
claims.csv + images + user_history.csv + evidence_requirements.csv
         ↓
   pipeline.py  (Gemini vision — primary)
         OR
   inference_engine.py  (NLP fallback — used when vision API quota unavailable)
         ↓
   output.csv
         ↓
   evaluation/evaluate.py  →  evaluation/evaluation_report.md
```

## Files

| File | Purpose |
|---|---|
| `pipeline.py` | Primary pipeline using Gemini 2.0 Flash vision API |
| `inference_engine.py` | NLP-based fallback using keyword extraction |
| `evaluation/evaluate.py` | Evaluates predictions against sample ground truth |
| `evaluation/sample_output.csv` | Predictions on sample_claims.csv |
| `evaluation/evaluation_report.md` | Operational analysis and accuracy report |
| `output.csv` | Final predictions for claims.csv |
| `dataset/` | CSVs and images |

## Setup

```bash
pip install google-genai pillow
export GOOGLE_API_KEY=your_key_here
```

## Run

```bash
# Run vision pipeline (requires GOOGLE_API_KEY with available quota)
python3 pipeline.py          # processes dataset/claims.csv → output.csv
python3 pipeline.py sample   # processes sample_claims.csv → evaluation/sample_output.csv

# Run NLP fallback (no API key required)
python3 inference_engine.py          # → output.csv
python3 inference_engine.py sample   # → evaluation/sample_output.csv

# Evaluate against ground truth
python3 evaluation/evaluate.py
```

## Vision Pipeline Design

- **Model**: `gemini-2.0-flash` (multimodal, vision-capable)
- **One call per claim**: all images bundled in a single multi-part request
- **Structured JSON output**: strict schema with sanitization against allowed value sets
- **Retry strategy**: exponential backoff (5s, 10s, 20s, 40s), max 4 attempts
- **Rate limiting**: 1.5s inter-call delay on paid tier; auto-increases on 429

## Security

- Prompt explicitly instructs the model to detect and ignore embedded text instructions in images
- `text_instruction_present` flag is raised for any claim/image containing override attempts
- User history adds risk context only — cannot override visual evidence

## NLP Fallback Accuracy (on sample_claims.csv)

| Field | Accuracy |
|---|---|
| claim_status | ~75% |
| object_part | ~80% |
| evidence_standard_met | ~85% |
| valid_image | ~85% |

The remaining ~25% of claim_status errors are inherently vision-dependent (e.g., user claims "shattered" but image shows scratch — only the vision model can detect this mismatch).
