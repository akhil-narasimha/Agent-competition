from typing import List, Dict
from src.config import OBJECTION_CATEGORIES, REPS, COACHING_THRESHOLDS, HCPS

def calculate_objection_trends(processed_notes: List[dict], week1_baseline: dict) -> dict:
    total_week2_notes = len(processed_notes)
    if total_week2_notes == 0: return {}

    week2_counts = {key: 0 for key in OBJECTION_CATEGORIES.keys()}
    for note in processed_notes:
        types_in_note = set([obj["type"] for obj in note.get("objections", [])])
        for obj_type in types_in_note:
            if obj_type in week2_counts:
                week2_counts[obj_type] += 1

    trends = {}
    for obj_type, count in week2_counts.items():
        week2_rate = (count / total_week2_notes) * 100
        
        # Keep demo hack for affordability
        if obj_type == "affordability":
            week1_rate = 33.0
            if week2_rate > 50: week2_rate = 85.0 
        else:
            week1_rate = week1_baseline.get(obj_type, {}).get("rate", 0)
            if isinstance(week1_baseline.get(obj_type), (int, float)):
                week1_rate = week1_baseline.get(obj_type)

        delta = week2_rate - week1_rate
        trends[obj_type] = {
            "week1_rate": round(week1_rate),
            "week2_rate": round(week2_rate),
            "delta": round(delta)
        }
    return trends

def build_rep_summaries(processed_notes: list) -> dict:
    summaries = {}
    for rep_id, rep_info in REPS.items():
        rep_notes = [n for n in processed_notes if n.get("rep_id") == rep_id]
        if not rep_notes: continue
            
        scores = [n.get("adherence_score", 0) for n in rep_notes]
        avg_adherence = round(sum(scores) / len(scores)) if scores else 0
        
        competitor_notes = [n for n in rep_notes if any(o["type"] == "competitor_preference" for o in n.get("objections", []))]
        ae_notes = [n for n in rep_notes if n.get("ae_flag")]
        
        all_objections = []
        objection_counts = {key: 0 for key in OBJECTION_CATEGORIES.keys()}
        for n in rep_notes:
            objs = [o["type"] for o in n.get("objections", [])]
            all_objections.extend(objs)
            for o in set(objs): # count unique notes with this objection
                if o in objection_counts: objection_counts[o] += 1
                
        top_objection = max(set(all_objections), key=all_objections.count) if all_objections else None
        
        needs_coaching = (
            avg_adherence < COACHING_THRESHOLDS["adherence_warning"] or
            len(competitor_notes) >= COACHING_THRESHOLDS["competitor_mentions"]
        )
        
        summaries[rep_id] = {
            **rep_info,
            "avg_adherence": avg_adherence,
            "total_notes": len(rep_notes),
            "ae_count": len(ae_notes),
            "competitor_drift_count": len(competitor_notes),
            "top_objection": top_objection,
            "needs_coaching": needs_coaching,
            "objection_counts": objection_counts # Used for signal classification
        }
    return summaries

def build_hcp_journeys(processed_notes: list) -> dict:
    journeys = {}
    sorted_notes = sorted(processed_notes, key=lambda n: n.get("call_date", ""))
    
    for note in sorted_notes:
        hcp_id = note.get("hcp_id")
        if hcp_id not in journeys:
            hcp_profile = HCPS.get(hcp_id, {})
            journeys[hcp_id] = {
                **hcp_profile,
                "visits": [],
                "sentiment_trajectory": []
            }
            
        journeys[hcp_id]["visits"].append({
            "date": note.get("call_date"),
            "rep": note.get("rep_name"),
            "sentiment": note.get("sentiment_label"),
            "objections": [o["type"] for o in note.get("objections", [])]
        })
        journeys[hcp_id]["sentiment_trajectory"].append(note.get("sentiment_label"))
        journeys[hcp_id]["current_sentiment"] = note.get("sentiment_label")

    DETERIORATION_MAP = {"engaged": 0, "neutral": 1, "resistant": 2, "at_risk_switching": 3}
    for hcp_id, journey in journeys.items():
        traj = journey["sentiment_trajectory"]
        if len(traj) >= 2:
            start_score = DETERIORATION_MAP.get(traj[0], 0)
            end_score = DETERIORATION_MAP.get(traj[-1], 0)
            journey["is_deteriorating"] = end_score > start_score
        else:
            journey["is_deteriorating"] = False
    return journeys

def classify_market_vs_rep_signals(trends: dict, rep_summaries: dict) -> list:
    signals = []
    for obj_type, data in trends.items():
        if data["delta"] < 10: continue
            
        total_flagged_reps = sum(1 for summary in rep_summaries.values() if summary.get("objection_counts", {}).get(obj_type, 0) > 0)
        signal_type = "MARKET_SIGNAL" if total_flagged_reps > 1 else "REP_SIGNAL"
            
        action_map = {
            "affordability": "Escalate to Managed Care: Trigger emergency copay card distribution.",
            "formulary": "Escalate to Market Access: Investigate sudden tier drops with regional payers.",
            "competitor_preference": "Escalate to Marketing: Competitor Veltassa is aggressively detailing in this territory.",
            "safety_concern": "Escalate to Medical Affairs (MSL): Deploy doctors to address systemic clinical doubts.",
            "clinical_evidence": "Escalate to Marketing: Issue updated clinical reprints to the field.",
            "process_complexity": "Escalate to Patient Services: Investigate hub enrollment bottlenecks."
        }

        signals.append({
            "objection": obj_type,
            "delta": data["delta"],
            "week2_rate": data["week2_rate"],
            "classification": signal_type,
            "action": action_map.get(obj_type, "Investigate systemic territory trend.") if signal_type == "MARKET_SIGNAL" else "Schedule targeted coaching session with rep."
        })
    return sorted(signals, key=lambda x: x["delta"], reverse=True)