"""Step 1: clean and merge the two Kaggle datasets into one team table and one match table.

Run from anywhere:  python3 -I analysis/01_clean_merge.py
Inputs  (data/raw):  mann14/teams.csv, mann14/matches.csv, khayalmammadov/World Cup 2026.csv
Outputs (data/clean): teams_merged.csv, matches_enriched.csv, cleaning_log.txt
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(sys.argv[0]).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "clean"
OUT.mkdir(parents=True, exist_ok=True)
log = []

teams = pd.read_csv(RAW / "mann14" / "teams.csv")
matches = pd.read_csv(RAW / "mann14" / "matches.csv")
pre = pd.read_csv(RAW / "khayalmammadov" / "World Cup 2026.csv", encoding="utf-8-sig")

# 1. Harmonise team names (the pre-tournament file abbreviates one name)
pre["Team"] = pre["Team"].replace({"Bosnia & Herz.": "Bosnia and Herzegovina"})
missing = set(teams.team) ^ set(pre.Team)
log.append(f"Name mismatches after harmonising: {sorted(missing) or 'none'}")

# 2. Stage reached, derived from the match file (the source of truth for results)
ORDER = {"Group Stage": 1, "Round of 32": 2, "Round of 16": 3, "Quarterfinal": 4,
         "Semifinal": 5, "Final": 6}
LABEL = {1: "Group stage", 2: "Round of 32", 3: "Round of 16", 4: "Quarter-final",
         5: "Semi-final", 6: "Final", 7: "Champion"}
reached = {}
for _, m in matches.iterrows():
    stage = "Semifinal" if m.stage == "Third Place Match" else m.stage
    for t in (m.team_1, m.team_2):
        reached[t] = max(reached.get(t, 0), ORDER[stage])
final = matches[matches.stage == "Final"].iloc[0]
reached[final.winner] = 7
teams["stage_n"] = teams.team.map(reached)
teams["stage"] = teams.stage_n.map(LABEL)

# Compare with the file's own eliminated_round column
FILE_N = {"Group Stage": 1, "Round of 32": 2, "Round of 16": 3, "Quarterfinal": 4,
          "Semifinal": 5, "Third Place Match": 5, "Final (Runner-up)": 6, "Champion": 7}
teams["file_stage_n"] = teams.eliminated_round.map(FILE_N)
bad = teams[teams.file_stage_n != teams.stage_n]
for _, r in bad.iterrows():
    log.append(f"Corrected {r.team}: teams.csv says '{r.eliminated_round}', "
               f"matches.csv shows it reached '{r.stage}'")

# 3. Merge pre-tournament attributes
keep = {"Team": "team", "FIFA Ranking": "fifa_rank", "Squad Market Value (€m)": "value_m",
        "Championship Prob. (%)": "title_prob", "Group Stage Qual. (%)": "qual_prob",
        "World Cup Appearances": "wc_apps", "World Titles": "titles",
        "Championship Category": "category", "Star Player": "star"}
pre = pre[list(keep)].rename(columns=keep)
df = teams.merge(pre, on="team", how="left", validate="one_to_one")
assert df.value_m.notna().all() and len(df) == 48

# 4. Value rank (1 = most valuable; ties share the best rank)
df["value_rank"] = df.value_m.rank(ascending=False, method="min").astype(int)

# 5. Matches played and won (shoot-out wins count as wins, as the file records them)
mp, w = {}, {}
for _, m in matches.iterrows():
    for t in (m.team_1, m.team_2):
        mp[t] = mp.get(t, 0) + 1
    if m.winner != "Draw":
        w[m.winner] = w.get(m.winner, 0) + 1
df["matches_played"] = df.team.map(mp)
df["wins"] = df.team.map(w).fillna(0).astype(int)

df.drop(columns=["file_stage_n"]).to_csv(OUT / "teams_merged.csv", index=False)

# 6. Enrich matches with squad values
val = df.set_index("team").value_m
mt = matches.copy()
mt["value_1"] = mt.team_1.map(val)
mt["value_2"] = mt.team_2.map(val)
mt["richer"] = mt.apply(lambda r: r.team_1 if r.value_1 > r.value_2 else
                        (r.team_2 if r.value_2 > r.value_1 else "Equal"), axis=1)
mt["value_ratio"] = mt[["value_1", "value_2"]].max(axis=1) / mt[["value_1", "value_2"]].min(axis=1)
mt["result_for_richer"] = mt.apply(
    lambda r: "Equal value" if r.richer == "Equal" else
    ("Draw" if r.winner == "Draw" else ("Win" if r.winner == r.richer else "Loss")), axis=1)
mt["phase"] = mt.stage.where(mt.stage == "Group Stage", "Knockout")
mt.to_csv(OUT / "matches_enriched.csv", index=False)

log.append(f"Teams: {len(df)} · matches: {len(mt)} · knockout matches: {(mt.phase == 'Knockout').sum()}")
log.append(f"Matches between squads of equal value (excluded from 'richer team' counts): "
           f"{(mt.richer == 'Equal').sum()}")
(OUT / "cleaning_log.txt").write_text("\n".join(log) + "\n")
print("\n".join(log))
