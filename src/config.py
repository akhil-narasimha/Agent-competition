"""
config.py — Rep Signal Intelligence System
All hardcoded configuration for the POC demo.
Product: LOKELMA (Sodium Zirconium Cyclosilicate)
"""

# ─────────────────────────────────────────────
# SCHEMA REFERENCE
# ─────────────────────────────────────────────

SCHEMA = {
    "note_id":              "Unique note identifier (N001–N025)",
    "rep_id":               "Rep identifier (R01 = Priya, R02 = Rahul)",
    "rep_name":             "Full name of the sales rep",
    "territory":            "Territory name",
    "hcp_id":               "Unique HCP identifier",
    "hcp_name":             "Doctor name",
    "hcp_specialty":        "Nephrology or Cardiology",
    "hcp_tier":             "1 = High value, 2 = Mid tier",
    "call_date":            "Date of visit (YYYY-MM-DD)",
    "week_label":           "Week 1 (Apr 14–17) or Week 2 (Apr 21–24)",
    "product":              "Product discussed (LOKELMA)",
    "call_duration_mins":   "Duration of the sales call in minutes",
    "note_text":            "Free-text call note entered by rep in Veeva CRM",
}


# ─────────────────────────────────────────────
# PRODUCT CORE MESSAGES
# Used by: Message Adherence Scorer Agent
# ─────────────────────────────────────────────

CORE_MESSAGES = {
    "LOKELMA": [
        {
            "id": "CM1",
            "label": "Rapid Onset",
            "description": "LOKELMA works within 1 hour — significantly faster than older potassium binders",
            "keywords": ["rapid onset", "within 1 hour", "1 hour", "fast acting", "quick", "onset of action", "within an hour"],
            "weight": 30,  # importance weight out of 100
        },
        {
            "id": "CM2",
            "label": "DAPA-CKD Clinical Evidence",
            "description": "Proven efficacy in CKD patients — DAPA-CKD trial demonstrates sustained potassium control",
            "keywords": ["DAPA-CKD", "clinical trial", "clinical data", "trial data", "evidence", "study", "CKD trial", "proven"],
            "weight": 30,
        },
        {
            "id": "CM3",
            "label": "Patient Assistance Program",
            "description": "Patient assistance program available — same-day approval for qualifying patients, simplified enrollment",
            "keywords": ["patient assistance", "assistance program", "assistance card", "copay support", "financial support", "enrollment", "assistance"],
            "weight": 20,
        },
        {
            "id": "CM4",
            "label": "RAASi Enablement",
            "description": "Enables continued RAASi therapy in HF/CKD patients by controlling hyperkalemia",
            "keywords": ["RAASi", "RAAS", "renin", "ACE inhibitor", "ARB", "heart failure", "HFrEF", "RAASi enablement", "continue therapy"],
            "weight": 20,
        },
    ]
}


# ─────────────────────────────────────────────
# ADVERSE EVENT SIGNAL KEYWORDS
# Used by: AE Detector Agent
# These are NOT definitive AE indicators — they are pre-screening signals
# Final classification is ALWAYS done by Pharmacovigilance team
# ─────────────────────────────────────────────

AE_SIGNAL_PATTERNS = {
    "symptom_keywords": [
        "muscle weakness", "fatigue", "nausea", "dizziness", "faint",
        "swelling", "ankle swelling", "side effect", "adverse", "reaction",
        "felt unwell", "complained", "symptoms", "complaint", "tolerate",
        "stopped medication", "paused medication", "discontinued",
        "shortness of breath", "chest pain", "palpitations", "rash",
        "itching", "vomiting", "diarrhea", "constipation", "abdominal pain",
        "weakness", "lightheaded", "confusion", "headache"
    ],
    "temporal_keywords": [
        "after starting", "after taking", "after initiation", "after beginning",
        "days after", "weeks after", "since starting", "since taking",
        "following treatment", "post initiation", "on treatment",
        "into treatment", "into therapy"
    ],
    "concern_keywords": [
        "not sure if related", "concerned", "hesitant", "worried",
        "paused", "stopped", "discontinued", "reduced dose",
        "causality", "safety concern", "safety question"
    ],
    "severity_indicators": {
        "high": ["severe", "significant", "serious", "hospitalized", "emergency"],
        "medium": ["moderate", "persistent", "ongoing", "worsening"],
        "low": ["mild", "minor", "slight", "brief"]
    }
}

