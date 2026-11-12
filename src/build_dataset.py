"""Build the cleaned team- and match-level tables used by the analysis and dashboard.

Run:  .venv/bin/python src/build_dataset.py
Inputs  (untouched):  data/raw/...
Outputs:              data/processed/teams.csv, data/processed/matches.csv

Every transformation here is also logged in docs/decisions.md.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# Ordered stages. The value is "stage reached" (1 = played group stage only, 7 = champion).
STAGES = ["Group Stage", "Round of 32", "Round of 16", "Quarterfinal", "Semifinal", "Final", "Champion"]
STAGE_IDX = {s: i + 1 for i, s in enumerate(STAGES)}
# How many teams reach at least each stage in a 48-team tournament.
TEAMS_REACHING = {1: 48, 2: 32, 3: 16, 4: 8, 5: 4, 6: 2, 7: 1}

NAME_FIX = {"Bosnia & Herz.": "Bosnia and Herzegovina"}


def load_pre_tournament() -> pd.DataFrame:
    pre = pd.read_csv(RAW / "fifa-world-cup-2026-48-teams-dataset" / "World Cup 2026.csv", encoding="utf-8-sig")
    pre["Team"] = pre["Team"].replace(NAME_FIX)
    pre = pre.rename(columns={
        "Team": "team", "Group": "group", "Confederation": "confederation",
        "FIFA Ranking": "fifa_rank", "World Cup Appearances": "wc_appearances",
        "World Titles": "world_titles", "Squad Market Value (€m)": "market_value_m",
        "Group Stage Qual. (%)": "p_qualify_group_pct", "Championship Prob. (%)": "p_champion_pct",
        "First Appearance": "debut", "Star Player": "star_player",
        "Championship Category": "pre_category",
    })
    keep = ["team", "group", "confederation", "fifa_rank", "market_value_m", "p_qualify_group_pct",
            "p_champion_pct", "wc_appearances", "world_titles", "debut", "star_player", "pre_category"]
    return pre[keep]


def load_matches() -> pd.DataFrame:
    m = pd.read_csv(RAW / "2026-fifa-world-cup" / "matches.csv")
    # Result after 90/120 minutes; a penalty shoot-out counts as a draw for "result",
    # but the shoot-out winner progresses.
    m["result_1"] = np.sign(m.score_1 - m.score_2).map({1: "W", 0: "D", -1: "L"})
    m["progressed"] = np.where(m.winner.eq("Draw"), None, m.winner)
    return m


def stage_reached(m: pd.DataFrame, teams: list[str]) -> pd.Series:
    """Derive the furthest stage from the match list (not the hand-typed eliminated_round label)."""
    ko = m[m.stage.isin(["Round of 32", "Round of 16", "Quarterfinal", "Semifinal", "Final"])]
    reached = {t: 1 for t in teams}
    for _, r in ko.iterrows():
        for t in (r.team_1, r.team_2):
            reached[t] = max(reached[t], STAGE_IDX[r.stage])
    final = m[m.stage == "Final"].iloc[0]
    reached[final.winner] = STAGE_IDX["Champion"]
    return pd.Series(reached, name="stage_reached")


def team_match_stats(m: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in m.iterrows():
        for a, b, ga, gb in ((r.team_1, r.team_2, r.score_1, r.score_2), (r.team_2, r.team_1, r.score_2, r.score_1)):
            rows.append({"team": a, "opponent": b, "stage": r.stage, "gf": ga, "ga": gb,
                         "pts": 3 if ga > gb else 1 if ga == gb else 0})
    long = pd.DataFrame(rows)
    grp = long[long.stage == "Group Stage"].groupby("team").agg(group_pts=("pts", "sum"), group_gd=("gf", "sum"))
    grp["group_gd"] = grp.group_gd - long[long.stage == "Group Stage"].groupby("team").ga.sum()
    allm = long.groupby("team").agg(matches=("pts", "size"), gf=("gf", "sum"), ga=("ga", "sum"))
    return grp.join(allm)


def main():
    pre = load_pre_tournament()
    m = load_matches()
    res = pd.read_csv(RAW / "2026-fifa-world-cup" / "teams.csv")[["team", "host_nation"]]

    df = pre.merge(res, on="team", how="outer", validate="1:1")
    assert len(df) == 48 and df.notna().all().all(), "team join is not clean"
    df = df.join(stage_reached(m, df.team.tolist()), on="team").join(team_match_stats(m), on="team")
    df["stage_name"] = df.stage_reached.map({v: k for k, v in STAGE_IDX.items()})

    # Value rank (1 = most valuable). Ties (e.g. three squads at €980m) are broken by FIFA rank.
    df = df.sort_values(["market_value_m", "fifa_rank"], ascending=[False, True]).reset_index(drop=True)
    df["value_rank"] = np.arange(1, 49)
    df["value_share_pct"] = 100 * df.market_value_m / df.market_value_m.sum()

    # Sanity checks against the published counts per stage.
    for s, n in TEAMS_REACHING.items():
        assert (df.stage_reached >= s).sum() == n, f"stage {s}: {(df.stage_reached >= s).sum()} != {n}"

    df.to_csv(OUT / "teams.csv", index=False)
    m.to_csv(OUT / "matches.csv", index=False)
    print(f"wrote {len(df)} teams, {len(m)} matches")


if __name__ == "__main__":
    main()
