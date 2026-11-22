"""Step 2: how far does squad market value explain how far a team went?

Run: python3 -I analysis/02_analysis.py   (after 01_clean_merge.py)
Writes data/clean/analysis_results.txt and data/clean/team_expectations.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(sys.argv[0]).resolve().parent.parent
C = ROOT / "data" / "clean"
t = pd.read_csv(C / "teams_merged.csv")
m = pd.read_csv(C / "matches_enriched.csv")
out = []
def say(*a):
    out.append(" ".join(str(x) for x in a))

# A. Rank correlations with stage reached (Spearman, robust to the ordinal stage scale)
say("A. Spearman correlation with stage reached (1 = group … 7 = champion)")
for col, sign, name in [("value_m", 1, "Squad market value"),
                        ("fifa_rank", -1, "FIFA ranking (better = higher)"),
                        ("title_prob", 1, "Bookmaker title probability")]:
    rho, p = stats.spearmanr(sign * t[col], t.stage_n)
    say(f"   {name:34s} rho = {rho:.2f}  (p = {p:.1g}, n = 48)  rho² ≈ {rho**2:.2f}")

# B. "If money decided": of the N richest squads, how many reached the stage with N teams?
say("\nB. Of the N most valuable squads, how many reached the round with N teams left?")
STAGES = [(32, 2, "Round of 32"), (16, 3, "Round of 16"), (8, 4, "Quarter-final"),
          (4, 5, "Semi-final"), (2, 6, "Final"), (1, 7, "Champion")]
top = t.sort_values(["value_m", "fifa_rank"], ascending=[False, True]).reset_index(drop=True)
hit_rows = []
for n, s, label in STAGES:
    hits = (top.head(n).stage_n >= s).sum()
    who_in = top.head(n)[top.head(n).stage_n >= s].team.tolist()
    who_out = top.head(n)[top.head(n).stage_n < s].team.tolist()
    crashers = t[(t.stage_n >= s) & (~t.team.isin(top.head(n).team))].team.tolist()
    say(f"   {label:13s}: {hits}/{n} of the top {n} by value made it "
        f"| missed: {who_out} | outsiders who got in: {crashers}")
    hit_rows.append((label, n, hits))

# C. Match level: did the richer squad win?
say("\nC. Result for the richer squad (shoot-out winners count as winners)")
for phase in ["Group Stage", "Knockout"]:
    sub = m[m.phase == phase]
    vc = sub.result_for_richer.value_counts()
    w, d, l = vc.get("Win", 0), vc.get("Draw", 0), vc.get("Loss", 0)
    say(f"   {phase:12s}: {len(sub)} matches · richer W {w} / D {d} / L {l} "
        f"· win rate {w/len(sub):.0%} · lost {l/len(sub):.0%}")
ko = m[m.phase == "Knockout"]
pens = ko[ko.decided_by_penalties == "Yes"]
say(f"   Knockout ties decided in regular/extra time: {len(ko)-len(pens)}, richer won "
    f"{(ko[ko.decided_by_penalties=='No'].result_for_richer=='Win').sum()}")
say(f"   Shoot-outs: {len(pens)}, richer won {(pens.result_for_richer=='Win').sum()} "
    f"→ {pens[['team_1','team_2','winner','value_1','value_2']].values.tolist()}")
for lo, hi, lab in [(1, 1.5, "<1.5x"), (1.5, 3, "1.5–3x"), (3, 1e9, ">3x")]:
    sub = m[(m.value_ratio >= lo) & (m.value_ratio < hi)]
    w = (sub.result_for_richer == "Win").sum(); l = (sub.result_for_richer == "Loss").sum()
    d = (sub.result_for_richer == "Draw").sum()
    say(f"   Value gap {lab:7s}: {len(sub):3d} matches · richer W {w} D {d} L {l} "
        f"· win {w/len(sub):.0%} · not-lost {(w+d)/len(sub):.0%}")
upsets = ko[ko.result_for_richer == "Loss"]
say("   Knockout upsets (poorer squad won):")
for _, r in upsets.iterrows():
    poorer = r.team_1 if r.value_1 < r.value_2 else r.team_2
    say(f"     {r.stage}: {poorer} (€{min(r.value_1,r.value_2):.0f}m) beat {r.richer} "
        f"(€{max(r.value_1,r.value_2):.0f}m) · {r.score_1}-{r.score_2}"
        f"{' pens' if r.decided_by_penalties=='Yes' else ''}")

# D. Value-based expectation: fit stage ~ log(value), compare with actual
X = np.log(t.value_m)
slope, intercept, r, p, se = stats.linregress(X, t.stage_n)
t["expected_stage"] = intercept + slope * X
t["rounds_vs_expected"] = t.stage_n - t.expected_stage
say(f"\nD. Linear fit stage = {intercept:.2f} + {slope:.2f}·ln(value €m): R² = {r**2:.2f}")
say(f"   Doubling squad value adds {slope*np.log(2):.2f} rounds on average")
cols = ["team", "confederation", "value_m", "stage", "expected_stage", "rounds_vs_expected"]
say("   Biggest over-performers:")
for _, r_ in t.sort_values("rounds_vs_expected", ascending=False).head(8)[cols].iterrows():
    say(f"     {r_.team:22s} €{r_.value_m:5.0f}m  {r_.stage:13s} expected {r_.expected_stage:.1f}  +{r_.rounds_vs_expected:.1f}")
say("   Biggest under-performers:")
for _, r_ in t.sort_values("rounds_vs_expected").head(8)[cols].iterrows():
    say(f"     {r_.team:22s} €{r_.value_m:5.0f}m  {r_.stage:13s} expected {r_.expected_stage:.1f}  {r_.rounds_vs_expected:.1f}")

# E. Value tiers
t["tier"] = pd.cut(t.value_m, [0, 200, 500, 900, 2000],
                   labels=["<€200m", "€200–500m", "€500–900m", ">€900m"])
say("\nE. Value tiers: share reaching each round")
g = t.groupby("tier", observed=True)
tier = pd.DataFrame({
    "teams": g.size(),
    "out_of_group": g.apply(lambda x: (x.stage_n >= 2).mean()),
    "r16": g.apply(lambda x: (x.stage_n >= 3).mean()),
    "qf": g.apply(lambda x: (x.stage_n >= 4).mean()),
    "sf": g.apply(lambda x: (x.stage_n >= 5).mean()),
    "avg_matches": g.matches_played.mean()})
say(tier.round(2).to_string())

# F. Confederations ("federations" in the brief): actual vs value-expected
say("\nF. Confederations: rounds above/below value expectation (mean per team)")
conf = t.groupby("confederation").agg(
    teams=("team", "size"), avg_value=("value_m", "mean"),
    out_of_group=("stage_n", lambda s: (s >= 2).sum()),
    r16_plus=("stage_n", lambda s: (s >= 3).sum()),
    avg_vs_expected=("rounds_vs_expected", "mean"),
    matches=("matches_played", "sum")).sort_values("avg_vs_expected", ascending=False)
say(conf.round(2).to_string())

# G. Under the "pick the richest" rule, how many group-stage survivors are called right?
exp_r32 = set(top.head(32).team)
act_r32 = set(t[t.stage_n >= 2].team)
say(f"\nG. Value ranking picks {len(exp_r32 & act_r32)}/32 of the round-of-32 teams")

# H. Finalists and semi-finalists against value rank
say("\nH. Final four:", t[t.stage_n >= 5][["team", "value_m", "value_rank"]].values.tolist())
say("   Quarter-finalists:", t[t.stage_n >= 4][["team", "value_m", "value_rank"]].values.tolist())

t.to_csv(C / "team_expectations.csv", index=False)
(C / "analysis_results.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
