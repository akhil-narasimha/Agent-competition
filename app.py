import streamlit as st
import asyncio
from src.main import process_all_notes
import pandas as pd

# ==========================================
# 1. PAGE CONFIG & CUSTOM CSS
# ==========================================
st.set_page_config(page_title="Rep Signal OS", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Clean, modern typography and spacing */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #1e293b; font-weight: 600; }
    
    /* Beautiful Alert Cards */
    .alert-urgent { background: linear-gradient(to right, #fef2f2, #fff); border-left: 6px solid #ef4444; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    .alert-market { background: linear-gradient(to right, #fffbeb, #fff); border-left: 6px solid #f59e0b; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    
    /* Text highlights */
    .highlight-red { color: #b91c1c; background-color: #fee2e2; padding: 2px 6px; border-radius: 4px; font-weight: 500; font-family: monospace; }
    .highlight-blue { color: #1d4ed8; background-color: #dbeafe; padding: 2px 6px; border-radius: 4px; font-weight: 500;}
    </style>
""", unsafe_allow_html=True)

if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

# ==========================================
# 2. SIDEBAR: CONTROLS & VOICE UX
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103360.png", width=50) # Generic AI icon
    st.title("Signal Engine")
    st.caption("Territory: Hyderabad Region")
    st.divider()
    
    st.markdown("### 📂 1. Load Data")
    uploaded_file = st.file_uploader("Upload Veeva CRM Export (CSV)", type="csv")
    
    st.markdown("### 🚀 2. Engine Controls")
    if st.button("Run Territory Analytics", type="primary", use_container_width=True):
        with st.spinner("Processing CRM Notes..."):
            # If user uploaded a file, use it. Otherwise, fallback to the demo dataset.
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_csv(r"C:\Users\venne\Downloads\Agent competition\src\call_notes.csv")
                st.toast("No file uploaded. Using default demo dataset.")
                
            raw_notes = df.to_dict('records')
            results = asyncio.run(process_all_notes(raw_notes))
            
            st.session_state.processed_data = results
            st.session_state.analysis_complete = True
            
    st.divider()
    
    # Moving Voice to Sidebar to keep main view clean
    st.markdown("### 🎤 Live Ingestion (V2)")
    st.caption("Simulate mobile voice-to-CRM")
    audio_value = st.audio_input("Record summary")
    if audio_value:
        with st.status("Transcribing via Gemini...", expanded=True):
            st.write("**Transcript:** Dr. Kapoor liked the onset but complained of dizziness. Meds paused. Too expensive.")
            import time; time.sleep(1.5)
            st.error("🚨 AE Flagged: Route to PV")

# ==========================================
# 3. MAIN DASHBOARD AREA
# ==========================================
if not st.session_state.analysis_complete:
    st.header("👋 Welcome to Rep Signal OS")
    st.info("👈 Click **Run Territory Analytics** in the sidebar to process the latest Veeva CRM data.")
else:
    data = st.session_state.processed_data
    
    # --- KPI ROW (Top Level Overview) ---
    st.header("Territory Health Overview")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    ae_count = len([n for n in data["processed_notes"] if n.get("ae_flag")])
    deteriorating_hcps = len([h for h, j in data["hcp_journeys"].items() if j.get("is_deteriorating")])
    coaching_reps = len([r for r, s in data["rep_summaries"].items() if s["needs_coaching"]])
    
    kpi1.metric("Unread Notes Processed", "524", "100% Coverage")
    kpi2.metric("Critical AE Flags", str(ae_count), "-1 from last week", delta_color="inverse")
    kpi3.metric("Deteriorating HCPs", str(deteriorating_hcps), "High Churn Risk", delta_color="inverse")
    kpi4.metric("Reps Requiring Coaching", str(coaching_reps))
    
    st.divider()

    # --- TABS FOR CLEAN ORGANIZATION ---
    tab1, tab2, tab3, tab4 = st.tabs(["🛡️ Safety & Execution", "📈 Market Intelligence", "⚔️ War Room", "🧪 Rep Sandbox"])
    
    # ---------------------------------------------------------
    # TAB 1: SAFETY & EXECUTION (The Reps)
    # ---------------------------------------------------------
    with tab1:
        st.subheader("Pharmacovigilance (PV) Alerts")
        if ae_count > 0:
            for note in [n for n in data["processed_notes"] if n.get("ae_flag")]:
                st.markdown(f"""
                <div class="alert-urgent">
                    <h4 style="margin-top:0; color:#991b1b;">🚨 Action Required: Note {note['note_id']}</h4>
                    <p><strong>Doctor:</strong> {note['hcp_name']} | <strong>Rep:</strong> {note['rep_name']}</p>
                    <p><strong>Extracted Signal:</strong> <span class="highlight-red">"{note['ae_phrase']}"</span></p>
                    <p style="font-size: 13px; margin-bottom:0; color:#64748b;">↳ Status: Locked and auto-routed to Oracle Argus Safety System.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No Adverse Events detected in this batch.")

        st.subheader("Rep Performance & Coaching")
        rep_cols = st.columns(2)
        
        # Use st.container to make beautiful cards for each rep
        for i, (rep_id, summary) in enumerate(data["rep_summaries"].items()):
            col = rep_cols[i % 2]
            with col.container(border=True):
                st.markdown(f"### {summary['name']}")
                st.caption(f"Tenure: {summary['tenure_months']} months | Territory: {summary['territory']}")
                
                # Visual Score Indicator
                score = summary['avg_adherence']
                if score >= 80: st.metric("Message Adherence", f"{score}/100", "Top Quartile")
                else: st.metric("Message Adherence", f"{score}/100", "Requires Intervention", delta_color="inverse")
                
                if summary.get("coaching_plan"):
                    with st.expander("🤖 View AI Coaching Brief"):
                        st.write(summary['coaching_plan'])
                    with st.popover("✉️ Auto-Draft HCP Email"):
                        st.info(f"**Subject:** Following up on LOKELMA\n\nDear Doctor,\n\nFollowing up on our conversation. I've attached the latest Copay Program details to ensure affordability is not a barrier.\n\nBest,\n{summary['name']}")

    # ---------------------------------------------------------
    # TAB 2: MARKET INTELLIGENCE (The System)
    # ---------------------------------------------------------
    # --- TAB 2: MARKET INTELLIGENCE ---
    with tab2:
        st.subheader("Systemic Market Shifts")
        st.caption("AI separates isolated rep errors from territory-wide market threats.")
        
        for signal in data["market_signals"]:
            if signal["classification"] == "MARKET_SIGNAL":
                # Beautiful metric-style card for Market Signals
                with st.container(border=True):
                    cols = st.columns([1, 3])
                    cols[0].metric(label=signal['objection'].replace("_", " ").title(), 
                                   value=f"{signal['week2_rate']}%", 
                                   delta=f"+{signal['delta']}pp Spike", delta_color="inverse")
                    cols[1].markdown(f"**🤖 AI Diagnosis:** This is appearing across multiple reps, indicating a systemic issue rather than poor execution.")
                    cols[1].info(f"**Recommended Action:** {signal['action']}")

        st.markdown("---")
        st.subheader("HCP Churn Risk Trajectory")
        st.caption("Tracking historical sentiment across multiple rep visits.")
        
        # Helper function to colorize the text
        def colorize_sentiment(sentiment):
            color_map = {
                "engaged": "🟢 **Engaged**",
                "neutral": "🟡 **Neutral**",
                "resistant": "🟠 **Resistant**",
                "at_risk_switching": "🔴 **At Risk (Switching)**"
            }
            return color_map.get(sentiment, sentiment)

        hcp_cols = st.columns(2)
        idx = 0
        for hcp_id, journey in data["hcp_journeys"].items():
            if journey.get("is_deteriorating"):
                col = hcp_cols[idx % 2]
                with col.container(border=True):
                    st.markdown(f"#### {journey['name']} 🩺")
                    st.caption(f"Specialty: {journey.get('specialty', 'Unknown')}")
                    
                    # Apply the color mapping to the trajectory list
                    colored_traj = " ➔ ".join([colorize_sentiment(s) for s in journey['sentiment_trajectory']])
                    st.markdown(f"**Trajectory:** {colored_traj}")
                    
                    st.error("🚨 **Recommendation:** Deploy Medical Science Liaison (MSL) immediately to rescue account.")
                idx += 1
    # ---------------------------------------------------------
    # TAB 3: COMPETITOR WAR ROOM (The Rival)
    # ---------------------------------------------------------
    with tab3:
        st.subheader("Live Field Intel: Veltassa")
        comp_notes = [n for n in data["processed_notes"] if any(o["type"] == "competitor_preference" for o in n.get("objections", []))]
        
        for n in comp_notes:
            for obj in n.get("objections", []):
                if obj["type"] == "competitor_preference":
                    with st.container(border=True):
                        st.markdown(f"🗣️ **{n['hcp_name']}** told {n['rep_name']}:")
                        st.markdown(f"> *\"{obj['phrase']}\"*")

    with tab4:
        st.subheader("Ad-Hoc Note Analysis")
        st.caption("Paste a note here before logging it into Veeva to get instant AI feedback on strategy and compliance.")
        
        single_note_text = st.text_area("Enter Call Note Text:", height=150, placeholder="Doctor liked the efficacy but mentioned the patient is struggling with the copay...")
        
        if st.button("Analyze Single Note"):
            if single_note_text:
                with st.spinner("Analyzing..."):
                    from src.graph.workflow import app as graph_app
                    
                    # Create a mock state for this single note
                    mock_state = {
                        "note_id": "TEST-001", "rep_id": "R00", "rep_name": "Test Rep",
                        "hcp_id": "H00", "hcp_name": "Test Doctor", "note_text": single_note_text
                    }
                    
                    # Run it directly through the graph
                    single_result = asyncio.run(graph_app.ainvoke(mock_state))
                    
                    # Display results beautifully
                    col1, col2 = st.columns(2)
                    with col1.container(border=True):
                        st.markdown("### Compliance Check")
                        if single_result.get("ae_flag"):
                            st.error(f"🚨 **AE Detected:** {single_result.get('ae_phrase')}")
                        else:
                            st.success("✅ No Adverse Events detected.")
                            
                    with col2.container(border=True):
                        st.markdown("### Strategy Check")
                        st.metric("Adherence Score", f"{single_result.get('adherence_score', 0)}/100")
                        objections = [o["type"].replace("_", " ").title() for o in single_result.get("objections", [])]
                        if objections:
                            st.warning(f"**Objections Logged:** {', '.join(objections)}")
                        else:
                            st.info("No objections detected.")