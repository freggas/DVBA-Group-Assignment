"""Step 3: every number used on the slides and in the brief, with how it is calculated.

Run: python3 -I analysis/03_story_numbers.py   (after 01 and 02)
Writes data/clean/story_numbers.txt and data/clean/chart_data.json
"""
import json
import sys
from pathlib import Path

import pandas as pd
from scipy import stats

ROOT = Path(sys.argv[0]).resolve().parent.parent
C = ROOT / "data" / "clean"
t = pd.read_csv(C / "team_expectations.csv")
m = pd.read_csv(C / "matches_enriched.csv")
out = []
def say(*a):
    out.append(" ".join(str(x) for x in a))

LABEL = {1: "Group stage", 2: "Round of 32", 3: "Round of 16", 4: "Quarter-final",
         5: "Semi-final", 6: "Final", 7: "Champion"}

# --- Field overview
say(f"Total squad value: €{t.value_m.sum():,.0f}m · median €{t.value_m.median():.0f}m · "
    f"max {t.loc[t.value_m.idxmax(),'team']} €{t.value_m.max():.0f}m · min "
    f"{t.loc[t.value_m.idxmin(),'team']} €{t.value_m.min():.0f}m · ratio {t.value_m.max()/t.value_m.min():.0f}x")
say(f"Squads €200–900m: {((t.value_m>=200)&(t.value_m<900)).sum()} of 48")

# --- The 'money ladder': expected stage if the richer squad always went through.
# Rank by value; ties broken by FIFA ranking. Rank 1 = champion, 2 = final, 3–4 = SF,
# 5–8 = QF, 9–16 = R16, 17–32 = R32, 33–48 = group stage.
lad = t.sort_values(["value_m", "fifa_rank"], ascending=[False, True]).reset_index(drop=True)
lad["ladder_rank"] = lad.index + 1
def ladder(r):
    return 7 if r == 1 else 6 if r == 2 else 5 if r <= 4 else 4 if r <= 8 else 3 if r <= 16 else 2 if r <= 32 else 1
lad["ladder_stage_n"] = lad.ladder_rank.map(ladder)
lad["ladder_stage"] = lad.ladder_stage_n.map(LABEL)
lad["rounds_vs_ladder"] = lad.stage_n - lad.ladder_stage_n
lad.to_csv(C / "team_expectations.csv", index=False)
say("\nMoney ladder: over-performers (rounds above the ladder)")
for _, r in lad[lad.rounds_vs_ladder > 0].sort_values(["rounds_vs_ladder", "value_m"], ascending=[False, True]).iterrows():
    say(f"   +{r.rounds_vs_ladder} {r.team:22s} €{r.value_m:.0f}m (#{r.ladder_rank}) ladder {r.ladder_stage:13s} → {r.stage}")
say("Money ladder: under-performers")
for _, r in lad[lad.rounds_vs_ladder < 0].sort_values("rounds_vs_ladder").iterrows():
    say(f"   {r.rounds_vs_ladder} {r.team:22s} €{r.value_m:.0f}m (#{r.ladder_rank}) ladder {r.ladder_stage:13s} → {r.stage}")
say(f"Exactly on the ladder: {(lad.rounds_vs_ladder==0).sum()} of 48")

# --- Tiers
bins = [0, 200, 500, 900, 2000]
labels = ["Under €200m", "€200–500m", "€500–900m", "Over €900m"]
t2 = lad.copy()
t2["tier"] = pd.cut(t2.value_m, bins, labels=labels, right=False)
say("\nTiers (count reaching at least each round)")
tiers = []
for lab in labels:
    g = t2[t2.tier == lab]
    row = {"tier": lab, "teams": len(g)}
    for s, k in [(2, "r32"), (3, "r16"), (4, "qf"), (5, "sf")]:
        row[k] = int((g.stage_n >= s).sum())
    row["avg_matches"] = round(g.matches_played.mean(), 1)
    tiers.append(row)
    say("  ", row)

# --- Median value by stage reached
say("\nMedian squad value by stage reached")
grp = t2.assign(s=t2.stage_n.clip(upper=5)).groupby("s").value_m
for s, v in grp.median().items():
    say(f"   {('Semi-final or better' if s==5 else LABEL[s]):22s} n={grp.size()[s]:2d}  median €{v:.0f}m")

