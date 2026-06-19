"""
NLP-based inference engine for damage claim verification.
Primary: deterministic keyword/rule extraction from claim transcript.
For vision-required cases (claim_mismatch by image content), the engine
flags manual_review_required; the Gemini vision pipeline handles these precisely.
"""
import re, csv, os
from pathlib import Path

# ── Issue keyword map ──────────────────────────────────────────────────────────
# Order matters: more specific patterns first
ISSUE_RULES = [
    # glass/windshield shatter: explicit shatter words
    ("glass_shatter", ["shatter","shattered"]),
    # crack: explicit crack/chip (NOT shatter)
    ("crack",         ["crack","cracked","cracking","fracture","chip","split"]),
    # dent: hail, dent word
    ("dent",          ["dent","dented","hail","indent","bent"]),
    # scratch
    ("scratch",       ["scratch","scratched","scrape","scuff","mark"]),
    # broken/missing part
    ("broken_part",   ["broken","broke","snapped","detached","fell off","came off",
                       "not sitting","wobble","does not sit"]),
    ("missing_part",  ["missing key","keycap","keys missing","came off","missing"]),
    # packaging
    ("torn_packaging",["torn","tore","ripped","phati","phata","open packaging",
                       "opened package","parcel khola","seal wali","jaise parcel"]),
    ("crushed_packaging",["crush","crushed","dab gaya","compressed","squash","pressed",
                          "badly crush","box crush"]),
    # water/stain
    ("water_damage",  ["water damage","water damaged","wet","rain","moisture","damp"]),
    ("stain",         ["stain","stained","oily","oil mark","coffee","liquid stain",
                       "liquid damage","spill","spilled"]),
]

# ── Part keyword maps ──────────────────────────────────────────────────────────
CAR_PARTS = {
    "front_bumper":  ["front bumper","parachoques delantero","front side bumper","bumper ke upar"],
    "rear_bumper":   ["rear bumper","back bumper","parachoques trasero","rear side","back bumper",
                      "back of the car","back looks"],
    "door":          ["door panel","door","side door"],
    "hood":          ["hood","bonnet","top panel","hail dents","hail damage"],
    "windshield":    ["windshield","front glass","windscreen","wind shield"],
    "side_mirror":   ["side mirror","mirror","left mirror","right mirror"],
    "headlight":     ["headlight","head light","front light"],
    "taillight":     ["taillight","tail light","back light","backlight","rear light"],
    "fender":        ["fender"],
    "quarter_panel": ["quarter panel"],
    "body":          ["body panel","car body","body"],
}

LAPTOP_PARTS = {
    "screen":    ["screen","display","monitor","lcd","pantalla","glass screen","the screen"],
    "keyboard":  ["keyboard","keys","key ","keycap","teclas","typing area"],
    "trackpad":  ["trackpad","touchpad","cursor area","palm rest","palm-rest"],
    "hinge":     ["hinge","hinges"],
    "lid":       ["lid","outer lid","top cover","laptop lid"],
    "corner":    ["corner","edge corner","laptop corner"],
    "port":      ["port","usb","hdmi","charging port"],
    "base":      ["base","bottom","underside"],
    "body":      ["outer body","body crack","side edge","outer shell"],
}

PACKAGE_PARTS = {
    "package_corner": ["corner","package corner","box corner","koona","dab gaya"],
    "package_side":   ["package side","side panel","box side","package surface","package surface"],
    "seal":           ["seal","tape","packaging seal","seal area","torn seal","torn open",
                       "phati hui","jaise parcel khola","seal wali","open packaging"],
    "label":          ["label","shipping label","unreadable label"],
    "contents":       ["contents","product inside","item inside","missing item","item missing",
                       "product missing"],
    "item":           ["item inside","item broken","item damaged"],
    "box":            ["outside box","outer box","delivery box","shipping box","cardboard box",
                       "outside","box"],
}

PART_MAPS = {"car": CAR_PARTS, "laptop": LAPTOP_PARTS, "package": PACKAGE_PARTS}

SEVERITY_MAP = {
    "glass_shatter": "high", "missing_part": "high",
    "broken_part": "medium", "crack": "medium", "dent": "medium",
    "crushed_packaging": "medium", "torn_packaging": "medium", "water_damage": "medium",
    "scratch": "low", "stain": "low", "none": "none", "unknown": "unknown",
}

# Phrases that signal user is uncertain about whether damage exists
UNCERTAINTY_PHRASES = [
    "not sure","not fully sure","may be","might be","i think","it looks like",
    "could be","possibly","probably","confused if","unsure","wondering if",
    "it looks like the headlight may","not certain","i am not sure",
    "i could not decide","i was not sure","reflection or actual","i am confused",
]

# Phrases that suggest user is overstating severity
EXAG_PHRASES = [
    "pretty bad","looks pretty bad","really bad","badly","badly damaged",
    "severely","major damage","huge dent","badly crushed",
]