# Notes that contain AE signals (ground truth for demo validation)
KNOWN_AE_NOTES = ["N014", "N019"]


# ─────────────────────────────────────────────
# OBJECTION TAXONOMY
# Used by: Objection Extractor Agent
# ─────────────────────────────────────────────

OBJECTION_CATEGORIES = {
    "affordability": {
        "label": "Affordability / Cost",
        "keywords": [
            "afford", "cost", "expensive", "price", "copay", "co-pay",
            "cheaper", "generic", "insurance", "out of pocket", "budget",
            "lower income", "fixed income", "can't afford", "pricing"
        ],
        "type": "access",  # access | clinical | competitive | behavioral
    },
    "formulary": {
        "label": "Formulary / Coverage Gap",
        "keywords": [
            "formulary", "coverage", "formulary tier", "tier", "not covered",
            "higher tier", "step therapy", "prior auth", "PA required",
            "payer", "insurance coverage", "reimbursement"
        ],
        "type": "access",
    },
    "competitor_preference": {
        "label": "Competitor Preference (Veltassa)",
        "keywords": [
            "Veltassa", "competitor", "other product", "switching",
            "colleagues use", "prefer", "already on", "currently prescribing"
        ],
        "type": "competitive",
    },
    "safety_concern": {
        "label": "Safety / Tolerability Concern",
        "keywords": [
            "safety", "side effect", "tolerability", "adverse", "concern",
            "risk", "hesitant", "worried about", "not safe", "uncertain"
        ],
        "type": "clinical",
    },
    "clinical_evidence": {
        "label": "Needs More Clinical Evidence",
        "keywords": [
            "evidence", "data", "proof", "outcomes", "real world",
            "study", "need to see", "not convinced", "more data"
        ],
        "type": "clinical",
    },
    "process_complexity": {
        "label": "Patient Assistance Program Complexity",
        "keywords": [
            "complicated", "complex", "confusing", "difficult process",
            "hard to enroll", "takes too long", "renewal", "paperwork"
        ],
        "type": "behavioral",
    },
}


# ─────────────────────────────────────────────
# SENTIMENT CLASSIFICATION
# Used by: HCP Sentiment Classifier Agent
# ─────────────────────────────────────────────

SENTIMENT_LABELS = {
    "engaged":            "✅ Engaged — actively prescribing or committed to trial",
    "neutral":            "🟡 Neutral — open but not yet committed",
    "resistant":          "⚠️ Resistant — consistent objections, not prescribing",
    "at_risk_switching":  "🔴 At-Risk of Switching — actively considering competitor",
}


# ─────────────────────────────────────────────
# COACHING TRIGGER THRESHOLDS
# Used by: Coaching Recommendation Agent
# ─────────────────────────────────────────────

COACHING_THRESHOLDS = {
    "adherence_warning":    60,   # below this → coaching recommended
    "adherence_critical":   40,   # below this → urgent coaching
    "competitor_mentions":  2,    # per week → flag competitor drift
    "unhandled_objections": 2,    # same objection unresolved across calls
}


# ─────────────────────────────────────────────
# WEEK-OVER-WEEK BASELINE (WEEK 1 ACTUALS)
# Pre-computed from Week 1 data — used for trend comparison in demo
# This is what the trend engine compares Week 2 against
# ─────────────────────────────────────────────