# --- Matches
g = m[m.phase == "Group Stage"]; ko = m[m.phase == "Knockout"]
inplay = ko[ko.decided_by_penalties == "No"]; pens = ko[ko.decided_by_penalties == "Yes"]
say(f"\nGroup stage: richer squad W {(g.result_for_richer=='Win').sum()} D {(g.result_for_richer=='Draw').sum()} "
    f"L {(g.result_for_richer=='Loss').sum()} of {len(g)}")
say(f"Knockouts settled in 90/120 min: richer won {(inplay.result_for_richer=='Win').sum()} of {len(inplay)} "
    f"({(inplay.result_for_richer=='Win').mean():.0%})")
say(f"Knockouts settled on penalties: richer won {(pens.result_for_richer=='Win').sum()} of {len(pens)}")
# Upsets by a squad outside the >€900m tier against a richer squad
up = ko[(ko.result_for_richer == "Loss")].copy()
up["winner_value"] = up.apply(lambda r: r.value_1 if r.winner == r.team_1 else r.value_2, axis=1)
up["loser"] = up.apply(lambda r: r.team_2 if r.winner == r.team_1 else r.team_1, axis=1)
up["loser_value"] = up.apply(lambda r: r.value_2 if r.winner == r.team_1 else r.value_1, axis=1)
und = up[up.winner_value < 900]
say(f"Knockout wins by a sub-€900m squad over a richer squad: {len(und)}; on penalties: "
    f"{(und.decided_by_penalties=='Yes').sum()}")
for _, r in und.iterrows():
    say(f"   {r.stage}: {r.winner} €{r.winner_value:.0f}m beat {r.loser} €{r.loser_value:.0f}m "
        f"{r.score_1}-{r.score_2}{' (pens)' if r.decided_by_penalties=='Yes' else ''}")

# --- Hosts and confederations
say("\nHosts:")
for _, r in lad[lad.host_nation == "Yes"].iterrows():
    say(f"   {r.team} €{r.value_m:.0f}m ladder {r.ladder_stage} → {r.stage}")
say("\nConfederations vs ladder (teams out of group: actual vs ladder)")
for c, gg in lad.groupby("confederation"):
    say(f"   {c:9s} teams {len(gg):2d} · out of group actual {(gg.stage_n>=2).sum():2d} vs ladder "
        f"{(gg.ladder_stage_n>=2).sum():2d} · R16+ actual {(gg.stage_n>=3).sum()} vs ladder {(gg.ladder_stage_n>=3).sum()} "
        f"· net rounds {gg.rounds_vs_ladder.sum():+d}")

# --- Predictive power: value vs FIFA ranking vs bookmakers (Spearman)
say("\nRank correlation with stage reached")
for col, sign in [("value_m", 1), ("fifa_rank", -1), ("title_prob", 1)]:
    rho = stats.spearmanr(sign * lad[col], lad.stage_n)[0]
    say(f"   {col:10s} rho {rho:.2f}  rho² {rho**2:.2f}")

# --- Prize money ladder (FIFA Council, 17 Dec 2025), USD m by finishing stage
PRIZE = {1: 9, 2: 11, 3: 15, 4: 19, 5: 27, 6: 33, 7: 50}   # semi-final loser = 4th place (27) or 3rd (29)
say("\nPrize money step-ups (USD m): group→R32 +2, R32→R16 +4, R16→QF +4, QF→SF +8 (4th) / +10 (3rd)")

# --- Chart data for the slides
chart = {
    "dots": lad[["team", "value_m", "stage_n", "confederation"]].to_dict("records"),
    "tiers": tiers,
    "upsets": und[["stage", "winner", "winner_value", "loser", "loser_value", "decided_by_penalties"]].to_dict("records"),
    "ladder": lad[["team", "value_m", "ladder_rank", "ladder_stage_n", "stage_n", "rounds_vs_ladder"]].to_dict("records"),
}
(C / "chart_data.json").write_text(json.dumps(chart, indent=1))
(C / "story_numbers.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