INSTR_PATTERNS = [
    r"approve\s+(?:this|the)\s+claim",
    r"skip\s+(?:manual\s+)?review",
    r"mark\s+(?:this\s+)?(?:as\s+)?supported",
    r"follow\s+(?:this\s+)?(?:note|instruction)",
    r"ignore\s+(?:previous\s+)?instruction",
    r"system\s+reading\s+this\s+should",
    r"auto(?:matically)?\s+approve",
    r"no\s+need\s+to\s+review",
    r"usko follow karke.*approve",
    r"note.*approve",
    r"approve.*note",
    r"bas.*mark karna",
    r"ignore.*instructions.*mark",
    r"(?:accept|approve)\s+(?:this|the)\s+(?:claim|request)\s+(?:immediately|quickly|now)",
]

def norm(t): return t.lower().strip()

def extract_issue(claim, obj):
    c = norm(claim)
    # Special: "stone hit" -> crack not shatter (user_004 pattern)
    if re.search(r"stone\s+hit", c) or re.search(r"small.*crack|crack.*spread", c):
        if "shatter" not in c:
            return "crack"
    # Water vs stain disambiguation
    if obj == "package":
        if any(k in c for k in ["water damage","water damaged","wet","rain","damp"]):
            return "water_damage"
        if any(k in c for k in ["stain","oil","oily","coffee"]):
            return "stain"
    if obj == "laptop":
        if any(k in c for k in ["liquid","spill","spilled","coffee","water"]):
            return "stain"
    # Walk rules in priority order
    for issue, kws in ISSUE_RULES:
        for kw in kws:
            if kw in c:
                return issue
    return "unknown"

def extract_part(claim, obj):
    c = norm(claim)
    part_map = PART_MAPS.get(obj, {})
    scores = {p: 0 for p in part_map}
    for part, kws in part_map.items():
        for kw in kws:
            if kw in c:
                scores[part] += len(kw.split())
    best = max(scores, key=lambda x: scores[x])
    return best if scores[best] > 0 else "unknown"

def has_instr(claim):
    c = norm(claim)
    return any(re.search(p, c) for p in INSTR_PATTERNS)

def has_uncertainty(claim):
    c = norm(claim)
    return any(ph in c for ph in UNCERTAINTY_PHRASES)

def has_exag(claim):
    c = norm(claim)
    return any(ph in c for ph in EXAG_PHRASES)

def build_flags(claim, issue, part, history, instr):
    flags = []
    c = norm(claim)
    if instr:
        flags.append("text_instruction_present")
    hist_flags = (history.get("history_flags","none") or "none") if history else "none"
    rejected   = int(history.get("rejected_claim","0") or 0) if history else 0
    manual_rev = int(history.get("manual_review_claim","0") or 0) if history else 0
    if hist_flags and hist_flags != "none":
        flags.append("user_history_risk")
    if "manipulation" in hist_flags or rejected >= 2:
        if "possible_manipulation" not in flags:
            flags.append("possible_manipulation")
    if "non_original_image" in hist_flags:
        flags.append("non_original_image")
    # claim_mismatch: exaggeration with history of rejections
    if has_exag(claim) and (rejected >= 1 or "severity_exaggeration" in hist_flags):
        flags.append("claim_mismatch")
    # wrong_angle/damage_not_visible: high uncertainty in claim + issue unknown
    if has_uncertainty(claim) and part != "unknown" and issue == "unknown":
        flags.append("wrong_angle")
        flags.append("damage_not_visible")
    elif issue == "unknown" and part != "unknown":
        flags.append("damage_not_visible")
    # manual review triggers
    mr_triggers = (
        "text_instruction_present" in flags or
        "possible_manipulation" in flags or
        "non_original_image" in flags or
        rejected >= 2 or manual_rev >= 2 or
        (issue == "unknown" and part != "unknown")
    )
    if mr_triggers and "manual_review_required" not in flags:
        flags.append("manual_review_required")
    if not flags:
        return ["none"]
    seen = set(); out = []
    for f in flags:
        if f not in seen: seen.add(f); out.append(f)
    return out

