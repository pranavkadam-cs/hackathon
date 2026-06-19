# Evaluation Report — Multi-Modal Evidence Review

## Approach

**Primary pipeline**: Google Gemini 2.0 Flash (vision API) — sends all images for a claim in a single multi-part request with a structured JSON prompt.

**NLP fallback** (`inference_engine.py`): deterministic keyword/rule extraction from claim transcript — used when vision API quota is unavailable.

---

## Accuracy on Sample Set (20 labeled examples)

| Field | Correct | Total | Accuracy |
|---|---|---|---|
| claim_status | 16 | 20 | 80.0% |
| issue_type | 14 | 20 | 70.0% |
| object_part | 19 | 20 | 95.0% |
| severity | 14 | 20 | 70.0% |
| evidence_standard_met | 18 | 20 | 90.0% |
| valid_image | 18 | 20 | 90.0% |
| risk_flags (overlap) | 14 | 20 | 70.0% |

> **Note**: remaining errors are inherently vision-dependent (e.g., user claims 'shattered' but image shows a scratch). Only the vision pipeline resolves these.

---

## Per-Row Detail

| user_id | object | status✓ | issue✓ | part✓ | sev✓ | gt_status | pred_status |
|---|---|---|---|---|---|---|---|
| user_001 | car | ✓ | ✓ | ✓ | ✓ | supported | supported |
| user_002 | car | ✓ | ✓ | ✓ | ✓ | supported | supported |
| user_004 | car | ✓ | ✓ | ✓ | ✓ | supported | supported |
| user_007 | car | ✓ | ✓ | ✓ | ✓ | supported | supported |
| user_005 | car | ✗ | ✗ | ✓ | ✗ | contradicted | not_enough_information |
| user_006 | car | ✗ | ✗ | ✓ | ✗ | not_enough_information | supported |
| user_003 | car | ✓ | ✓ | ✓ | ✓ | supported | supported |
| user_008 | car | ✓ | ✓ | ✓ | ✓ | supported | supported |
| user_009 | laptop | ✓ | ✓ | ✓ | ✓ | supported | supported |
| user_010 | laptop | ✓ | ✓ | ✗ | ✓ | supported | supported |
| user_011 | laptop | ✓ | ✓ | ✓ | ✗ | supported | supported |
| user_012 | laptop | ✓ | ✓ | ✓ | ✗ | supported | supported |
| user_018 | laptop | ✗ | ✗ | ✓ | ✗ | contradicted | supported |
| user_020 | laptop | ✓ | ✓ | ✓ | ✓ | not_enough_information | not_enough_information |
| user_015 | package | ✓ | ✓ | ✓ | ✓ | supported | supported |
| user_030 | package | ✓ | ✗ | ✓ | ✓ | supported | supported |
| user_031 | package | ✓ | ✓ | ✓ | ✓ | supported | supported |
| user_032 | package | ✓ | ✗ | ✓ | ✓ | not_enough_information | not_enough_information |
| user_033 | package | ✓ | ✓ | ✓ | ✓ | contradicted | contradicted |
| user_034 | package | ✗ | ✗ | ✓ | ✗ | contradicted | supported |

---

## Operational Analysis

### Model Calls

| Stage | Rows | Images | API Calls |
|---|---|---|---|
| Sample evaluation | 20 | 28 | 20 |
| Test set | 44 | 111 | 44 |
| **Total** | **64** | **139** | **64** |

Each claim = 1 API call. All images for the claim are bundled in a single multi-part request.

### Token Usage (estimated)

- Input per call: ~1,500 text tokens + ~800 tokens/image (1024px JPEG)
- Avg images/call: 2.2 → ~1,760 image tokens
- **Total input**: 64 × (1,500 + 1,760) ≈ **208,640 tokens**
- Output per call: ~300 tokens (structured JSON)
- **Total output**: 64 × 300 ≈ **19,200 tokens**

### Cost Estimate

| Item | Tokens | Rate | Cost |
|---|---|---|---|
| Input (text+image) | 208,640 | $0.075/1M | ~$0.016 |
| Output | 19,200 | $0.30/1M | ~$0.006 |
| **Total** | | | **~$0.022** |

> Pricing: Gemini 2.0 Flash at $0.075/1M input, $0.30/1M output (mid-2025 pricing). Total test set cost < $0.03.

### Latency

- ~2–4 seconds per API call (Flash model)
- 1.5s inter-call delay: 64 × (3 + 1.5) ≈ **~5 minutes** total
- Sample set (20 rows): ~**90 seconds**

### Rate Limits, Batching & Throttling

| Concern | Strategy |
|---|---|
| RPM (free tier: 15 RPM) | 1.5s inter-call delay (~40 RPM); auto-scales to 5s+ on 429 |
| Retries | Exponential backoff: 5s → 10s → 20s → 40s, max 4 attempts |
| Batching | All images per claim in one request — no per-image calls |
| Caching | No repeated calls for same row; prompt reuse across rows |
| TPM | ~208K input + ~19K output = ~227K tokens; well within 1M/min limit |

### Images Processed

- Sample: 28 images (20 claims)
- Test: 111 images (44 claims)
- **Total: 139 images, 64 claims**

---

## Key Design Decisions

1. **Vision-first** — all decisions grounded in image evidence; claim text provides context only.
2. **Prompt injection defense** — model instructed to detect and flag any embedded text instructions; claim status is never set by image text.
3. **User history = risk signal only** — raises `user_history_risk` / `manual_review_required` flags but cannot override visual evidence.
4. **Single-call-per-claim** — minimises cost and latency; images bundled in one request.
5. **Strict output sanitization** — model JSON validated against allowed value sets before writing.
6. **NLP fallback** — keyword extraction achieves 80% claim_status accuracy when vision API is unavailable.
