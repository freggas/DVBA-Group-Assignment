"""Compute every number shown in the dashboard and brief, and export it.

Run:  .venv/bin/python src/analysis.py      (after src/build_dataset.py)
Outputs:
  dashboard/data.js                    window.DATA = {...}, read by dashboard/index.html
  data/processed/team_metrics.csv      team table incl. expected stage and over/under-performance
  data/processed/match_metrics.csv     match table incl. value gap and whether the richer side won
  docs/results.md                      every headline number with its denominator (for the brief / Q&A)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
STAGES = ["Group Stage", "Round of 32", "Round of 16", "Quarterfinal", "Semifinal", "Final", "Champion"]
KO_ROUNDS = ["Round of 32", "Round of 16", "Quarterfinal", "Semifinal", "Final"]
# If squad value alone decided the tournament, the k-th most valuable squad would reach the
# stage that the k-th best finisher reaches: #1 wins, #2 loses the final, #3-4 semi-finals,
# #5-8 quarter-finals, #9-16 round of 16, #17-32 round of 32, #33-48 group stage.
EXPECTED_BY_RANK = np.array([7, 6, 5, 5] + [4] * 4 + [3] * 8 + [2] * 16 + [1] * 16)
BANDS = [0, 100, 250, 500, 1000, 2000]
BAND_LABELS = ["<€100m", "€100–250m", "€250–500m", "€500m–1bn", ">€1bn"]
GAP_EDGES = [1, 1.5, 2, 4, np.inf]
GAP_LABELS = ["under 1.5×", "1.5–2×", "2–4×", "over 4×"]
SEED = 42


def team_metrics(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["expected_stage"] = EXPECTED_BY_RANK[d.value_rank - 1]
    d["stage_vs_expected"] = d.stage_reached - d.expected_stage
    d["value_band"] = pd.cut(d.market_value_m, BANDS, labels=BAND_LABELS, right=True).astype(str)
    return d


def match_metrics(m: pd.DataFrame, d: pd.DataFrame) -> pd.DataFrame:
    v = d.set_index("team").market_value_m
    m = m.copy()
    m["value_1"], m["value_2"] = m.team_1.map(v), m.team_2.map(v)
    m["richer"] = np.where(m.value_1 >= m.value_2, m.team_1, m.team_2)
    m["poorer"] = np.where(m.value_1 >= m.value_2, m.team_2, m.team_1)
    m["value_gap"] = m[["value_1", "value_2"]].max(axis=1) / m[["value_1", "value_2"]].min(axis=1)
    m["gap_band"] = pd.cut(m.value_gap, GAP_EDGES, labels=GAP_LABELS, include_lowest=True).astype(str)
    richer_goals = np.where(m.value_1 >= m.value_2, m.score_1, m.score_2)
    poorer_goals = np.where(m.value_1 >= m.value_2, m.score_2, m.score_1)
    # Result after 90 (or 120) minutes; shoot-outs count as draws here.
    m["result"] = np.select([richer_goals > poorer_goals, richer_goals < poorer_goals], ["richer won", "poorer won"], "draw")
    # Knockout matches: who went through (shoot-outs included).
    m["richer_progressed"] = np.where(m.stage.eq("Group Stage"), np.nan, (m.winner == m.richer).astype(float))
    return m


def spearman_ci(x, y, n_boot=4000):
    rng = np.random.default_rng(SEED)
    rho = stats.spearmanr(x, y)[0]
    idx = rng.integers(0, len(x), (n_boot, len(x)))
    boots = [stats.spearmanr(x[i], y[i])[0] for i in idx]
    return rho, *np.percentile(boots, [2.5, 97.5])


def main():
    d = team_metrics(pd.read_csv(P / "teams.csv"))
    m = match_metrics(pd.read_csv(P / "matches.csv"), d)
    d.to_csv(P / "team_metrics.csv", index=False)
    m.to_csv(P / "match_metrics.csv", index=False)

    # 1. Overall association (Spearman, bootstrap 95% CI). Stage is ordinal, so rank correlation.
    y = d.stage_reached.values
    predictors = {
        "Squad market value": d.market_value_m.values,
        "FIFA ranking": -d.fifa_rank.values,
        "Bookmaker title odds": d.p_champion_pct.values,
    }
    assoc = [dict(zip(["predictor", "rho", "lo", "hi"], [k, *spearman_ci(v, y)])) for k, v in predictors.items()]

    # 2. Stage reached by value band.
    bands = (d.groupby("value_band", observed=True)
              .agg(n=("team", "size"),
                   r32=("stage_reached", lambda s: int((s >= 2).sum())),
                   r16=("stage_reached", lambda s: int((s >= 3).sum())),
                   qf=("stage_reached", lambda s: int((s >= 4).sum())))
              .reindex(BAND_LABELS).reset_index())

    # 3. Logistic curve: P(reach stage) vs log value, for the "what would more value buy" read-out.
    X = sm.add_constant(np.log(d.market_value_m))
    grid = np.round(np.geomspace(40, 1600, 60), 1)
    curves, curves_ci, odds = {}, {}, {}
    for key, s in (("r32", 2), ("r16", 3), ("qf", 4)):
        # Binomial GLM = logistic regression, and it gives a 95% CI for the predicted probability.
        fit = sm.GLM((d.stage_reached >= s).astype(int), X, family=sm.families.Binomial()).fit()
        pred = fit.get_prediction(sm.add_constant(np.log(grid))).summary_frame(alpha=0.05)
        curves[key] = pred["mean"].round(4).tolist()
        curves_ci[key] = {"lo": pred.mean_ci_lower.round(4).tolist(), "hi": pred.mean_ci_upper.round(4).tolist()}
        odds[key] = {"or_per_doubling": float(np.exp(fit.params.iloc[1] * np.log(2))), "p": float(fit.pvalues.iloc[1]),
                     "at": {str(v): float(fit.predict(np.array([[1, np.log(v)]]))[0]) for v in (100, 250, 500, 1000)}}

    # 4. Match level: richer side's record by value gap, and the gap by knockout round.
    gap = (m.groupby("gap_band").result.value_counts().unstack(fill_value=0)
             .reindex(GAP_LABELS)[["richer won", "draw", "poorer won"]].reset_index())
    ko = m[m.stage.isin(KO_ROUNDS)]
    rounds = (ko.groupby("stage")
                .agg(n=("match_id", "size"), richer_through=("richer_progressed", "sum"),
                     median_gap=("value_gap", "median"), min_gap=("value_gap", "min"), max_gap=("value_gap", "max"))
                .reindex(KO_ROUNDS).reset_index())
    ko_close = ko[ko.value_gap < 1.5]

    decisive = m[m.result != "draw"]
    k = {
        "matches": len(m), "draws": int((m.result == "draw").sum()),
        "decisive": len(decisive), "richer_won_decisive": int((decisive.result == "richer won").sum()),
        "top32_reached_r32": int((d[d.value_rank <= 32].stage_reached >= 2).sum()),
        "top16_reached_r16": int((d[d.value_rank <= 16].stage_reached >= 3).sum()),
        "top8_reached_qf": int((d[d.value_rank <= 8].stage_reached >= 4).sum()),
        "top4_reached_sf": int((d[d.value_rank <= 4].stage_reached >= 5).sum()),
        "ko_close_n": len(ko_close), "ko_close_richer": int(ko_close.richer_progressed.sum()),
        "ko_n": len(ko), "ko_richer": int(ko.richer_progressed.sum()),
        "on_expectation": int((d.stage_vs_expected == 0).sum()),
        "over": int((d.stage_vs_expected > 0).sum()), "under": int((d.stage_vs_expected < 0).sum()),
        "total_value_m": int(d.market_value_m.sum()),
    }

    # 5. Drivers: what separates teams above the value floor, and who beat the value expectation.
    margin = (m.score_1 - m.score_2).abs()
    grp = m.stage.eq("Group Stage")
    conf = (d.groupby("confederation").stage_vs_expected.agg(n="size", net="sum", mean="mean")
              .sort_values("net", ascending=False).reset_index())
    # "Undervalued" = the market ranks a squad lower than FIFA's results-based ranking does.
    underval = d.value_rank - d.fifa_rank.rank(method="first")
    uefa = d[d.confederation == "UEFA"]
    group_others = (d.groupby("group").market_value_m.transform("sum") - d.market_value_m) / 3
    rho = lambda a, b: dict(zip(["rho", "p"], map(float, stats.spearmanr(a, b))))
    drivers = {
        "ko_close_margin": float((margin[ko.index] <= 1).mean()), "group_close_margin": float((margin[grp] <= 1).mean()),
        "conf": conf.to_dict("records"),
        "hosts": {"n": int(d.host_nation.eq("Yes").sum()), "mean": float(d[d.host_nation.eq("Yes")].stage_vs_expected.mean())},
        "undervalued": {**rho(underval, d.stage_vs_expected), "n_top": int((underval >= 5).sum()),
                        "mean_top": float(d[underval >= 5].stage_vs_expected.mean()),
                        "mean_rest": float(d[underval < 5].stage_vs_expected.mean())},
        "uefa_only": {"n": len(uefa), **rho(uefa.market_value_m, uefa.stage_reached)},
        "group_relative_value_r32": rho(np.log(d.market_value_m / group_others), d.stage_reached >= 2),
        "group_strength_vs_expected": rho(group_others, d.stage_vs_expected),
    }

    teams = d[["team", "confederation", "group", "host_nation", "market_value_m", "value_rank", "fifa_rank",
               "p_champion_pct", "stage_reached", "stage_name", "expected_stage", "stage_vs_expected",
               "group_pts", "gf", "ga", "value_band"]].to_dict("records")
    matches = m[["match_id", "date", "stage", "team_1", "team_2", "score_1", "score_2", "winner",
                 "decided_by_penalties", "richer", "value_gap", "result", "richer_progressed"]] \
        .replace({np.nan: None}).to_dict("records")

    data = {"kpi": k, "assoc": assoc, "bands": bands.to_dict("records"), "gap": gap.to_dict("records"),
            "rounds": rounds.to_dict("records"), "curve_grid": grid.tolist(), "curves": curves, "curves_ci": curves_ci, "odds": odds,
            "drivers": drivers, "teams": teams, "matches": matches, "stages": STAGES}
    (ROOT / "dashboard" / "data.js").write_text("window.DATA = " + json.dumps(data, default=float) + ";\n")

    # Human-readable results for the brief and Q&A prep.
    lines = ["# Results (generated by src/analysis.py; do not edit by hand)\n", "## Headline numbers\n"]
    lines += [f"- The more valuable squad won {k['richer_won_decisive']} of {k['decisive']} matches that had a winner "
              f"after 90/120 min ({k['richer_won_decisive']/k['decisive']:.0%}); {k['draws']} of {k['matches']} were draws.",
              f"- {k['top32_reached_r32']} of the 32 most valuable squads reached the Round of 32.",
              f"- {k['top16_reached_r16']} of the 16 most valuable reached the Round of 16; "
              f"{k['top8_reached_qf']} of the 8 most valuable reached the quarter-finals; "
              f"{k['top4_reached_sf']} of the 4 most valuable reached the semi-finals.",
              f"- Knockout ties: the more valuable side went through in {k['ko_richer']} of {k['ko_n']}; "
              f"when the two squads were within 1.5× in value, {k['ko_close_richer']} of {k['ko_close_n']}.",
              f"- Against a value-only expectation: {k['on_expectation']} teams finished exactly where value ranked them, "
              f"{k['over']} went further, {k['under']} fell short.\n", "## Association with stage reached (Spearman ρ, bootstrap 95% CI, n=48)\n"]
    lines += [f"- {a['predictor']}: ρ = {a['rho']:.2f} [{a['lo']:.2f}, {a['hi']:.2f}]" for a in assoc]
    lines += ["\n## Stage reached by value band\n", bands.to_markdown(index=False),
              "\n## Logistic model: P(reach stage) by squad value\n"]
    for key, o in odds.items():
        at = ", ".join(f"€{v}m: {p:.0%}" for v, p in o["at"].items())
        lines.append(f"- {key}: odds ×{o['or_per_doubling']:.1f} per doubling of value (p={o['p']:.4f}); {at}")
    lines += ["\n## Match result by value gap (all 104 matches)\n", gap.to_markdown(index=False),
              "\n## Knockout rounds\n", rounds.round(2).to_markdown(index=False),
              "\n## Over/under-performance (stages vs value-expected)\n",
              d.sort_values("stage_vs_expected", ascending=False)[["team", "confederation", "market_value_m", "value_rank",
                "fifa_rank", "stage_name", "expected_stage", "stage_vs_expected"]].to_markdown(index=False)]
    dr, u = drivers, drivers["undervalued"]
    lines += ["\n## Drivers\n",
              f"- Matches level or decided by one goal: {dr['ko_close_margin']:.0%} of knockout matches vs "
              f"{dr['group_close_margin']:.0%} of group matches.",
              f"- Hosts: {dr['hosts']['n']} teams, mean {dr['hosts']['mean']:+.2f} stages vs value expectation.",
              f"- 'Undervalued' (value rank minus FIFA rank) vs over/under-performance: ρ = {u['rho']:.2f} (p = {u['p']:.2f}); "
              f"the {u['n_top']} most undervalued (≥5 ranks) averaged {u['mean_top']:+.2f} stages, the rest {u['mean_rest']:+.2f}.",
              f"- Simpson check, UEFA only (n = {dr['uefa_only']['n']}): value vs stage ρ = {dr['uefa_only']['rho']:.2f} "
              f"(p = {dr['uefa_only']['p']:.4f}).",
              f"- Value relative to group opponents vs reaching the Round of 32: ρ = {dr['group_relative_value_r32']['rho']:.2f}; "
              f"group strength vs over/under-performance: ρ = {dr['group_strength_vs_expected']['rho']:.2f}.",
              "\nBy confederation (stages vs value expectation):\n", conf.round(2).to_markdown(index=False)]
    (ROOT / "docs" / "results.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:16]))
    print(rounds.round(2).to_string())


if __name__ == "__main__":
    main()
