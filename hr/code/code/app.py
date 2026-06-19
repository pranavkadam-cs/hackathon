"""
FastAPI backend for the Damage Claim Verification Dashboard.
Serves the frontend and exposes API endpoints backed by real CSV data.
"""
import csv, os, subprocess, sys, json, uuid, shutil, logging
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from dotenv import load_dotenv
from pydantic import BaseModel

log = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Claim Verify API")

BASE     = Path(__file__).parent
DATASET  = BASE / "dataset"
EVAL_DIR = BASE / "evaluation"
IMG_DIR  = DATASET / "images" / "uploads"
IMG_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMG = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# ── CSV helpers ───────────────────────────────────────────────────────────────

def read_csv(path: Path):
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(path: Path, rows: list, fieldnames: list):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def append_csv_row(path: Path, row: dict, fieldnames: list):
    exists = path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, extrasaction="ignore")
        if not exists:
            w.writeheader()
        w.writerow(row)

CLAIMS_FIELDS = [
    "user_id","image_paths","user_claim","claim_object",
    "evidence_standard_met","evidence_standard_met_reason",
    "risk_flags","issue_type","object_part","claim_status",
    "claim_status_justification","supporting_image_ids","valid_image","severity"
]

HISTORY_FIELDS = [
    "user_id","past_claim_count","accept_claim","manual_review_claim",
    "rejected_claim","last_90_days_claim_count","history_flags","history_summary"
]

# ── merge helper ──────────────────────────────────────────────────────────────

def merge_claims():
    """Merge sample_claims.csv (ground truth) with sample_output.csv (predictions)."""
    gt_claims = read_csv(DATASET / "sample_claims.csv")
    up_claims = read_csv(DATASET / "uploaded_claims.csv")  # user-uploaded claims
    all_claims = gt_claims + up_claims

    preds_gt  = {r["user_id"]: r for r in read_csv(EVAL_DIR / "sample_output.csv")}
    preds_up  = {r["user_id"]: r for r in read_csv(EVAL_DIR / "uploaded_output.csv") if (EVAL_DIR / "uploaded_output.csv").exists()}
    preds     = {**preds_gt, **preds_up}

    history   = {r["user_id"]: r for r in read_csv(DATASET / "user_history.csv")}
    up_hist   = {r["user_id"]: r for r in read_csv(DATASET / "uploaded_history.csv") if (DATASET / "uploaded_history.csv").exists()}
    all_hist  = {**history, **up_hist}

    merged = []
    seen = set()
    for claim in all_claims:
        uid = claim.get("user_id","")
        if uid in seen:
            continue
        seen.add(uid)
        pred = preds.get(uid, {})
        hist = all_hist.get(uid, {})
        merged.append({
            "user_id":       uid,
            "claim_object":  claim.get("claim_object", ""),
            "user_claim":    claim.get("user_claim", ""),
            "image_paths":   claim.get("image_paths", ""),
            "claim_status":                pred.get("claim_status", "pending"),
            "issue_type":                  pred.get("issue_type", "unknown"),
            "object_part":                 pred.get("object_part", "unknown"),
            "severity":                    pred.get("severity", "unknown"),
            "evidence_standard_met":       pred.get("evidence_standard_met", "false"),
            "evidence_standard_met_reason":pred.get("evidence_standard_met_reason", ""),
            "risk_flags":                  pred.get("risk_flags", "none"),
            "claim_status_justification":  pred.get("claim_status_justification", ""),
            "valid_image":                 pred.get("valid_image", "false"),
            "supporting_image_ids":        pred.get("supporting_image_ids", "none"),
            "gt_claim_status":             claim.get("claim_status", ""),
            "past_claim_count":            hist.get("past_claim_count", "0"),
            "accept_claim":                hist.get("accept_claim", "0"),
            "rejected_claim":              hist.get("rejected_claim", "0"),
            "manual_review_claim":         hist.get("manual_review_claim", "0"),
            "history_flags":               hist.get("history_flags", "none"),
            "history_summary":             hist.get("history_summary", ""),
            "is_uploaded":                 claim in up_claims,
        })
    return merged

# ── GET /api/claims ───────────────────────────────────────────────────────────

@app.get("/api/claims")
def get_claims():
    return JSONResponse(merge_claims())

# ── GET /api/stats ────────────────────────────────────────────────────────────

