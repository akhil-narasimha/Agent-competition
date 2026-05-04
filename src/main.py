import pandas as pd
import asyncio
from collections import Counter
from src.graph.workflow import app
from src.graph.aggregator import calculate_objection_trends, build_rep_summaries, build_hcp_journeys, classify_market_vs_rep_signals
from src.config import WEEK1_BASELINE
from src.utils.llm_client import call_agent_json

async def generate_rep_coaching(rep_summary: dict, rep_notes: list) -> str:
    all_objections = []
    for n in rep_notes:
        all_objections.extend([o["type"] for o in n.get("objections", [])])
    most_common = Counter(all_objections).most_common(3)
    
    missed_msgs = set()
    for n in rep_notes:
        delivered = n.get("messages_delivered", [])
        missed_msgs.update([m for m in ["CM1","CM2","CM3","CM4"] if m not in delivered])
        
    prompt = f"""You are a pharma sales coach writing a weekly coaching brief.
Rep: {rep_summary['name']}, Territory: {rep_summary['territory']}
Avg adherence this week: {rep_summary['avg_adherence']}/100
Consistently missed messages: {list(missed_msgs)}
Top objections from HCPs this week: {most_common}

Write a 4-sentence coaching brief telling the rep exactly what to say next week.
Return JSON: {{"coaching_brief": "..."}}"""

    result = await call_agent_json(prompt, "")
    return result.get("coaching_brief", "")

async def process_all_notes(raw_notes: list):
    """
    Processes a list of note dictionaries concurrently through LangGraph.
    """
    print(f"Loaded {len(raw_notes)} notes. Firing LangGraph parallel execution...")
    
    tasks = [app.ainvoke(note) for note in raw_notes]
    processed_notes = await asyncio.gather(*tasks)
    
    # Run the new intelligence aggregators
    trends = calculate_objection_trends(processed_notes, WEEK1_BASELINE)
    rep_summaries = build_rep_summaries(processed_notes)
    hcp_journeys = build_hcp_journeys(processed_notes)
    market_signals = classify_market_vs_rep_signals(trends, rep_summaries)
    
    # Generate holistic coaching ONLY for reps who need it
    for rep_id, summary in rep_summaries.items():
        if summary["needs_coaching"]:
            rep_notes = [n for n in processed_notes if n.get("rep_id") == rep_id]
            summary["coaching_plan"] = await generate_rep_coaching(summary, rep_notes)
    
    return {
        "processed_notes": processed_notes,
        "trends": trends,
        "rep_summaries": rep_summaries,
        "hcp_journeys": hcp_journeys,
        "market_signals": market_signals
    }