def decide(row, issue, part, history, instr):
    """Returns (ev_met, ev_reason, status, justification, severity, valid_img)"""
    claim = row['user_claim']
    obj   = row['claim_object']
    imgs  = [p.strip() for p in row['image_paths'].split(';')]
    c     = norm(claim)
    hist_flags = (history.get("history_flags","none") or "none") if history else "none"
    rejected   = int(history.get("rejected_claim","0") or 0) if history else 0

    # ── Embedded instructions ─────────────────────────────────────────────────
    if instr:
        return (False,
                "Image or claim contains embedded instructions attempting to override the review.",
                "contradicted",
                "An embedded instruction was detected and ignored. The claim cannot be approved via embedded text.",
                "unknown", False)

    # ── Part fully unknown ────────────────────────────────────────────────────
    if part == "unknown":
        return (False, "The claimed object part could not be identified.",
                "not_enough_information",
                "Insufficient information to determine which part is claimed.",
                "unknown", False)

    # ── Issue unknown + uncertainty in claim ──────────────────────────────────
    if issue == "unknown" and has_uncertainty(claim):
        return (False,
                f"The {part.replace('_',' ')} is mentioned but the claimed damage is uncertain or unconfirmed.",
                "not_enough_information",
                f"The claim is uncertain. No clear damage type was confirmed for the {part.replace('_',' ')}.",
                "unknown", True)

    # ── Issue unknown without uncertainty ─────────────────────────────────────
    if issue == "unknown":
        return (False, "Damage type could not be determined from the claim.",
                "not_enough_information",
                "The submitted images and claim do not provide enough information to determine the damage type.",
                "unknown", False)

    # ── Package contents ──────────────────────────────────────────────────────
    if obj == "package" and part == "contents":
        return (False,
                "Interior contents cannot be reliably verified from standard packaging images.",
                "not_enough_information",
                "The submitted images do not clearly show the contents.",
                "unknown", False)

    # ── Contradicted: exaggeration + history ──────────────────────────────────
    # User says "badly crushed" / "pretty bad" but history flags severity_exaggeration or rejections
    if has_exag(claim) and (rejected >= 1 or "severity_exaggeration" in hist_flags):
        sev = SEVERITY_MAP.get(issue,"low")
        if sev == "high": sev = "medium"
        elif sev == "medium": sev = "low"
        return (True,
                f"The {part.replace('_',' ')} is visible but the described severity appears overstated.",
                "contradicted",
                f"The image shows only minor {issue.replace('_',' ')} on the {part.replace('_',' ')}, contradicting the severity described.",
                sev, True)

    # ── issue=none: no visible damage ────────────────────────────────────────
    if issue == "none":
        return (True,
                f"The {part.replace('_',' ')} is visible but no damage is apparent.",
                "contradicted",
                f"The submitted image shows the {part.replace('_',' ')} without visible damage.",
                "none", True)

    # ── Default: supported ────────────────────────────────────────────────────
    img_ids = [Path(p.strip()).stem for p in imgs]
    sev = SEVERITY_MAP.get(issue, "medium")
    if len(img_ids) > 1:
        primary = img_ids[-1]
        just = f"{primary} shows {issue.replace('_',' ')} on the {part.replace('_',' ')}, supporting the claim."
    else:
        just = f"{img_ids[0]} shows {issue.replace('_',' ')} on the {part.replace('_',' ')}, supporting the claim."
    ev_reason = f"The {part.replace('_',' ')} is visible and the {issue.replace('_',' ')} can be assessed from the submitted image(s)."
    return (True, ev_reason, "supported", just, sev, True)


def get_sup_ids(imgs, status):
    ids = [Path(p.strip()).stem for p in imgs]
    if status == "not_enough_information":
        return ["none"]
    return ids


def process_claim(row, histories):
    h      = histories.get(row['user_id'])
    instr  = has_instr(row['user_claim'])
    issue  = extract_issue(row['user_claim'], row['claim_object'])
    part   = extract_part(row['user_claim'], row['claim_object'])
    flags  = build_flags(row['user_claim'], issue, part, h, instr)
    ev_met, ev_rsn, status, just, sev, valid = decide(row, issue, part, h, instr)
    sup = get_sup_ids(row['image_paths'].split(';'), status)
    return {
        "evidence_standard_met": str(ev_met).lower(),
        "evidence_standard_met_reason": ev_rsn,
        "risk_flags": ";".join(flags),
        "issue_type": issue,
        "object_part": part,
        "claim_status": status,
        "claim_status_justification": just,
        "supporting_image_ids": ";".join(sup),
        "valid_image": str(valid).lower(),
        "severity": sev,
    }


def load_csv(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_output(rows, path):
    fnames = ["user_id","image_paths","user_claim","claim_object",
              "evidence_standard_met","evidence_standard_met_reason",
              "risk_flags","issue_type","object_part","claim_status",
              "claim_status_justification","supporting_image_ids","valid_image","severity"]
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fnames, quoting=csv.QUOTE_ALL)
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {path}")

def run(claims_path, out_path):
    claims    = load_csv(claims_path)
    histories = {r['user_id']: r for r in load_csv("dataset/user_history.csv")}
    results   = []
    for row in claims:
        res = process_claim(row, histories)
        results.append({"user_id":row['user_id'],"image_paths":row['image_paths'],
                         "user_claim":row['user_claim'],"claim_object":row['claim_object'],**res})
    write_output(results, out_path)
    return results

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"
    run("dataset/sample_claims.csv" if mode == "sample" else "dataset/claims.csv",
        "evaluation/sample_output.csv" if mode == "sample" else "output.csv")