@app.get("/api/stats")
def get_stats():
    claims = merge_claims()
    total        = len(claims)
    supported    = sum(1 for c in claims if c["claim_status"] == "supported")
    contradicted = sum(1 for c in claims if c["claim_status"] == "contradicted")
    nei          = sum(1 for c in claims if c["claim_status"] == "not_enough_information")
    flagged      = sum(1 for c in claims if c["risk_flags"] not in ("none",""))
    review_req   = sum(1 for c in claims if "manual_review_required" in c["risk_flags"])
    return JSONResponse({
        "total": total, "supported": supported, "contradicted": contradicted,
        "not_enough_information": nei, "flagged": flagged, "review_required": review_req,
    })

# ── POST /api/claims/new ──────────────────────────────────────────────────────

@app.post("/api/claims/new")
async def new_claim(
    user_id:      str        = Form(...),
    user_claim:   str        = Form(...),
    claim_object: str        = Form(...),
    history_summary: str     = Form(""),
    images: List[UploadFile] = File(default=[]),
):
    # Validate object type
    if claim_object not in ("car", "laptop", "package"):
        raise HTTPException(400, "claim_object must be car, laptop, or package")

    # Sanitise user_id
    uid = user_id.strip().replace(" ", "_")
    if not uid:
        raise HTTPException(400, "user_id is required")

    # Save images
    case_dir = IMG_DIR / uid
    case_dir.mkdir(parents=True, exist_ok=True)
    saved_paths = []
    for i, img in enumerate(images, 1):
        suffix = Path(img.filename).suffix.lower() if img.filename else ".jpg"
        if suffix not in ALLOWED_IMG:
            continue
        dest = case_dir / f"img_{i}{suffix}"
        content = await img.read()
        dest.write_bytes(content)
        # Store relative path (relative to dataset dir)
        rel = f"images/uploads/{uid}/img_{i}{suffix}"
        saved_paths.append(rel)

    img_paths_str = ";".join(saved_paths) if saved_paths else "none"

    # Append to uploaded_claims.csv
    up_claims_path = DATASET / "uploaded_claims.csv"
    claim_row = {
        "user_id": uid,
        "image_paths": img_paths_str,
        "user_claim": user_claim,
        "claim_object": claim_object,
    }
    existing = read_csv(up_claims_path)
    # Remove existing entry for same user_id if present
    existing = [r for r in existing if r["user_id"] != uid]
    existing.append(claim_row)
    write_csv(up_claims_path, existing, ["user_id","image_paths","user_claim","claim_object"])

    # Append/update history
    up_hist_path = DATASET / "uploaded_history.csv"
    hist_rows = read_csv(up_hist_path) if up_hist_path.exists() else []
    hist_rows = [r for r in hist_rows if r["user_id"] != uid]
    hist_rows.append({
        "user_id": uid,
        "past_claim_count": "0",
        "accept_claim": "0",
        "manual_review_claim": "0",
        "rejected_claim": "0",
        "last_90_days_claim_count": "0",
        "history_flags": "none",
        "history_summary": history_summary or "New client — no prior history.",
    })
    write_csv(up_hist_path, hist_rows, HISTORY_FIELDS)

    # Run NLP inference on this single claim
    result = subprocess.run(
        [sys.executable, "-c", f"""
import sys; sys.path.insert(0,r'{str(BASE)}')
from inference_engine import process_claim, load_csv
import csv, os
histories = {{r['user_id']: r for r in load_csv(r'{str(DATASET / 'user_history.csv')}')}}
try:
    uh = load_csv(r'{str(up_hist_path)}')
    histories.update({{r['user_id']: r for r in uh}})
except: pass
row = {{'user_id': '{uid}', 'image_paths': '{img_paths_str}', 'user_claim': '''{user_claim.replace("'", "\\'")}''', 'claim_object': '{claim_object}'}}
res = process_claim(row, histories)
import json; print(json.dumps(res))
"""],
        cwd=str(BASE), capture_output=True, text=True
    )

    prediction = {}
    try:
        prediction = json.loads(result.stdout.strip().split("\n")[-1])
    except Exception:
        pass

    # Save prediction to uploaded_output.csv
    up_out_path = EVAL_DIR / "uploaded_output.csv"
    out_rows = read_csv(up_out_path) if up_out_path.exists() else []
    out_rows = [r for r in out_rows if r["user_id"] != uid]
    out_row = {"user_id": uid, "image_paths": img_paths_str,
               "user_claim": user_claim, "claim_object": claim_object, **prediction}
    out_rows.append(out_row)
    write_csv(up_out_path, out_rows, CLAIMS_FIELDS)

    return JSONResponse({
        "ok": True,
        "user_id": uid,
        "prediction": prediction,
        "image_count": len(saved_paths),
    })

