from typing import TypedDict, List, Dict, Any, Optional

class NoteState(TypedDict):
    """
    The strict state dictionary that flows through the LangGraph for a single Veeva call note.
    """
    # --- Inputs (from CSV) ---
    note_id: str
    rep_id: str
    rep_name: str
    hcp_id: str
    hcp_name: str
    week_label: str
    note_text: str
    
    # --- Agent Outputs ---
    
    # 1. AE Detector Output
    ae_flag: bool
    ae_phrase: Optional[str]
    ae_severity: Optional[str] # "high", "medium", "low", None
    
    # 2. Adherence Scorer Output
    adherence_score: int # 0-100
    messages_delivered: List[str] # List of core message IDs hit
    
    # 3. Objection Extractor Output
    objections: List[Dict[str, str]] # e.g., [{"type": "affordability", "phrase": "too expensive"}]
    
    # 4. Sentiment Classifier Output
    sentiment_label: str # "engaged", "neutral", "resistant", "at_risk_switching"
    sentiment_evidence: str
    
    requires_pv_review: Optional[bool] # Added missing key
    requires_coaching: Optional[bool]  # Made Optional
    coaching_plan: Optional[str]