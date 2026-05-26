import streamlit as st
import cv2
import numpy as np
from PIL import Image
from collections import Counter
import time
import io
import os

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Construction Safety Monitor",
    page_icon="🦺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --bg:      #0a0c10;
    --surface: #111318;
    --border:  #1e2229;
    --accent:  #f0c040;
    --green:   #22c55e;
    --red:     #ef4444;
    --orange:  #f97316;
    --blue:    #60a5fa;
    --purple:  #a78bfa;
    --text:    #e8eaf0;
    --muted:   #6b7280;
}
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1400px; }

.header-banner {
    background: linear-gradient(135deg, #111318 0%, #1a1d24 50%, #111318 100%);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 8px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.header-banner::before {
    content: '';
    position: absolute;
    top: -50%; right: -10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(240,192,64,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.header-title { font-size:2rem; font-weight:800; color:var(--accent); letter-spacing:-0.02em; margin:0 0 0.3rem; line-height:1.1; }
.header-sub   { font-size:0.85rem; color:var(--muted); font-family:'IBM Plex Mono',monospace; margin:0; letter-spacing:0.05em; }

.metric-grid   { display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin:1.5rem 0; }
.metric-grid-5 { display:grid; grid-template-columns:repeat(5,1fr); gap:1rem; margin:1.5rem 0; }
.metric-card { background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:1.2rem 1.4rem; position:relative; overflow:hidden; }
.metric-card::after { content:''; position:absolute; top:0; left:0; width:100%; height:3px; }
.metric-card.yellow::after { background:var(--accent); }
.metric-card.green::after  { background:var(--green); }
.metric-card.red::after    { background:var(--red); }
.metric-card.orange::after { background:var(--orange); }
.metric-card.blue::after   { background:var(--blue); }
.metric-label { font-size:0.72rem; color:var(--muted); font-family:'IBM Plex Mono',monospace; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.5rem; }
.metric-value { font-size:2rem; font-weight:800; line-height:1; color:var(--text); }
.metric-card.yellow .metric-value { color:var(--accent); }
.metric-card.green  .metric-value { color:var(--green); }
.metric-card.red    .metric-value { color:var(--red); }
.metric-card.orange .metric-value { color:var(--orange); }
.metric-card.blue   .metric-value { color:var(--blue); }
.metric-sub { font-size:0.75rem; color:var(--muted); margin-top:0.3rem; font-family:'IBM Plex Mono',monospace; }

.status-badge { display:inline-flex; align-items:center; gap:0.6rem; padding:0.8rem 1.4rem; border-radius:6px; font-weight:700; font-size:1.1rem; letter-spacing:0.03em; margin:0.5rem 0; width:100%; box-sizing:border-box; }
.status-aman    { background:rgba(34,197,94,0.12);  border:1px solid rgba(34,197,94,0.3);  color:var(--green); }
.status-waspada { background:rgba(249,115,22,0.12); border:1px solid rgba(249,115,22,0.3); color:var(--orange); }
.status-bahaya  { background:rgba(239,68,68,0.12);  border:1px solid rgba(239,68,68,0.3);  color:var(--red); }

.score-ring-wrap { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:1.2rem 0; }
.score-ring { position:relative; width:120px; height:120px; }
.score-ring svg { transform:rotate(-90deg); }
.score-center { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center; }
.score-num   { font-size:1.8rem; font-weight:800; line-height:1; }
.score-denom { font-size:0.72rem; color:var(--muted); font-family:'IBM Plex Mono',monospace; }
.grade-badge { margin-top:0.6rem; font-size:1.6rem; font-weight:800; letter-spacing:0.05em; }
.risk-label  { font-size:0.72rem; font-family:'IBM Plex Mono',monospace; color:var(--muted); text-transform:uppercase; letter-spacing:0.08em; margin-top:0.2rem; }

.worker-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(190px,1fr)); gap:0.8rem; margin:0.8rem 0; }
.worker-card { background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:1rem; position:relative; }
.worker-card.compliant  { border-color:rgba(34,197,94,0.4); }
.worker-card.violation  { border-color:rgba(249,115,22,0.4); }
.worker-card.critical   { border-color:rgba(239,68,68,0.4); }
.worker-card.unassigned { border-color:rgba(240,192,64,0.3); }
.worker-id     { font-size:0.7rem; color:var(--muted); font-family:'IBM Plex Mono',monospace; letter-spacing:0.1em; margin-bottom:0.5rem; }
.worker-status { font-size:0.85rem; font-weight:700; margin-bottom:0.6rem; }
.worker-apd-row { display:flex; justify-content:space-between; font-size:0.75rem; margin:0.2rem 0; font-family:'IBM Plex Mono',monospace; }
.worker-footer  { font-size:0.68rem; font-family:'IBM Plex Mono',monospace; color:var(--muted); margin-top:0.5rem; padding-top:0.5rem; border-top:1px solid var(--border); }

.apd-row { margin:0.7rem 0; }
.apd-header { display:flex; justify-content:space-between; margin-bottom:0.35rem; font-size:0.82rem; }
.apd-label { color:var(--text); font-weight:600; }
.apd-pct   { color:var(--muted); font-family:'IBM Plex Mono',monospace; }
.progress-track { height:6px; background:var(--border); border-radius:99px; overflow:hidden; }
.progress-fill  { height:100%; border-radius:99px; }

.det-table { width:100%; border-collapse:collapse; font-size:0.82rem; font-family:'IBM Plex Mono',monospace; }
.det-table th { text-align:left; padding:0.5rem 0.7rem; border-bottom:1px solid var(--border); color:var(--muted); font-weight:500; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.06em; }
.det-table td { padding:0.45rem 0.7rem; border-bottom:1px solid rgba(30,34,41,0.6); color:var(--text); }
.det-table tr:last-child td { border-bottom:none; }

.badge { display:inline-block; padding:0.15rem 0.55rem; border-radius:4px; font-size:0.72rem; font-weight:600; }
.badge-green  { background:rgba(34,197,94,0.15);  color:var(--green); }
.badge-red    { background:rgba(239,68,68,0.15);   color:var(--red); }
.badge-yellow { background:rgba(240,192,64,0.15);  color:var(--accent); }
.badge-blue   { background:rgba(96,165,250,0.15);  color:var(--blue); }
.badge-orange { background:rgba(249,115,22,0.15);  color:var(--orange); }

.section-label { font-size:0.7rem; font-family:'IBM Plex Mono',monospace; color:var(--muted); letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.8rem; padding-bottom:0.5rem; border-bottom:1px solid var(--border); }
.panel { background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:1.4rem; }
.info-box { background:rgba(240,192,64,0.06); border:1px solid rgba(240,192,64,0.2); border-radius:6px; padding:0.9rem 1.1rem; font-size:0.82rem; color:var(--text); line-height:1.6; margin:0.8rem 0; }
.info-box b { color:var(--accent); }
.divider { border:none; border-top:1px solid var(--border); margin:1.5rem 0; }

[data-testid="stFileUploader"] { background:var(--surface) !important; border:1px dashed var(--border) !important; border-radius:8px !important; }
[data-testid="stSidebar"] { background-color:var(--surface) !important; border-right:1px solid var(--border) !important; }
[data-testid="stImage"] img { border-radius:6px; border:1px solid var(--border); }
.stButton > button { background:var(--accent) !important; color:#0a0c10 !important; font-family:'Syne',sans-serif !important; font-weight:700 !important; border:none !important; border-radius:6px !important; padding:0.6rem 1.2rem !important; }
.stButton > button:hover { opacity:0.85 !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# IoU-based Per-Worker APD Assignment
# ══════════════════════════════════════════════════════════════

def compute_iou(box_a: list, box_b: list) -> float:
    """Hitung IoU antara dua bbox [x1,y1,x2,y2]."""
    xa = max(box_a[0], box_b[0])
    ya = max(box_a[1], box_b[1])
    xb = min(box_a[2], box_b[2])
    yb = min(box_a[3], box_b[3])
    inter = max(0, xb - xa) * max(0, yb - ya)
    if inter == 0:
        return 0.0
    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    union  = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def get_head_zone(person_box: list, ratio: float = 0.35) -> list:
    """Top `ratio` dari bbox person = zona kepala untuk matching helmet."""
    x1, y1, x2, y2 = person_box
    return [x1, y1, x2, y1 + (y2 - y1) * ratio]


def assign_apd_to_workers(results, class_names, iou_thresh: float = 0.05) -> list:
    """
    Assign helmet & vest ke masing-masing person berdasarkan IoU overlap.

    Untuk setiap person:
      - Head zone (top 35%) → match dengan helmet / no-helmet
      - Body zone (full bbox) → match dengan vest / no-vest
      - Yang menang = IoU tertinggi di atas threshold
    """
    if isinstance(class_names, dict):
        class_names = [class_names[i] for i in range(len(class_names))]

    persons = []
    helmets = []
    no_helmets = []
    vests = []
    no_vests = []

    for box in results[0].boxes:
        cls_id   = int(box.cls.item())
        cls_name = class_names[cls_id]
        conf     = float(box.conf.item())
        xyxy     = box.xyxy[0].tolist()
        entry    = xyxy + [conf]

        if   cls_name == "person":    persons.append(entry)
        elif cls_name == "helmet":    helmets.append(entry)
        elif cls_name == "no-helmet": no_helmets.append(entry)
        elif cls_name == "vest":      vests.append(entry)
        elif cls_name == "no-vest":   no_vests.append(entry)

    workers = []

    for idx, p in enumerate(persons):
        p_box     = p[:4]
        p_conf    = p[4]
        head_zone = get_head_zone(p_box)
        body_zone = p_box

        # ── Helmet matching ───────────────────────────────────
        best_h  = max((compute_iou(head_zone, h[:4]) for h in helmets),    default=0.0)
        best_nh = max((compute_iou(head_zone, h[:4]) for h in no_helmets), default=0.0)

        if best_h >= iou_thresh and best_h >= best_nh:
            helmet_status = "yes"
        elif best_nh >= iou_thresh:
            helmet_status = "no"
        else:
            helmet_status = "undetected"

        # ── Vest matching ─────────────────────────────────────
        best_v  = max((compute_iou(body_zone, v[:4]) for v in vests),    default=0.0)
        best_nv = max((compute_iou(body_zone, v[:4]) for v in no_vests), default=0.0)

        if best_v >= iou_thresh and best_v >= best_nv:
            vest_status = "yes"
        elif best_nv >= iou_thresh:
            vest_status = "no"
        else:
            vest_status = "undetected"

        has_helmet  = helmet_status == "yes"
        has_vest    = vest_status   == "yes"
        miss_helmet = helmet_status == "no"
        miss_vest   = vest_status   == "no"

        if miss_helmet and miss_vest:
            compliance = "critical"
        elif miss_helmet or miss_vest:
            compliance = "violation"
        elif helmet_status == "undetected" or vest_status == "undetected":
            compliance = "unassigned"
        else:
            compliance = "compliant"

        workers.append({
            "id":            idx + 1,
            "bbox":          p_box,
            "conf":          p_conf,
            "helmet_status": helmet_status,
            "vest_status":   vest_status,
            "has_helmet":    has_helmet,
            "has_vest":      has_vest,
            "miss_helmet":   miss_helmet,
            "miss_vest":     miss_vest,
            "compliance":    compliance,
            "helmet_iou":    round(best_h,  3),
            "no_helmet_iou": round(best_nh, 3),
            "vest_iou":      round(best_v,  3),
            "no_vest_iou":   round(best_nv, 3),
        })

    return workers


# ══════════════════════════════════════════════════════════════
# Weighted Severity Scoring
# ══════════════════════════════════════════════════════════════

PENALTY = {
    "missing_helmet": 25,
    "missing_vest":   15,
    "missing_both":   10,   # extra penalty jika keduanya tidak ada
    "systemic_mult":  0.8,  # multiplier jika >50% violation
}

GRADE_TABLE = [
    (90, "A", "#22c55e", "EXCELLENT",  "Kondisi keselamatan sangat baik"),
    (75, "B", "#86efac", "GOOD",       "Kondisi baik, pantau terus"),
    (60, "C", "#f97316", "MODERATE",   "Ada pelanggaran, tindak segera"),
    (40, "D", "#ef4444", "HIGH RISK",  "Risiko tinggi, hentikan pekerjaan berbahaya"),
    (0,  "F", "#dc2626", "CRITICAL",   "Kondisi kritis, evakuasi & safety briefing"),
]


def compute_severity_score(workers: list) -> dict:
    """
    Hitung severity score 0-100 dari list workers.

    Algoritma:
      score = 100
      Untuk tiap worker yang violation → kurangi penalty
      Jika violation rate > 50% → kalikan 0.8 (systemic)
    """
    if not workers:
        return {
            "score": None, "raw_score": None,
            "grade": "N/A", "color": "#6b7280",
            "risk_label": "NO DATA",
            "recommendation": "Tidak ada pekerja terdeteksi",
            "raw_penalty": 0, "violation_count": 0,
            "violation_rate": 0, "breakdown": [], "systemic": False,
        }

    total_workers   = len(workers)
    total_penalty   = 0
    violation_count = 0
    breakdown       = []

    for w in workers:
        penalty = 0
        desc    = []

        if w["miss_helmet"] and w["miss_vest"]:
            p = PENALTY["missing_helmet"] + PENALTY["missing_vest"] + PENALTY["missing_both"]
            penalty += p
            desc.append(f"−{p}pt (no helmet + no vest + extra)")
            violation_count += 1
        elif w["miss_helmet"]:
            penalty += PENALTY["missing_helmet"]
            desc.append(f"−{PENALTY['missing_helmet']}pt (no helmet)")
            violation_count += 1
        elif w["miss_vest"]:
            penalty += PENALTY["missing_vest"]
            desc.append(f"−{PENALTY['missing_vest']}pt (no vest)")
            violation_count += 1

        total_penalty += penalty
        breakdown.append({
            "worker_id":  w["id"],
            "compliance": w["compliance"],
            "penalty":    penalty,
            "desc":       desc[0] if desc else "—",
        })

    raw_score      = max(0, 100 - total_penalty)
    violation_rate = violation_count / total_workers
    systemic       = violation_rate > 0.5
    final_score    = round(max(0, min(100, raw_score * (PENALTY["systemic_mult"] if systemic else 1))), 1)

    grade, color, risk_label, recommendation = "F", "#dc2626", "CRITICAL", "Kondisi kritis"
    for threshold, g, c, r, rec in GRADE_TABLE:
        if final_score >= threshold:
            grade, color, risk_label, recommendation = g, c, r, rec
            break

    return {
        "score":           final_score,
        "raw_score":       raw_score,
        "grade":           grade,
        "color":           color,
        "risk_label":      risk_label,
        "recommendation":  recommendation,
        "raw_penalty":     total_penalty,
        "violation_count": violation_count,
        "violation_rate":  round(violation_rate * 100, 1),
        "breakdown":       breakdown,
        "systemic":        systemic,
    }


# ══════════════════════════════════════════════════════════════
# ANNOTATION — Worker Bounding Box Overlay
# ══════════════════════════════════════════════════════════════

COMPLIANCE_COLORS_CV = {
    "compliant":  (34,  197, 94),
    "violation":  (249, 115, 22),
    "critical":   (239, 68,  68),
    "unassigned": (240, 192, 64),
}

STATUS_TEXT = {
    "compliant":  "SAFE",
    "violation":  "VIOLATION",
    "critical":   "CRITICAL",
    "unassigned": "UNVERIFIED",
}


def draw_worker_annotations(img_rgb: np.ndarray, workers: list) -> np.ndarray:
    """
    Overlay per-worker bounding box dengan warna compliance dan label ID+status.
    """
    img = img_rgb.copy()
    for w in workers:
        x1, y1, x2, y2 = [int(v) for v in w["bbox"]]
        color           = COMPLIANCE_COLORS_CV.get(w["compliance"], (107, 114, 128))

        # Main bounding box (tebal)
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

        # Top label: Worker ID
        lbl = f"W{w['id']}"
        cv2.rectangle(img, (x1, y1 - 22), (x1 + 52, y1), color, -1)
        cv2.putText(img, lbl, (x1 + 4, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (10, 12, 16), 2)

        # Bottom bar: compliance status
        status = STATUS_TEXT.get(w["compliance"], "?")
        cv2.rectangle(img, (x1, y2), (x2, y2 + 18), color, -1)
        cv2.putText(img, status, (x1 + 4, y2 + 13),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (10, 12, 16), 1)

    return img


# ══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def load_model(model_path: str):
    from ultralytics import YOLO
    return YOLO(model_path)


def analyze_safety(results, class_names: list) -> dict:
    """Flat analysis — summary count & basic compliance stats."""
    counts     = Counter()
    detections = []

    for box in results[0].boxes:
        cls_id   = int(box.cls.item())
        cls_name = class_names[cls_id]
        conf     = float(box.conf.item())
        counts[cls_name] += 1
        detections.append({"class": cls_name, "conf": conf})

    for cls in ["person", "helmet", "no-helmet", "vest", "no-vest"]:
        counts.setdefault(cls, 0)

    wh = counts["helmet"];   mh = counts["no-helmet"]
    wv = counts["vest"];     mv = counts["no-vest"]
    hp = (wh / (wh + mh) * 100) if (wh + mh) > 0 else 100.0
    vp = (wv / (wv + mv) * 100) if (wv + mv) > 0 else 100.0
    violations = mh + mv

    if violations == 0:
        risk, emoji, detail = "AMAN",    "✅", "Semua pekerja memakai APD lengkap"
    elif violations <= 2:
        risk, emoji, detail = "WASPADA", "⚠️", f"{violations} pelanggaran APD terdeteksi"
    else:
        risk, emoji, detail = "BAHAYA",  "🚨", f"{violations} pelanggaran APD — segera tindak lanjut!"

    return {
        "counts": dict(counts), "detections": sorted(detections, key=lambda x: -x["conf"]),
        "total_persons": counts["person"],
        "wearing_helmet": wh, "missing_helmet": mh,
        "wearing_vest": wv,   "missing_vest": mv,
        "helmet_pct": round(hp, 1), "vest_pct": round(vp, 1),
        "violations": violations, "risk": risk, "emoji": emoji, "detail": detail,
    }


def color_for_pct(pct: float) -> str:
    return "#22c55e" if pct >= 80 else "#f97316" if pct >= 50 else "#ef4444"


def render_severity_ring(score, grade, color, risk_label) -> str:
    if score is None:
        return '<div style="text-align:center;color:#6b7280;padding:2rem">N/A</div>'
    r = 48
    c = 2 * 3.14159 * r
    filled = c * (score / 100)
    empty  = c - filled
    return f"""
    <div class="score-ring-wrap">
        <div class="score-ring">
            <svg width="120" height="120" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="{r}" fill="none" stroke="#1e2229" stroke-width="10"/>
                <circle cx="60" cy="60" r="{r}" fill="none" stroke="{color}" stroke-width="10"
                    stroke-dasharray="{filled:.1f} {empty:.1f}" stroke-linecap="round"/>
            </svg>
            <div class="score-center">
                <div class="score-num" style="color:{color}">{score:.0f}</div>
                <div class="score-denom">/100</div>
            </div>
        </div>
        <div class="grade-badge" style="color:{color}">{grade}</div>
        <div class="risk-label">{risk_label}</div>
    </div>"""


def render_worker_cards(workers: list) -> str:
    if not workers:
        return '<div style="color:#6b7280;font-size:0.85rem;padding:1rem">Tidak ada pekerja terdeteksi.</div>'

    status_map = {
        "compliant":  ("✅ COMPLIANT",  "var(--green)"),
        "violation":  ("⚠️ VIOLATION",  "var(--orange)"),
        "critical":   ("🚨 CRITICAL",   "var(--red)"),
        "unassigned": ("❓ UNVERIFIED", "var(--accent)"),
    }
    apd_label = {"yes": "✅ Ada", "no": "❌ Tidak Ada", "undetected": "❓ N/D"}

    cards = ""
    for w in workers:
        sl, sc   = status_map.get(w["compliance"], ("?", "var(--muted)"))
        hl       = apd_label.get(w["helmet_status"], "?")
        vl       = apd_label.get(w["vest_status"],   "?")
        card_cls = w["compliance"] if w["compliance"] in ["compliant","violation","critical","unassigned"] else "unassigned"
        hc       = "color:#22c55e" if w["has_helmet"] else "color:#ef4444" if w["miss_helmet"] else "color:#6b7280"
        vc       = "color:#22c55e" if w["has_vest"]   else "color:#ef4444" if w["miss_vest"]   else "color:#6b7280"

        cards += f"""
        <div class="worker-card {card_cls}">
            <div class="worker-id">WORKER #{w['id']:02d} · {w['conf']:.0%}</div>
            <div class="worker-status" style="color:{sc}">{sl}</div>
            <div class="worker-apd-row"><span>🪖 Helmet</span><span style="{hc}">{hl}</span></div>
            <div class="worker-apd-row"><span>🦺 Vest</span><span style="{vc}">{vl}</span></div>
            <div class="worker-footer">
                IoU helm:{w['helmet_iou']:.3f} nh:{w['no_helmet_iou']:.3f}<br>
                IoU vest:{w['vest_iou']:.3f} nv:{w['no_vest_iou']:.3f}
            </div>
        </div>"""

    return f'<div class="worker-grid">{cards}</div>'


def render_score_breakdown(sd: dict) -> str:
    if not sd["breakdown"]:
        return ""
    rows = ""
    for b in sd["breakdown"]:
        color = {"compliant":"#22c55e","violation":"#f97316","critical":"#ef4444","unassigned":"#f0c040"}.get(b["compliance"], "#6b7280")
        p     = b["penalty"]
        rows += f"""
        <tr>
            <td>Worker #{b['worker_id']:02d}</td>
            <td><span class="badge" style="background:rgba(0,0,0,0.3);color:{color}">{b['compliance'].upper()}</span></td>
            <td style="color:{'#ef4444' if p>0 else '#22c55e'};text-align:center">{'−' if p>0 else ''}{p}</td>
            <td style="color:#6b7280;font-size:0.72rem">{b['desc']}</td>
        </tr>"""

    systemic_row = ""
    if sd["systemic"]:
        systemic_row = f"""
        <tr style="border-top:1px solid #1e2229">
            <td colspan="2" style="color:#f97316">⚠️ Systemic Multiplier (×0.8)</td>
            <td style="color:#f97316;text-align:center">×0.8</td>
            <td style="color:#6b7280;font-size:0.72rem">Violation rate {sd['violation_rate']}% &gt; 50%</td>
        </tr>"""

    return f"""
    <div class="panel">
        <table class="det-table">
            <thead><tr><th>Worker</th><th>Status</th><th style="text-align:center">Penalty</th><th>Keterangan</th></tr></thead>
            <tbody>
                {rows}
                {systemic_row}
                <tr style="border-top:1px solid #1e2229">
                    <td colspan="2"><b>Raw Score</b></td>
                    <td style="text-align:center;font-weight:700">100 − {sd['raw_penalty']} = {sd['raw_score']}</td>
                    <td></td>
                </tr>
                <tr>
                    <td colspan="2"><b style="color:{sd['color']}">Final Score</b></td>
                    <td style="text-align:center;font-weight:800;color:{sd['color']}">{sd['score']:.1f}</td>
                    <td style="color:{sd['color']};font-weight:700">{sd['recommendation']}</td>
                </tr>
            </tbody>
        </table>
    </div>"""


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='margin-bottom:1.5rem'>
        <div style='font-size:1.3rem;font-weight:800;color:#f0c040'>⚙️ Konfigurasi</div>
        <div style='font-size:0.72rem;color:#6b7280;font-family:IBM Plex Mono,monospace;letter-spacing:0.05em'>CONSTRUCTION SAFETY MONITOR</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**📁 Model**")
    model_path = st.text_input("Path ke best.pt", value="best_construction.pt", label_visibility="collapsed")

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
    st.markdown("**🎯 Detection**")
    conf_threshold = st.slider("Confidence Threshold", 0.1, 0.9, 0.4, 0.05)
    iou_threshold  = st.slider("IoU Threshold (NMS)", 0.1, 0.9, 0.45, 0.05)

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
    st.markdown("**🔗 Worker Assignment**")
    assignment_iou = st.slider(
        "Min IoU for APD Assignment", 0.01, 0.3, 0.05, 0.01,
        help="IoU minimum antara APD bbox dan zona worker agar dianggap match"
    )

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
    st.markdown("**🎨 Visualisasi**")
    show_conf         = st.toggle("Confidence score", value=True)
    show_labels       = st.toggle("Label text", value=True)
    show_worker_annot = st.toggle("Worker annotation overlay", value=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#0a0c10;border:1px solid #1e2229;border-radius:6px;padding:1rem;font-size:0.74rem;color:#6b7280;font-family:IBM Plex Mono,monospace;line-height:2'>
        <b style='color:#f0c040'>WORKER STATUS</b><br>
        <span style='color:#22c55e'>█</span> COMPLIANT<br>
        <span style='color:#f97316'>█</span> VIOLATION (1 APD)<br>
        <span style='color:#ef4444'>█</span> CRITICAL (0 APD)<br>
        <span style='color:#f0c040'>█</span> UNVERIFIED<br><br>
        <b style='color:#f0c040'>SAFETY GRADE</b><br>
        <span style='color:#22c55e'>A</span> ≥90 EXCELLENT<br>
        <span style='color:#86efac'>B</span> ≥75 GOOD<br>
        <span style='color:#f97316'>C</span> ≥60 MODERATE<br>
        <span style='color:#ef4444'>D</span> ≥40 HIGH RISK<br>
        <span style='color:#dc2626'>F</span> &lt;40 CRITICAL
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════

st.markdown("""
<div class="header-banner">
    <p class="header-title">🦺 Construction Safety Monitor</p>
    <p class="header-sub">CAPSTONE PROJECT MODULE 4 · YOLOv8 · PER-WORKER APD ASSIGNMENT · SEVERITY SCORING</p>
</div>
""", unsafe_allow_html=True)

# ── Load model ────────────────────────────────────────────────
model = None
if os.path.exists(model_path):
    with st.spinner("Memuat model..."):
        try:
            model       = load_model(model_path)
            class_names = model.names
            if isinstance(class_names, dict):
                class_names = [class_names[i] for i in range(len(class_names))]
            st.success(f"✅ Model dimuat — {len(class_names)} class terdeteksi")
        except Exception as e:
            st.error(f"❌ Gagal memuat model: {e}")
else:
    st.markdown("""
    <div class="info-box">
        <b>Model belum ditemukan.</b> Letakkan <b>best_construction.pt</b> di folder
        yang sama dengan <b>app.py</b>, atau ubah path di sidebar.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════

tab1, tab2, tab3 = st.tabs(["📸 Upload & Deteksi", "📹 Kamera Langsung", "ℹ️ Tentang Model"])


# ═══════════════════════════════════════════════════════════════
# TAB 1
# ═══════════════════════════════════════════════════════════════
with tab1:
    uploaded = st.file_uploader(
        "Upload gambar area konstruksi (JPG / PNG / JPEG)",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded is not None and model is not None:
        file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
        img_bgr    = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        img_rgb    = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        with st.spinner("🔍 Mendeteksi & menganalisis..."):
            t0         = time.time()
            results    = model(img_rgb, conf=conf_threshold, iou=iou_threshold, verbose=False)
            elapsed    = time.time() - t0
            report     = analyze_safety(results, class_names)
            workers    = assign_apd_to_workers(results, class_names, assignment_iou)
            score_data = compute_severity_score(workers)

        # Annotate
        ann_bgr = results[0].plot(conf=show_conf, labels=show_labels, line_width=2)
        ann_rgb = cv2.cvtColor(ann_bgr, cv2.COLOR_BGR2RGB)
        worker_ann = draw_worker_annotations(ann_rgb, workers) if show_worker_annot else ann_rgb

        # ── SECTION A: Gambar & Summary ───────────────────────
        col_img, col_stats = st.columns([3, 2], gap="large")

        with col_img:
            st.markdown('<div class="section-label">Hasil Deteksi + Worker Annotation</div>', unsafe_allow_html=True)
            st.image(worker_ann, use_container_width=True)
            col_orig, col_info = st.columns(2)
            with col_orig:
                st.markdown('<div class="section-label">Original</div>', unsafe_allow_html=True)
                st.image(img_rgb, use_container_width=True)
            with col_info:
                h, w = img_rgb.shape[:2]
                st.markdown(f"""
                <div class="panel" style="height:100%;font-family:'IBM Plex Mono',monospace;font-size:0.78rem;line-height:2.1">
                    <div class="section-label">Inference Info</div>
                    <div>⏱ Waktu     : <b style="color:#f0c040">{elapsed*1000:.0f} ms</b></div>
                    <div>📐 Resolusi  : <b style="color:#f0c040">{w}×{h}px</b></div>
                    <div>📦 Deteksi   : <b style="color:#f0c040">{len(results[0].boxes)} objek</b></div>
                    <div>👷 Workers   : <b style="color:#f0c040">{len(workers)} orang</b></div>
                    <div>🎯 Conf thr  : <b style="color:#f0c040">{conf_threshold}</b></div>
                    <div>🔗 Assign IoU: <b style="color:#f0c040">{assignment_iou}</b></div>
                </div>
                """, unsafe_allow_html=True)

        with col_stats:
            # Status badge
            rc = {"AMAN":"status-aman","WASPADA":"status-waspada","BAHAYA":"status-bahaya"}
            st.markdown(f"""
            <div class="status-badge {rc[report['risk']]}">
                <span style="font-size:1.4rem">{report['emoji']}</span>
                <span>{report['risk']} — {report['detail']}</span>
            </div>""", unsafe_allow_html=True)

            # 5 metric cards (tambah Safety Score)
            sc_color = score_data["color"]
            sc_disp  = f"{score_data['score']:.0f}" if score_data["score"] is not None else "N/A"
            st.markdown(f"""
            <div class="metric-grid-5">
                <div class="metric-card yellow">
                    <div class="metric-label">Pekerja</div>
                    <div class="metric-value">{report['total_persons']}</div>
                    <div class="metric-sub">detected</div>
                </div>
                <div class="metric-card {'red' if report['violations']>0 else 'green'}">
                    <div class="metric-label">Violations</div>
                    <div class="metric-value">{report['violations']}</div>
                    <div class="metric-sub">APD missing</div>
                </div>
                <div class="metric-card {'green' if report['helmet_pct']>=80 else 'orange' if report['helmet_pct']>=50 else 'red'}">
                    <div class="metric-label">Helmet</div>
                    <div class="metric-value">{report['helmet_pct']:.0f}%</div>
                    <div class="metric-sub">compliance</div>
                </div>
                <div class="metric-card {'green' if report['vest_pct']>=80 else 'orange' if report['vest_pct']>=50 else 'red'}">
                    <div class="metric-label">Vest</div>
                    <div class="metric-value">{report['vest_pct']:.0f}%</div>
                    <div class="metric-sub">compliance</div>
                </div>
                <div class="metric-card" style="border-color:{sc_color}50">
                    <div style="position:absolute;top:0;left:0;width:100%;height:3px;background:{sc_color}"></div>
                    <div class="metric-label">Safety Score</div>
                    <div class="metric-value" style="color:{sc_color}">{sc_disp}</div>
                    <div class="metric-sub">grade {score_data['grade']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # APD bars
            hc = color_for_pct(report["helmet_pct"])
            vc = color_for_pct(report["vest_pct"])
            st.markdown(f"""
            <div class="panel">
                <div class="section-label">APD Compliance</div>
                <div class="apd-row">
                    <div class="apd-header">
                        <span class="apd-label">🪖 Helmet</span>
                        <span class="apd-pct">{report['wearing_helmet']} pakai / {report['missing_helmet']} tidak — {report['helmet_pct']}%</span>
                    </div>
                    <div class="progress-track"><div class="progress-fill" style="width:{report['helmet_pct']}%;background:{hc}"></div></div>
                </div>
                <div class="apd-row" style="margin-top:0.8rem">
                    <div class="apd-header">
                        <span class="apd-label">🦺 Rompi / Vest</span>
                        <span class="apd-pct">{report['wearing_vest']} pakai / {report['missing_vest']} tidak — {report['vest_pct']}%</span>
                    </div>
                    <div class="progress-track"><div class="progress-fill" style="width:{report['vest_pct']}%;background:{vc}"></div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── SECTION B: Per-Worker Cards ─────────────
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("""
        <div class="section-label">Per-Worker APD Assignment</div>
        <div class="info-box">
            <b>IoU-based Individual Analysis:</b> Setiap worker dianalisis secara terpisah.
            Helmet di-match ke <b>head zone (top 35%)</b> dari bbox worker,
            vest di-match ke <b>full body zone</b>.
            Warna bbox → <span style="color:#22c55e">■ SAFE</span>
            <span style="color:#f97316">■ VIOLATION</span>
            <span style="color:#ef4444">■ CRITICAL</span>
            <span style="color:#f0c040">■ UNVERIFIED</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(render_worker_cards(workers), unsafe_allow_html=True)

        # ── SECTION C: Severity Score  ───────────────
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("""
        <div class="section-label">Severity Score & Safety Grade</div>
        <div class="info-box">
            <b>Weighted Penalty Scoring:</b> Skor 0–100 berdasarkan bobot pelanggaran per worker.
            Missing helmet = −25pt · Missing vest = −15pt · Keduanya = extra −10pt.
            Violation rate &gt;50% → <b>systemic multiplier ×0.8</b>.
        </div>
        """, unsafe_allow_html=True)

        col_ring, col_break = st.columns([1, 3], gap="large")
        with col_ring:
            st.markdown(
                render_severity_ring(score_data["score"], score_data["grade"],
                                     score_data["color"], score_data["risk_label"]),
                unsafe_allow_html=True,
            )
            st.markdown(f"""
            <div style="text-align:center;font-size:0.78rem;color:#6b7280;font-family:'IBM Plex Mono',monospace;line-height:2;margin-top:0.5rem">
                <div>Violations : <b style="color:{score_data['color']}">{score_data['violation_count']}/{len(workers)}</b></div>
                <div>Viol. rate : <b style="color:{score_data['color']}">{score_data.get('violation_rate',0)}%</b></div>
                <div>Systemic   : <b style="color:{'#f97316' if score_data['systemic'] else '#22c55e'}">{'YA' if score_data['systemic'] else 'TIDAK'}</b></div>
            </div>
            <div style="margin-top:1rem;font-size:0.7rem;font-family:'IBM Plex Mono',monospace;line-height:2;color:#6b7280">
                <span style="color:#22c55e">A</span> ≥90 EXCELLENT<br>
                <span style="color:#86efac">B</span> ≥75 GOOD<br>
                <span style="color:#f97316">C</span> ≥60 MODERATE<br>
                <span style="color:#ef4444">D</span> ≥40 HIGH RISK<br>
                <span style="color:#dc2626">F</span> &lt;40 CRITICAL
            </div>
            """, unsafe_allow_html=True)

        with col_break:
            st.markdown('<div class="section-label">Penalty Breakdown</div>', unsafe_allow_html=True)
            st.markdown(render_score_breakdown(score_data), unsafe_allow_html=True)
            if score_data["score"] is not None:
                sc_color = score_data["color"]
                st.markdown(f"""
                <div style="margin-top:1rem;background:rgba(0,0,0,0.3);border:1px solid {sc_color}40;
                     border-left:3px solid {sc_color};border-radius:6px;padding:0.9rem 1.1rem">
                    <div style="font-size:0.7rem;color:#6b7280;font-family:'IBM Plex Mono',monospace;
                         letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.4rem">Rekomendasi Tindakan</div>
                    <div style="font-weight:700;color:{sc_color}">{score_data['recommendation']}</div>
                </div>
                """, unsafe_allow_html=True)

        # ── SECTION D: Detection Count & Top Detections ───────
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        col_cnt, col_top = st.columns(2, gap="large")

        with col_cnt:
            st.markdown('<div class="section-label">Detection Count</div>', unsafe_allow_html=True)
            badge_map = {
                "helmet":"badge-green","vest":"badge-green",
                "person":"badge-yellow","no-helmet":"badge-red","no-vest":"badge-red",
            }
            label_map = {
                "helmet":"APD ✓","vest":"APD ✓",
                "person":"Person","no-helmet":"VIOLATION","no-vest":"VIOLATION",
            }
            rows = "".join([
                f"<tr><td>{cls}</td><td style='text-align:center'><b>{cnt}</b></td>"
                f"<td><span class='badge {badge_map.get(cls, 'badge-blue')}'>{label_map.get(cls, '')}</span></td></tr>"
                 for cls, cnt in sorted(report["counts"].items(), key=lambda x: -x[1])
])
            st.markdown(f"""
            <div class="panel">
                <table class="det-table">
                    <thead><tr><th>Class</th><th style="text-align:center">Count</th><th>Status</th></tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>""", unsafe_allow_html=True)

        with col_top:
            st.markdown('<div class="section-label">Top Detections</div>', unsafe_allow_html=True)
            det_rows = "".join(
                f"<tr><td style='color:#6b7280'>{i:02d}</td>"
                f"<td><span class='badge {'badge-red' if 'no-' in d['class'] else 'badge-green' if d['class'] in ['helmet','vest'] else 'badge-yellow'}'>{d['class']}</span></td>"
                f"<td style='color:{'#22c55e' if d['conf']>=0.7 else '#f97316' if d['conf']>=0.5 else '#ef4444'}'>{d['conf']:.2%}</td></tr>"
                for i, d in enumerate(report["detections"][:8], 1)
            )
            st.markdown(f"""
            <div class="panel">
                <table class="det-table">
                    <thead><tr><th>#</th><th>Class</th><th>Conf</th></tr></thead>
                    <tbody>{det_rows}</tbody>
                </table>
            </div>""", unsafe_allow_html=True)

        # ── Download ──────────────────────────────────────────
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        buf = io.BytesIO()
        Image.fromarray(worker_ann).save(buf, format="PNG")
        st.download_button(
            "⬇️ Download Hasil Deteksi", buf.getvalue(),
            f"construction_safety_{int(time.time())}.png", "image/png",
        )

    elif uploaded is not None and model is None:
        st.warning("⚠️ Model belum dimuat. Pastikan path model benar di sidebar.")
    else:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:#6b7280">
            <div style="font-size:4rem;margin-bottom:1rem">📷</div>
            <div style="font-size:1.1rem;font-weight:600;color:#9ca3af;margin-bottom:0.5rem">Upload gambar untuk memulai</div>
            <div style="font-size:0.82rem;font-family:'IBM Plex Mono',monospace">Mendukung format JPG, JPEG, PNG</div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TAB 2 — KAMERA
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="info-box">
        <b>Mode Kamera Langsung</b> — Analisis lengkap termasuk per-worker assignment dan severity score.
    </div>""", unsafe_allow_html=True)

    cam_img = st.camera_input("📷 Ambil Foto")

    if cam_img is not None and model is not None:
        file_bytes = np.asarray(bytearray(cam_img.read()), dtype=np.uint8)
        img_bgr    = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        img_rgb    = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        with st.spinner("🔍 Menganalisis..."):
            results    = model(img_rgb, conf=conf_threshold, iou=iou_threshold, verbose=False)
            report     = analyze_safety(results, class_names)
            workers    = assign_apd_to_workers(results, class_names, assignment_iou)
            score_data = compute_severity_score(workers)

        ann_bgr    = results[0].plot(conf=show_conf, labels=show_labels, line_width=2)
        ann_rgb    = cv2.cvtColor(ann_bgr, cv2.COLOR_BGR2RGB)
        worker_ann = draw_worker_annotations(ann_rgb, workers) if show_worker_annot else ann_rgb

        col1, col2 = st.columns([3, 2], gap="large")
        with col1:
            st.image(worker_ann, use_container_width=True)
        with col2:
            rc       = {"AMAN":"status-aman","WASPADA":"status-waspada","BAHAYA":"status-bahaya"}
            sc_color = score_data["color"]
            sc_disp  = f"{score_data['score']:.0f}" if score_data["score"] is not None else "N/A"
            st.markdown(f"""
            <div class="status-badge {rc[report['risk']]}">
                <span style="font-size:1.4rem">{report['emoji']}</span>
                <span>{report['risk']} — {report['detail']}</span>
            </div>
            <div class="metric-grid" style="grid-template-columns:repeat(2,1fr)">
                <div class="metric-card yellow"><div class="metric-label">Pekerja</div><div class="metric-value">{len(workers)}</div></div>
                <div class="metric-card" style="border-color:{sc_color}50">
                    <div style="position:absolute;top:0;left:0;width:100%;height:3px;background:{sc_color}"></div>
                    <div class="metric-label">Safety Score</div>
                    <div class="metric-value" style="color:{sc_color}">{sc_disp}</div>
                    <div class="metric-sub">grade {score_data['grade']} · {score_data['risk_label']}</div>
                </div>
                <div class="metric-card {'green' if report['helmet_pct']>=80 else 'orange'}">
                    <div class="metric-label">Helmet</div><div class="metric-value">{report['helmet_pct']:.0f}%</div>
                </div>
                <div class="metric-card {'green' if report['vest_pct']>=80 else 'orange'}">
                    <div class="metric-label">Vest</div><div class="metric-value">{report['vest_pct']:.0f}%</div>
                </div>
            </div>""", unsafe_allow_html=True)
            st.markdown(render_worker_cards(workers), unsafe_allow_html=True)

    elif cam_img is not None and model is None:
        st.warning("⚠️ Model belum dimuat.")


# ═══════════════════════════════════════════════════════════════
# TAB 3 — TENTANG MODEL
# ═══════════════════════════════════════════════════════════════
with tab3:
    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown("""
        <div class="section-label">Informasi Model</div>
        <div class="panel" style="font-size:0.85rem;line-height:2;font-family:'IBM Plex Mono',monospace">
            <div>🤖 <b style="color:#f0c040">Arsitektur</b>     : YOLOv8n (Nano)</div>
            <div>🎓 <b style="color:#f0c040">Strategy</b>       : Fine-tuning (Transfer Learning)</div>
            <div>📦 <b style="color:#f0c040">Base Weights</b>   : COCO pretrained</div>
            <div>🖼️ <b style="color:#f0c040">Input Size</b>     : 640 × 640 px</div>
            <div>🏷️ <b style="color:#f0c040">Classes</b>        : 5 (person, helmet, no-helmet, vest, no-vest)</div>
            <div>⏱️ <b style="color:#f0c040">Training</b>       : 50 epoch (early stop @40)</div>
            <div>💾 <b style="color:#f0c040">Model Size</b>     : ~6 MB</div>
            <div>🔗 <b style="color:#f0c040">APD Assignment</b> : IoU-based per worker (head zone + body zone)</div>
            <div>📊 <b style="color:#f0c040">Scoring</b>        : Weighted penalty 0–100 + grade A–F</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="section-label" style="margin-top:1.5rem">Hasil Evaluasi (Validation Set)</div>
        <div class="panel">
        """, unsafe_allow_html=True)
        for name, val, color in [("mAP@50",83.86,"#22c55e"),("mAP@50-95",44.55,"#f97316"),("Precision",79.03,"#60a5fa"),("Recall",81.26,"#a78bfa")]:
            st.markdown(f"""
            <div class="apd-row">
                <div class="apd-header"><span class="apd-label">{name}</span><span class="apd-pct" style="color:{color};font-weight:700">{val}%</span></div>
                <div class="progress-track"><div class="progress-fill" style="width:{val}%;background:{color}"></div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="section-label" style="margin-top:1.5rem">Penalty Weight Table</div>
        <div class="panel">
            <table class="det-table">
                <thead><tr><th>Pelanggaran</th><th>Penalty</th><th>Alasan</th></tr></thead>
                <tbody>
                    <tr><td>Missing Helmet</td><td style="color:#ef4444">−25 pt</td><td style="color:#6b7280;font-size:0.75rem">Head protection = prioritas tertinggi</td></tr>
                    <tr><td>Missing Vest</td><td style="color:#f97316">−15 pt</td><td style="color:#6b7280;font-size:0.75rem">Visibility = prioritas medium</td></tr>
                    <tr><td>Missing Both (+extra)</td><td style="color:#dc2626">−50 pt</td><td style="color:#6b7280;font-size:0.75rem">Zero APD → extra penalty −10pt</td></tr>
                    <tr><td>Systemic (&gt;50% viol.)</td><td style="color:#f97316">×0.8</td><td style="color:#6b7280;font-size:0.75rem">Kondisi sistemik lebih berbahaya</td></tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="section-label">mAP@50 per Class</div>
        <div class="panel">
        """, unsafe_allow_html=True)
        for cls, val, color in [("person",93.56,"#22c55e"),("helmet",90.82,"#22c55e"),("vest",88.73,"#22c55e"),("no-vest",80.43,"#f97316"),("no-helmet",64.75,"#ef4444")]:
            st.markdown(f"""
            <div class="apd-row">
                <div class="apd-header"><span class="apd-label">{cls}</span><span class="apd-pct" style="color:{color};font-weight:700">{val}%</span></div>
                <div class="progress-track"><div class="progress-fill" style="width:{val}%;background:{color}"></div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="section-label" style="margin-top:1.5rem">Dataset Info</div>
        <div class="panel" style="font-size:0.82rem;line-height:2;font-family:'IBM Plex Mono',monospace">
            <div>📂 <b style="color:#f0c040">Dataset</b>       : Construction Safety v1 (Roboflow)</div>
            <div>🖼️ <b style="color:#f0c040">Total</b>         : 1.206 gambar</div>
            <div>🏋️ <b style="color:#f0c040">Train</b>         : 997 gambar</div>
            <div>✅ <b style="color:#f0c040">Valid</b>         : 119 gambar</div>
            <div>🧪 <b style="color:#f0c040">Test</b>          : 90 gambar</div>
            <div>🏷️ <b style="color:#f0c040">Annotations</b>   : 7.724 bounding box</div>
            <div>⚠️ <b style="color:#f0c040">Class Imbalance</b>: no-helmet hanya 1.7%</div>
        </div>
        <div class="info-box" style="margin-top:1rem">
            <b>Catatan Class Imbalance:</b> Class <b>no-helmet</b> memiliki mAP terendah (64.75%)
            karena jumlah sampel training hanya <b>129 dari 7.724 total objek (1.7%)</b>.
            Untuk meningkatkan performa bisa menggunakan weighted loss atau oversampling.
        </div>
        """, unsafe_allow_html=True)