# ── POST /api/clients/upload-photo ───────────────────────────────────────────

@app.post("/api/clients/upload-photo")
async def upload_client_photo(
    user_id: str = Form(...),
    photo: UploadFile = File(...),
):
    suffix = Path(photo.filename).suffix.lower() if photo.filename else ".jpg"
    if suffix not in ALLOWED_IMG:
        raise HTTPException(400, "Invalid image type")
    photos_dir = BASE / "static" / "photos"
    photos_dir.mkdir(exist_ok=True)
    dest = photos_dir / f"{user_id.strip()}{suffix}"
    dest.write_bytes(await photo.read())
    return JSONResponse({"ok": True, "url": f"/static/photos/{dest.name}"})

# ── POST /api/chat ────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    claim_object: str = ""
    client_name: str = ""
    description: str = ""
    history: list = []

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """Gemini-powered conversational AI for claim intake."""
    try:
        from google import genai as genai_sdk
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        if not api_key:
            return JSONResponse({"reply": "I'm sorry, the AI service is currently unavailable. Please describe your damage in detail and proceed to upload your photos."})

        client_ai = genai_sdk.Client(api_key=api_key)

        system_prompt = f"""You are ClaimVerify AI, a helpful and professional insurance claim intake assistant.
You are helping a client named \"{req.client_name}\" file a damage claim for their \"{req.claim_object}\".
Their initial description: \"{req.description}\"

Your role:
1. Always respond confidently about any damage claim, whether it is for a car, laptop, or package. NEVER say you don't understand or cannot help.
2. Precisely and accurately answer ALL questions the user asks related to cars, laptops, packages, and the claims process. Provide technical and domain-specific expertise where appropriate to guide them.
3. Ask clarifying questions specific to the \"{req.claim_object}\" (e.g., bumper/door for cars, screen/hinge for laptops, torn seal/crushed box for packages).
4. Be empathetic and professional.
5. Help them understand what specific photos they should upload based on their damage.
6. Summarize what you've understood from the conversation.
7. Keep responses concise (2-4 sentences max) but highly informative.
8. Do NOT make claim decisions — you only gather information.
9. If the user has answered enough questions, encourage them to proceed to photo upload.

IMPORTANT: Answer all queries gracefully without fail, providing precise and direct answers to any user questions. Never approve or reject claims. You only gather information."""

        # Build conversation
        contents = [system_prompt]
        for msg in req.history:
            role = msg.get('role', 'user')
            text = msg.get('text', '')
            if text:
                contents.append(f"{'User' if role == 'user' else 'Assistant'}: {text}")
        contents.append(f"User: {req.message}")
        contents.append("Assistant:")

        full_prompt = "\n\n".join(contents)

        resp = client_ai.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt
        )
        reply = resp.text.strip()
        # Clean up any "Assistant:" prefix
        if reply.lower().startswith('assistant:'):
            reply = reply[len('assistant:'):].strip()

        return JSONResponse({"reply": reply})

    except Exception as e:
        log.warning(f"Chat API error: {e}")
        return JSONResponse({"reply": "I am here to help you with your claim. Could you tell me more about the damage — specifically which part was affected and how severe it looks? This will help us process your claim faster."})

# ── POST /api/run/nlp ─────────────────────────────────────────────────────────

@app.post("/api/run/nlp")
def run_nlp():
    result = subprocess.run(
        [sys.executable, "inference_engine.py", "sample"],
        cwd=str(BASE), capture_output=True, text=True
    )
    if result.returncode != 0:
        return JSONResponse({"ok": False, "error": result.stderr}, status_code=500)
    return JSONResponse({"ok": True, "message": result.stdout.strip()})

@app.post("/api/run/vision")
def run_vision():
    env = os.environ.copy()
    result = subprocess.run(
        [sys.executable, "pipeline.py", "sample"],
        cwd=str(BASE), capture_output=True, text=True, env=env
    )
    if result.returncode != 0:
        return JSONResponse({"ok": False, "error": result.stderr}, status_code=500)
    return JSONResponse({"ok": True, "message": result.stdout.strip()})

# ── Static files ──────────────────────────────────────────────────────────────

STATIC = BASE / "static"
STATIC.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")

@app.get("/")
def index():
    return FileResponse(str(STATIC / "index.html"))

@app.get("/client")
def client_portal():
    return FileResponse(str(STATIC / "client.html"))
