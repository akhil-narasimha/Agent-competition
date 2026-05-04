"""
validate_dataset.py
Run this to confirm the dataset is correct and all expected signals are present.
Usage: python validate_dataset.py
"""

import pandas as pd
import sys
sys.path.append("..")
from config import WEEK1_BASELINE, WEEK2_EXPECTED, KNOWN_AE_NOTES, AE_SIGNAL_PATTERNS

df = pd.read_csv("C:\\Users\\venne\\Downloads\\Agent competition\\src\\call_notes.csv")

print("=" * 60)
print("DATASET VALIDATION REPORT")
print("=" * 60)

# ── Basic Shape ──────────────────────────────────────────────
print(f"\n📋 Total notes loaded : {len(df)}")
print(f"   Week 1 notes        : {len(df[df.week_label == 'Week 1'])}")
print(f"   Week 2 notes        : {len(df[df.week_label == 'Week 2'])}")
print(f"   Reps                : {df.rep_name.nunique()} ({', '.join(df.rep_name.unique())})")
print(f"   Unique HCPs         : {df.hcp_name.nunique()}")
print(f"   Date range          : {df.call_date.min()} → {df.call_date.max()}")

# ── AE Signal Check ──────────────────────────────────────────
print(f"\n🚨 AE SIGNAL CHECK")
ae_notes = []
for _, row in df.iterrows():
    note = row["note_text"].lower()
    has_symptom  = any(k in note for k in AE_SIGNAL_PATTERNS["symptom_keywords"])
    has_temporal = any(k in note for k in AE_SIGNAL_PATTERNS["temporal_keywords"])
    if has_symptom and has_temporal:
        ae_notes.append(row["note_id"])
        print(f"   ⚠️  {row['note_id']} | {row['rep_name']} | {row['hcp_name']} | {row['call_date']}")

if set(ae_notes) == set(KNOWN_AE_NOTES):
    print(f"   ✅ AE notes match expected: {KNOWN_AE_NOTES}")
else:
    print(f"   ❌ Mismatch. Found: {ae_notes}, Expected: {KNOWN_AE_NOTES}")

# ── Affordability Trend ──────────────────────────────────────
print(f"\n📈 AFFORDABILITY OBJECTION TREND")
for week in ["Week 1", "Week 2"]:
    week_df = df[df.week_label == week]
    count = week_df["note_text"].str.lower().str.contains("afford|cost|copay|expensive|price|cheaper").sum()
    rate = round(count / len(week_df) * 100, 1)
    print(f"   {week}: {count}/{len(week_df)} notes = {rate}%")

w1_rate = WEEK1_BASELINE["objection_rates"]["affordability"]["rate"]
w2_rate = WEEK2_EXPECTED["objection_rates"]["affordability"]["rate"]
delta   = round(w2_rate - w1_rate, 1)
print(f"   📊 Week-over-week delta: +{delta}pp  ({'✅ Matches config' if abs(delta - 36) < 5 else '⚠️ Check config'})")

# ── Rep Distribution ─────────────────────────────────────────
print(f"\n👤 CALLS PER REP PER WEEK")
pivot = df.groupby(["week_label", "rep_name"]).size().unstack(fill_value=0)
print(pivot.to_string())

# ── Competitor Mentions ───────────────────────────────────────
print(f"\n🔄 COMPETITOR (VELTASSA) MENTIONS BY REP")
for rep in df.rep_name.unique():
    rep_df = df[df.rep_name == rep]
    count = rep_df["note_text"].str.lower().str.contains("veltassa").sum()
    print(f"   {rep}: {count} notes mention Veltassa")

# ── Notes Preview ─────────────────────────────────────────────
print(f"\n📝 SAMPLE NOTE PREVIEW (N014 — Expected AE Signal)")
row = df[df.note_id == "N014"].iloc[0]
print(f"   Rep   : {row['rep_name']}")
print(f"   HCP   : {row['hcp_name']}")
print(f"   Date  : {row['call_date']}")
print(f"   Text  : {row['note_text'][:200]}...")

print("\n" + "=" * 60)
print("✅ Validation complete. Dataset ready for agent pipeline.")
print("=" * 60)