WEEK1_BASELINE = {
    "total_calls": 12,
    "objection_rates": {
        "affordability":         {"count": 4, "rate": 33.3},   # Notes N002, N004, N006, N009
        "formulary":             {"count": 1, "rate": 8.3},    # Note N009 (coverage mention)
        "competitor_preference": {"count": 2, "rate": 16.7},   # Notes N003, N009
        "safety_concern":        {"count": 0, "rate": 0.0},
        "clinical_evidence":     {"count": 1, "rate": 8.3},    # Note N009
        "process_complexity":    {"count": 1, "rate": 8.3},    # Note N004
    },
    "rep_adherence": {
        "R01": {"score": 32, "label": "Priya Sharma"},
        "R02": {"score": 88, "label": "Rahul Menon"},
    },
    "ae_flags": 0,
    "sentiment_distribution": {
        "engaged":           2,
        "neutral":           4,
        "resistant":         2,
        "at_risk_switching": 0,
    }
}

# Expected Week 2 computed values (for demo validation)
WEEK2_EXPECTED = {
    "total_calls": 13,
    "objection_rates": {
        "affordability":         {"count": 9, "rate": 69.2},   # Notes N013–N017, N020–N022, N025
        "formulary":             {"count": 4, "rate": 30.8},   # Notes N015, N016, N022, N025
        "competitor_preference": {"count": 4, "rate": 30.8},   # Notes N013, N015, N017, N019
        "safety_concern":        {"count": 3, "rate": 23.1},   # Notes N014, N018, N019
        "clinical_evidence":     {"count": 0, "rate": 0.0},
        "process_complexity":    {"count": 2, "rate": 15.4},   # Notes N013, N016
    },
    "rep_adherence": {
        "R01": {"score": 22, "label": "Priya Sharma"},   # drops further
        "R02": {"score": 91, "label": "Rahul Menon"},    # stays strong
    },
    "ae_flags": 2,   # N014, N019
    "sentiment_distribution": {
        "engaged":           2,
        "neutral":           1,
        "resistant":         2,
        "at_risk_switching": 3,
    }
}


# ─────────────────────────────────────────────
# REP PROFILES
# Reference data for dashboard display
# ─────────────────────────────────────────────

REPS = {
    "R01": {
        "name": "Priya Sharma",
        "territory": "Hyderabad South",
        "manager": "Arjun Kapoor",
        "tenure_months": 14,
    },
    "R02": {
        "name": "Rahul Menon",
        "territory": "Hyderabad North",
        "manager": "Arjun Kapoor",
        "tenure_months": 28,
    }
}

# ─────────────────────────────────────────────
# HCP PROFILES
# ─────────────────────────────────────────────

HCPS = {
    "H01": {"name": "Dr. Arun Mehta",    "specialty": "Nephrology", "hospital": "Yashoda Hospital",   "tier": 2, "rep": "R01"},
    "H02": {"name": "Dr. Shalini Kapoor","specialty": "Nephrology", "hospital": "KIMS Hospital",       "tier": 2, "rep": "R01"},
    "H03": {"name": "Dr. Vikram Rao",    "specialty": "Cardiology", "hospital": "Vikram Clinic",       "tier": 2, "rep": "R01"},
    "H04": {"name": "Dr. Ramesh Sharma", "specialty": "Nephrology", "hospital": "Care Hospitals",      "tier": 1, "rep": "R01"},
    "H05": {"name": "Dr. Aditya Singh",  "specialty": "Nephrology", "hospital": "Apollo Hospital",     "tier": 1, "rep": "R02"},
    "H06": {"name": "Dr. Nikhil Patel",  "specialty": "Cardiology", "hospital": "KIMS Hospital",       "tier": 2, "rep": "R02"},
    "H07": {"name": "Dr. Pradeep Nair",  "specialty": "Nephrology", "hospital": "Banjara Clinic",      "tier": 2, "rep": "R02"},
    "H08": {"name": "Dr. Suresh Reddy",  "specialty": "Cardiology", "hospital": "Sunshine Hospital",   "tier": 2, "rep": "R02"},
}
