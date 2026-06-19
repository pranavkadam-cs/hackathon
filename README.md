 # Multi-Modal Evidence Review System

## Overview

The Multi-Modal Evidence Review System automatically evaluates insurance-style damage claims using:

* Images (primary evidence source)
* User claim conversations
* Historical user claim behavior
* Evidence requirement rules

The system determines whether submitted visual evidence supports, contradicts, or is insufficient to verify a damage claim.

Supported claim objects:

* Car
* Laptop
* Package

The solution combines computer vision, claim understanding, evidence validation, risk assessment, and structured decision generation.

---

## Problem Statement

Users submit damage claims along with one or more images and a conversation describing the issue.

The system must:

1. Extract the actual damage claim.
2. Analyze submitted images.
3. Identify visible damage.
4. Validate evidence requirements.
5. Assess claim consistency.
6. Consider user history risk signals.
7. Produce a structured claim decision.

Images are treated as the primary source of truth.

---

## Features

### Claim Understanding

* Extracts damage descriptions from conversations.
* Detects claimed issue type.
* Identifies affected object parts.

### Image Analysis

* Supports multiple images per claim.
* Detects:

  * Dent
  * Scratch
  * Crack
  * Glass shatter
  * Broken part
  * Missing part
  * Torn packaging
  * Crushed packaging
  * Water damage
  * Stains

### Evidence Validation

Checks:

* Minimum image requirements
* Visibility of object
* Visibility of damage
* Required viewing angles
* Image quality

### Risk Assessment

Flags:

* Blurry image
* Cropped image
* Wrong object
* Wrong object part
* Damage not visible
* Claim mismatch
* Possible manipulation
* User history risk
* Manual review required

### Severity Assessment

Classifies damage severity as:

* None
* Low
* Medium
* High
* Unknown

### Final Decision Engine

Outputs:

* Supported
* Contradicted
* Not Enough Information

---

## Project Structure

```text
project/
│
├── dataset/
│   ├── claims.csv
│   ├── sample_claims.csv
│   ├── user_history.csv
│   ├── evidence_requirements.csv
│   └── images/
│       ├── sample/
│       └── test/
│
├── src/
│   ├── claim_parser.py
│   ├── image_analyzer.py
│   ├── evidence_checker.py
│   ├── risk_assessor.py
│   ├── severity_estimator.py
│   ├── decision_engine.py
│   └── main.py
│
├── evaluation/
│   ├── evaluation_report.md
│   └── metrics.json
│
├── output.csv
├── requirements.txt
└── README.md
```

---

## Workflow

### Step 1 – Claim Parsing

Input:

* User conversation

Output:

* Claimed issue
* Claimed object part

---

### Step 2 – Image Inspection

Input:

* One or more claim images

Output:

* Visible issue type
* Object part
* Image quality indicators

---

### Step 3 – Evidence Verification

Matches visual findings against:

* Evidence requirement rules

Determines:

* Evidence standard met
* Evidence standard not met

---

### Step 4 – User History Analysis

Uses:

* Past claim count
* Rejection history
* Manual review history
* Historical risk flags

Generates:

* User history risk indicators

---

### Step 5 – Claim Decision

Combines:

* Claim text
* Visual evidence
* Evidence rules
* Risk signals

Produces final classification:

* Supported
* Contradicted
* Not Enough Information

---

## Output Schema

The generated `output.csv` contains:

| Column                       | Description          |
| ---------------------------- | -------------------- |
| user_id                      | User identifier      |
| image_paths                  | Submitted images     |
| user_claim                   | Claim conversation   |
| claim_object                 | Object category      |
| evidence_standard_met        | Evidence sufficiency |
| evidence_standard_met_reason | Explanation          |
| risk_flags                   | Risk indicators      |
| issue_type                   | Visible issue        |
| object_part                  | Affected component   |
| claim_status                 | Final decision       |
| claim_status_justification   | Reasoning            |
| supporting_image_ids         | Supporting images    |
| valid_image                  | Image usability      |
| severity                     | Damage severity      |

---

## Evaluation

The system is evaluated using:

`dataset/sample_claims.csv`

Metrics:

* Claim status accuracy
* Issue type accuracy
* Object part accuracy
* Evidence sufficiency accuracy
* Risk flag accuracy

Results are documented in:

```text
evaluation/evaluation_report.md
```

---

## Operational Analysis

The evaluation report includes:

* Model call estimates
* Token usage estimates
* Number of processed images
* Cost projections
* Runtime analysis
* TPM/RPM considerations
* Batching strategy
* Retry strategy
* Caching strategy

---

## Assumptions

1. Images are the primary source of truth.
2. User history only contributes risk context.
3. User history cannot override clear visual evidence.
4. Claims are limited to:

   * Car
   * Laptop
   * Package
5. Multiple images may be provided for a single claim.

---

## Running the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Run evaluation:

```bash
python src/evaluate.py
```

Generate predictions:

```bash
python src/main.py
```

Output:

```text
output.csv
```

---

## Future Improvements

* Advanced image authenticity detection
* Visual grounding verification
* Confidence scoring
* Human-in-the-loop review workflows
* Active learning feedback loops
* Fine-tuned multimodal models
* Automated fraud pattern detection

---

## Tech Stack

* Python
* Pandas
* OpenCV
* Pillow
* NumPy
* LLM-based Claim Parser
* Vision-Language Model (VLM)

---

## Author

Built as a Multi-Modal Damage Claim Verification System for automated evidence review and claim assessment.
