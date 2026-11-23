#!/usr/bin/env python3
"""Build compressed certificate images and samples.json for the demo site."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path("/workspace/coi-demo-site")
BENCH = Path("/workspace/acord25-benchmark")
SRC_PREVIEWS = BENCH / "previews"
OUT_IMAGES = ROOT / "images"
OUT_DATA = ROOT / "data"

SELECTED = ["coi_16", "coi_35", "coi_18"]

FLAG_LABELS = {
    "INVALID_NAIC": "Missing or invalid NAIC number",
    "MISSING_OR_INVALID_LIMITS": "Missing or invalid limit",
    "INVALID_OR_MISSING_DATES": "Missing or invalid dates",
    "ORPHAN_INSR_LTR": "Coverage letter does not match a listed insurer",
    "LOW_OCR_CONFIDENCE": "Low OCR confidence",
    "MISSING_CERT_DATE": "Missing certificate date",
    "MISSING_CERT_HOLDER": "Missing certificate holder",
    "MISSING_POLICY_NUMBER": "Missing policy number",
    "SUSPECT_INSURER_NAME": "Insurer name looks incomplete",
    "UNUSUAL_LIMIT_VALUE": "Unusual limit value",
}

COV_LABELS = {
    "general_liability": "General liability",
    "automobile_liability": "Automobile liability",
    "umbrella_excess": "Umbrella / excess",
    "workers_comp": "Workers' compensation",
}

COV_LIMIT_FIELDS = {
    "general_liability": [
        ("each_occurrence", "Each occurrence"),
        ("general_aggregate", "General aggregate"),
    ],
    "automobile_liability": [
        ("combined_single_limit", "Combined single limit"),
    ],
    "umbrella_excess": [
        ("each_occurrence", "Each occurrence"),
        ("aggregate", "Aggregate"),
    ],
    "workers_comp": [
        ("el_each_accident", "E.L. each accident"),
        ("el_disease_ea_employee", "E.L. disease / employee"),
        ("el_disease_policy_limit", "E.L. disease / policy"),
    ],
}

SAMPLE_META = {
    "coi_16": {
        "tab": "Digital · clean",
        "title": "Resideo Technologies",
        "kicker": "Born-digital PDF · straight-through",
        "review_summary": "No validation flags. On a paid plan this unflagged digital certificate could be released without waiting in the review queue. On the free pilot, and on the Scale plan, a person on our team still checks every file.",
    },
    "coi_35": {
        "tab": "Digital · flagged",
        "title": "Waverly at South Beach",
        "kicker": "Born-digital PDF · flagged for review",
        "review_summary": "Every extracted field matches the certificate, including a blank auto combined single limit. The validator still flagged the missing limit, so a person on our team would review it before delivery. This is a problem on the form, not a misread.",
    },
    "coi_18": {
        "tab": "Scan · flagged",
        "title": "Amazing Air",
        "kicker": "Scanned PDF · flagged for review",
        "review_summary": "This scan is 90% accurate (27 of 30 scored fields). The three misses — a general-liability expiration date and two insurer letters — were all flagged. In the official test, every scanned certificate was sent to a person. Nothing here would be released straight through.",
    },
}


def money(v):
    if v is None or v == "":
        return None
    if isinstance(v, str):
        return v
    return f"${int(v):,}"


def load_sources():
    out = {}
    with open(BENCH / "sources.csv", newline="") as f:
        for row in csv.DictReader(f):
            out[row["doc_id"]] = row
    return out


def details_for(field_id: str, details: list[str]) -> list[str]:
    hits = []
    for d in details:
        if field_id == "certificate_date" and "MISSING_CERT_DATE" in d:
            hits.append(d)
        elif field_id == "certificate_holder" and "MISSING_CERT_HOLDER" in d:
            hits.append(d)
        elif field_id.startswith("insurer_") and "INVALID_NAIC" in d:
            letter = field_id.split("_")[1]
            if f"Insurer {letter} " in d or f"Insurer {letter}(" in d:
                hits.append(d)
        elif "." in field_id:
            cov, leaf = field_id.split(".", 1)
            if cov in d:
                if leaf in ("eff_date", "exp_date") and "DATES" in d:
                    if leaf == "exp_date" and ("exp=None" in d or "exp=null" in d):
                        hits.append(d)
                    elif leaf == "eff_date" and ("eff=None" in d or "eff=null" in d):
                        hits.append(d)
                    elif "eff=" not in d and "exp=" not in d:
                        hits.append(d)
                elif leaf == "insr_ltr" and "ORPHAN_INSR_LTR" in d:
                    hits.append(d)
                elif leaf == "policy_number" and "POLICY_NUMBER" in d:
                    hits.append(d)
                elif leaf in (
                    "each_occurrence",
                    "general_aggregate",
                    "combined_single_limit",
                    "aggregate",
                    "el_each_accident",
                    "el_disease_ea_employee",
                    "el_disease_policy_limit",
                ) and ("LIMITS" in d or "UNUSUAL_LIMIT" in d):
                    hits.append(d)
    return hits


def error_for(field_id: str, errors: list[dict]):
    for e in errors:
        if e.get("field") == field_id:
            return e
    return None


def field_row(field_id, section, label, value, fmt, errors, details, doc_conf, is_money=False, display=None):
    err = error_for(field_id, errors)
    attached = details_for(field_id, details)
    display_value = display if display is not None else (money(value) if is_money else value)
    if display_value is None or display_value == "":
        display_value = None

    status = "ok"
    gt_display = None
    flag_label = None
    note = None
    confidence = int(round(doc_conf))

    if err:
        gt = err.get("gt")
        if is_money:
            gt_display = money(gt)
        else:
            gt_display = gt
        if display_value is None and gt not in (None, ""):
            status = "missed"
            note = "Not extracted"
            display_value = "—"
        else:
            status = "mismatch"
            note = "Does not match the certificate"
            if display_value is None:
                display_value = "—"
        confidence = min(confidence, 55)
        if attached:
            code = re.search(r"\[([A-Z_]+)\]", attached[0])
            if code:
                flag_label = FLAG_LABELS.get(code.group(1), code.group(1).replace("_", " ").title())
        elif err.get("critical"):
            flag_label = "Flagged (critical field)"
        else:
            flag_label = "Flagged"
    elif attached:
        status = "flagged"
        code = re.search(r"\[([A-Z_]+)\]", attached[0])
        flag_label = FLAG_LABELS.get(code.group(1), "Flagged for review") if code else "Flagged for review"
        note = re.sub(r"^\[[A-Z_]+\]\s*", "", attached[0])
        confidence = min(confidence, 70)
        if display_value is None:
            display_value = "—"
    else:
        if display_value is None:
            display_value = "—"
        if fmt == "scanned":
            confidence = min(confidence, 95)

    return {
        "id": field_id,
        "section": section,
        "label": label,
        "value": display_value,
        "status": status,
        "confidence": confidence,
        "flag": flag_label,
        "note": note,
        "ground_truth": gt_display,
        "critical": bool(err.get("critical")) if err else False,
    }


def build_sample(doc_id, pred_wrap, score, source):
    pred = pred_wrap["prediction"]
    val = pred_wrap["validation"]
    meta = pred.get("_meta") or {}
    details = val.get("review_details") or []
    errors = score.get("errors") or []
    fmt = pred.get("format") or score.get("format")
    doc_conf = meta.get("ocr_mean_conf")
    if doc_conf is None:
        doc_conf = 100.0 if fmt == "digital" else 80.0

    fields = []
    fields.append(field_row("certificate_date", "Parties", "Certificate date", pred.get("certificate_date"), fmt, errors, details, doc_conf))
    fields.append(field_row("producer", "Parties", "Producer", pred.get("producer"), fmt, errors, details, doc_conf))
    fields.append(field_row("insured", "Parties", "Insured", pred.get("insured"), fmt, errors, details, doc_conf))
    fields.append(field_row("certificate_holder", "Parties", "Certificate holder", pred.get("certificate_holder"), fmt, errors, details, doc_conf))

    insurers = pred.get("insurers") or {}
    for letter in ["A", "B", "C", "D", "E", "F"]:
        slot = insurers.get(letter)
        if not slot:
            continue
        fields.append(field_row(
            f"insurer_{letter}_name",
            "Insurers",
            f"Insurer {letter}",
            slot.get("name"),
            fmt, errors, details, doc_conf,
        ))
        fields.append(field_row(
            f"insurer_{letter}_naic",
            "Insurers",
            f"Insurer {letter} NAIC",
            slot.get("naic"),
            fmt, errors, details, doc_conf,
        ))

    coverages = pred.get("coverages") or {}
    for cov_key, cov_label in COV_LABELS.items():
        cov = coverages.get(cov_key) or {}
        present = bool(cov.get("present"))
        section = cov_label
        fields.append(field_row(
            f"{cov_key}.present",
            section,
            "Present on certificate",
            present,
            fmt, errors, details, doc_conf,
            display="Yes" if present else "No",
        ))
        if not present:
            continue
        fields.append(field_row(f"{cov_key}.insr_ltr", section, "Insurer letter", cov.get("insr_ltr"), fmt, errors, details, doc_conf))
        fields.append(field_row(f"{cov_key}.policy_number", section, "Policy number", cov.get("policy_number"), fmt, errors, details, doc_conf))
        fields.append(field_row(f"{cov_key}.eff_date", section, "Effective", cov.get("eff_date"), fmt, errors, details, doc_conf))
        fields.append(field_row(f"{cov_key}.exp_date", section, "Expiration", cov.get("exp_date"), fmt, errors, details, doc_conf))
        for leaf, lab in COV_LIMIT_FIELDS[cov_key]:
            fields.append(field_row(f"{cov_key}.{leaf}", section, lab, cov.get(leaf), fmt, errors, details, doc_conf, is_money=True))

    flags = val.get("review_flags") or []
    ok = sum(1 for f in fields if f["status"] == "ok")
    flagged_n = sum(1 for f in fields if f["status"] in ("flagged", "missed", "mismatch"))

    return {
        "id": doc_id,
        "tab": SAMPLE_META[doc_id]["tab"],
        "title": SAMPLE_META[doc_id]["title"],
        "kicker": SAMPLE_META[doc_id]["kicker"],
        "review_summary": SAMPLE_META[doc_id]["review_summary"],
        "format": fmt,
        "image": f"images/{doc_id}.jpg",
        "source_url": source.get("source_url"),
        "source_label": "Publicly posted ACORD 25",
        "certificate_date": pred.get("certificate_date"),
        "producer": pred.get("producer"),
        "insured": pred.get("insured"),
        "certificate_holder": pred.get("certificate_holder"),
        "desc_additional_insured": bool(pred.get("desc_additional_insured")),
        "desc_waiver_of_subrogation": bool(pred.get("desc_waiver_of_subrogation")),
        "ocr_mean_conf": round(float(doc_conf), 1),
        "field_accuracy": score.get("field_accuracy"),
        "correct_fields": score.get("correct_fields"),
        "total_fields": score.get("total_fields"),
        "straight_through": bool(score.get("straight_through")),
        "needs_human_review": bool(score.get("needs_human_review")),
        "review_flags": [{"code": c, "label": FLAG_LABELS.get(c, c.replace("_", " ").title())} for c in flags],
        "field_counts": {"ok": ok, "flagged": flagged_n, "total": len(fields)},
        "fields": fields,
    }


def compress_image(doc_id: str) -> None:
    src = SRC_PREVIEWS / f"{doc_id}.png"
    dest = OUT_IMAGES / f"{doc_id}.jpg"
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    if im.mode != "RGB":
        im = im.convert("RGB")
    w, h = im.size
    max_w = 1400
    if w > max_w:
        h = int(h * (max_w / w))
        w = max_w
        im = im.resize((w, h), Image.Resampling.LANCZOS)
    im.save(dest, "JPEG", quality=82, optimize=True, progressive=True)
    print(f"  {dest.name} {w}x{h} {dest.stat().st_size/1024:.0f} KB")


def main():
    OUT_IMAGES.mkdir(parents=True, exist_ok=True)
    OUT_DATA.mkdir(parents=True, exist_ok=True)

    preds = {d["doc_id"]: d for d in json.loads((BENCH / "results/predictions.json").read_text())}
    scores = {d["doc_id"]: d for d in json.loads((BENCH / "results/doc_scores.json").read_text())}
    sources = load_sources()

    print("Compressing images…")
    samples = []
    for doc_id in SELECTED:
        compress_image(doc_id)
        samples.append(build_sample(doc_id, preds[doc_id], scores[doc_id], sources[doc_id]))

    payload = {
        "generated": "2026-11-22",
        "disclaimer": "Official ACORD 25 test (corrections OFF) on 22 fresh public certificates, run November 22, 2026, 5:37 PM PT, with free local tools. Memory was not trained on this set. Not a production guarantee.",
        "benchmarks": {
            "official": {
                "name": "Official test (corrections OFF)",
                "date": "2026-11-22",
                "time_pt": "5:37 PM PT",
                "commit": "d9034ee",
                "n": 22,
                "digital_n": 12,
                "scan_n": 10,
                "fields": 774,
                "correct": 609,
                "accuracy": 0.787,
                "accuracy_label": "78.7% (609 / 774)",
                "ci_overall": "69.3–87.6%",
                "digital_accuracy": 0.954,
                "digital_accuracy_label": "95.4% (374 / 392)",
                "digital_fields": 392,
                "digital_correct": 374,
                "ci_digital": "89.6–99.7%",
                "scan_accuracy": 0.615,
                "scan_accuracy_label": "61.5% (235 / 382)",
                "scan_fields": 382,
                "scan_correct": 235,
                "ci_scans": "51.0–71.0%",
                "straight_through": 0.273,
                "straight_through_label": "27.3% (6 / 22)",
                "digital_stp": "50.0% (6 / 12)",
                "scan_stp": "0% (0 / 10)",
                "flag_rate": 0.682,
                "flag_label": "68.2% (15 / 22)",
                "scan_flag_label": "100% of scans flagged for a person",
                "escape": 0.045,
                "escape_label": "1 of 22",
                "official_note": "Official score is corrections OFF. Memory was not trained on this set.",
            },
        },
        "samples": samples,
    }
    out = OUT_DATA / "samples.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
