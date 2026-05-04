import asyncio
from langgraph.graph import StateGraph, END
from src.graph.state import NoteState
from src.utils.llm_client import call_agent_json

# Import our prompts (assuming they are saved as variables in their respective files)
from src.agents.ae_detector import AE_DETECTOR_PROMPT
from src.agents.adherence_scorer import ADHERENCE_SCORER_PROMPT
from src.agents.object_extractor import OBJECTION_EXTRACTOR_PROMPT
from src.agents.sentiment_classifier import SENTIMENT_CLASSIFIER_PROMPT

# ==========================================
# NODE DEFINITIONS (The "Doers")
# ==========================================

async def parallel_agent_node(state: NoteState) -> NoteState:
    """
    Fires off all 4 prompts to Gemini simultaneously for lightning-fast processing.
    """
    note_text = state["note_text"]
    
    # asyncio.gather runs all these API calls at the exact same time
    ae_result, adherence_result, objection_result, sentiment_result = await asyncio.gather(
        call_agent_json(AE_DETECTOR_PROMPT, note_text),
        call_agent_json(ADHERENCE_SCORER_PROMPT, note_text),
        call_agent_json(OBJECTION_EXTRACTOR_PROMPT, note_text),
        call_agent_json(SENTIMENT_CLASSIFIER_PROMPT, note_text)
    )
    
    # Update the state with the JSON results returned by Gemini
    return {
        "ae_flag": ae_result.get("ae_flag", False),
        "ae_phrase": ae_result.get("ae_phrase"),
        "ae_severity": ae_result.get("ae_severity"),
        
        "adherence_score": adherence_result.get("adherence_score", 0),
        "messages_delivered": adherence_result.get("messages_delivered", []),
        
        "objections": objection_result.get("objections", []),
        
        "sentiment_label": sentiment_result.get("sentiment_label", "neutral"),
        "sentiment_evidence": sentiment_result.get("sentiment_evidence", "")
    }

def pv_queue_node(state: NoteState) -> NoteState:
    """
    This node simply tags the state as requiring urgent safety review.
    In a real app, this might trigger an email API to the compliance team.
    """
    return {"requires_pv_review": True}

async def coaching_agent_node(state: NoteState) -> NoteState:
    missed = [m for m in ["CM1","CM2","CM3","CM4"] if m not in state.get("messages_delivered", [])]
    objections = [o["type"] for o in state.get("objections", [])]
        
    coaching_prompt = f"""
    You are a pharma sales coach. The rep scored {state.get('adherence_score', 0)}/100.
    Missed messages: {missed}
    HCP objections raised: {objections}
    
    Return JSON with one key: "tip" — a 3-sentence specific coaching recommendation telling the rep exactly what to say next visit to address the gaps above.
    """
    coaching_result = await call_agent_json(coaching_prompt, state["note_text"])
    return {"requires_coaching": True, "coaching_plan": coaching_result.get("tip", "")}

# ==========================================
# ROUTING LOGIC (The "Traffic Cops")
# ==========================================

def route_after_analysis(state: NoteState):
    if state.get("ae_flag") is True:
        return "pv_queue"
    if state.get("adherence_score", 100) < 60:
        return "coaching_agent"
    return END

def route_after_pv(state: NoteState):
    # Check if the AE note ALSO needs coaching
    if state.get("adherence_score", 100) < 60:
        return "coaching_agent"
    return END

workflow = StateGraph(NoteState)
workflow.add_node("parallel_agents", parallel_agent_node)
workflow.add_node("pv_queue", pv_queue_node)
workflow.add_node("coaching_agent", coaching_agent_node)

workflow.set_entry_point("parallel_agents")

# Route 1: From parallel analysis
workflow.add_conditional_edges("parallel_agents", route_after_analysis, {
    "pv_queue": "pv_queue",
    "coaching_agent": "coaching_agent",
    END: END
})

# Route 2: From PV queue (The Fix for Bug 5)
workflow.add_conditional_edges("pv_queue", route_after_pv, {
    "coaching_agent": "coaching_agent",
    END: END
})

workflow.add_edge("coaching_agent", END)
app = workflow.compile()