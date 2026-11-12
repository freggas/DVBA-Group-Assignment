"""Build dashboard/data.js from the cleaned data (run after 01-03).

python3 -I analysis/04_dashboard_data.py
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data" / "clean"
OUT = ROOT / "dashboard" / "data.js"

t = pd.read_csv(CLEAN / "team_expectations.csv")
m = pd.read_csv(CLEAN / "matches_enriched.csv")
value = dict(zip(t.team, t.value_m))

teams = []
for r in t.sort_values("value_m", ascending=False).itertuples():
    teams.append({
        "team": r.team, "group": r.group, "conf": r.confederation,
        "host": r.host_nation == "Yes", "value": int(r.value_m),
        "rank": int(r.ladder_rank), "fifa": int(r.fifa_rank),
        "odds": float(r.title_prob), "stage": int(r.stage_n),
        "ladder": int(r.ladder_stage_n), "delta": int(r.rounds_vs_ladder),
        "star": r.star, "wins": int(r.wins), "played": int(r.matches_played),
    })

matches = []
for r in m.itertuples():
    matches.append({
        "id": int(r.match_id), "date": r.date, "stage": r.stage,
        "a": r.team_1, "b": r.team_2, "sa": int(r.score_1), "sb": int(r.score_2),
        "winner": r.winner if isinstance(r.winner, str) else None,
        "pens": r.decided_by_penalties == "Yes",
        "va": int(value[r.team_1]), "vb": int(value[r.team_2]),
    })

# Checks against story_numbers.txt
ko = m[m.phase == "Knockout"]
play, pens = ko[ko.decided_by_penalties == "No"], ko[ko.decided_by_penalties == "Yes"]
assert (len(play), (play.result_for_richer == "Win").sum()) == (28, 24)
assert (len(pens), (pens.result_for_richer == "Win").sum()) == (4, 1)
assert len(teams) == 48 and len(matches) == 104

prize = [  # FIFA Council (Dec 2025, Apr 2026), US$ m per team
    ["Group stage", 10], ["Round of 32", 12], ["Round of 16", 16], ["Quarter-final", 20],
    ["Fourth place", 28], ["Third place", 30], ["Runner-up", 34], ["Champion", 51],
]
corr = [["Bookmaker odds", 0.74], ["Squad value", 0.72], ["FIFA ranking", 0.64]]

OUT.parent.mkdir(exist_ok=True)
payload = {"teams": teams, "matches": matches, "prize": prize, "corr": corr}
OUT.write_text("window.WC = " + json.dumps(payload, ensure_ascii=False) + ";\n", encoding="utf-8")
print(f"wrote {OUT.relative_to(ROOT)}: {len(teams)} teams, {len(matches)} matches")
