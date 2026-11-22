"""Step 3: turn the raw FIFA API files into two clean tables and add the squad values.

Run:  python3 -I analysis/03_build_tables.py

Output
  data/clean/matches.csv  one row per match, 1930-2026, with shoot-out flag and
                          (2006-2026) both squad values and the result for the richer squad
  data/clean/teams.csv    one row per team per World Cup: furthest round, W/D/L, goals,
                          shoot-out wins/losses and (2006-2026) squad value and value rank

Definitions
  FIFA ResultType: 1 = decided in 90 min, 3 = after extra time, 8 = golden goal,
                   2 = penalty shoot-out. Only ResultType 2 counts as a shoot-out.
  Goals exclude shoot-out kicks. A shoot-out match counts as a draw "in play" and as a
  shoot-out win or loss; wins_in_play excludes shoot-out wins.
  Value rank: 1 = most valuable squad of that edition (ties share the better rank).
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "fifa_api"
CLEAN = ROOT / "data" / "clean"

GROUP_LIKE = {"Group Matches", "Group Stage", "First stage", "First Stage"}
STAGE_KEY = {  # FIFA stage name -> our label for the knockout rounds
    "Preliminary Round": "Round of 16",  # 1934: straight knockout of 16 teams
    "1st Round": "Round of 16",          # 1938: straight knockout
    "Round of 32": "Round of 32", "Round of 16": "Round of 16",
    "Quarter-final": "Quarter-final", "Semi-final": "Semi-final",
    "Match for third place": "Third place", "Play-off for third place": "Third place",
    "Bronze final": "Third place", "Final": "Final",
    "Second Round": "Second group stage",  # 1974-1982
    "Final Round": "Final group",          # 1950
}
# Furthest round reached, best last. Used to order outcomes in the analysis.
OUTCOMES = ["Group stage", "Round of 32", "Second group stage", "Round of 16", "Quarter-final",
            "Semi-final", "Final", "Champion"]


def name(team):
    return team["TeamName"][0]["Description"]


def load_matches():
    rows = []
    for f in sorted(RAW.glob("matches_*.json")):
        year = int(f.stem.split("_")[1])
        for m in json.loads(f.read_text())["Results"]:
            h, a = m["Home"], m["Away"]
            if not h or not a or m["HomeTeamScore"] is None:
                continue  # not played
            stage_raw = m["StageName"][0]["Description"]
            ids = {h["IdTeam"]: h["IdCountry"], a["IdTeam"]: a["IdCountry"]}
            pens = m["ResultType"] == 2
            rows.append({
                "year": year, "match_id": m["IdMatch"], "date": m["Date"][:10],
                "stage_fifa": stage_raw,
                "phase": "Group" if stage_raw in GROUP_LIKE else STAGE_KEY[stage_raw],
                "team_1": h["IdCountry"], "team_1_name": name(h),
                "team_2": a["IdCountry"], "team_2_name": name(a),
                "score_1": m["HomeTeamScore"], "score_2": m["AwayTeamScore"],
                "result_type": m["ResultType"], "shootout": int(pens),
                "pen_1": m["HomeTeamPenaltyScore"] if pens else "",
                "pen_2": m["AwayTeamPenaltyScore"] if pens else "",
                "winner": ids.get(m["Winner"], "") if m["Winner"] else "",
            })
    # sanity: a match without a FIFA winner must be level in play
    for r in rows:
        if not r["winner"]:
            assert r["score_1"] == r["score_2"], r
        if r["shootout"]:
            assert r["score_1"] == r["score_2"] and r["winner"], r
    return rows


def final_group_order(matches):
    """1950 had a final group of four instead of a final: rank by points (2 per win)."""
    pts, gd = defaultdict(int), defaultdict(int)
    for m in matches:
        for me, op, s, c in ((m["team_1"], m["team_2"], m["score_1"], m["score_2"]),
                             (m["team_2"], m["team_1"], m["score_2"], m["score_1"])):
            pts[me] += 2 if m["winner"] == me else (1 if not m["winner"] else 0)
            gd[me] += s - c
    return sorted(pts, key=lambda t: (-pts[t], -gd[t]))


def build_teams(matches):
    stats = {}
    by_year = defaultdict(list)
    for m in matches:
        by_year[m["year"]].append(m)
    for year, ms in by_year.items():
        for m in ms:
            for side, other in ((1, 2), (2, 1)):
                code = m[f"team_{side}"]
                s = stats.setdefault((year, code), {
                    "year": year, "code": code, "team": m[f"team_{side}_name"], "phases": set(),
                    "matches": 0, "wins": 0, "wins_in_play": 0, "draws_in_play": 0, "losses": 0,
                    "goals_for": 0, "goals_against": 0, "shootout_wins": 0, "shootout_losses": 0,
                    "ko_matches": 0, "ko_wins_in_play": 0})
                s["phases"].add(m["phase"])
                s["matches"] += 1
                s["goals_for"] += m[f"score_{side}"]
                s["goals_against"] += m[f"score_{other}"]
                ko = m["phase"] not in ("Group", "Second group stage", "Final group")
                s["ko_matches"] += ko
                if m["shootout"]:
                    s["draws_in_play"] += 1
                    won = m["winner"] == code
                    s["shootout_wins" if won else "shootout_losses"] += 1
                    s["wins"] += won
                    s["losses"] += not won
                elif not m["winner"]:
                    s["draws_in_play"] += 1
                elif m["winner"] == code:
                    s["wins"] += 1
                    s["wins_in_play"] += 1
                    s["ko_wins_in_play"] += ko
                else:
                    s["losses"] += 1

        # furthest round and placing
        final = [m for m in ms if m["phase"] == "Final"]
        third = [m for m in ms if m["phase"] == "Third place"]
        placing = {}
        if final:
            f = final[0]
            placing[f["winner"]] = 1
            placing[f["team_1"] if f["winner"] == f["team_2"] else f["team_2"]] = 2
        else:  # 1950
            for i, t in enumerate(final_group_order([m for m in ms if m["phase"] == "Final group"])):
                placing[t] = i + 1
        if third:
            t = third[0]
            placing[t["winner"]] = 3
            placing[t["team_1"] if t["winner"] == t["team_2"] else t["team_2"]] = 4
        for (y, code), s in stats.items():
            if y != year:
                continue
            p = placing.get(code)
            ph = s["phases"]
            if p == 1:
                stage = "Champion"
            elif p == 2:
                stage = "Final"
            elif p in (3, 4) or "Semi-final" in ph:
                stage = "Semi-final"
            elif "Final group" in ph:
                stage = "Semi-final"  # 1950: the four teams of the final group
            else:
                stage = next(o for o in reversed(OUTCOMES[:5])
                             if o in ph or (o == "Group stage"))
            s["placing"] = p or ""
            s["stage"] = stage
            s["stage_n"] = OUTCOMES.index(stage)
    for s in stats.values():
        s.pop("phases")
    return sorted(stats.values(), key=lambda s: (s["year"], -s["stage_n"], s["code"]))


def add_values(teams, matches):
    vals = {}
    with open(CLEAN / "squad_values.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            vals[(int(r["year"]), r["code"])] = float(r["value_m"])
    years = sorted({y for y, _ in vals})
    for y in years:
        vs = sorted((v for (yy, _), v in vals.items() if yy == y), reverse=True)
        n = len(vs)
        median = (vs[n // 2] + vs[(n - 1) // 2]) / 2
        for t in teams:
            if t["year"] != y:
                continue
            v = vals[(y, t["code"])]
            t["value_m"] = v
            t["value_rank"] = vs.index(v) + 1
            t["teams_in_edition"] = n
            t["value_vs_median"] = round(v / median, 2)
            t["value_share_of_top"] = round(v / vs[0], 3)
    for m in matches:
        v1, v2 = vals.get((m["year"], m["team_1"])), vals.get((m["year"], m["team_2"]))
        m["value_1"], m["value_2"] = v1 or "", v2 or ""
        if v1 is None or v2 is None or v1 == v2:
            m["richer"] = m["value_ratio"] = m["richer_result_in_play"] = m["richer_won"] = ""
            continue
        rich = m["team_1"] if v1 > v2 else m["team_2"]
        m["richer"] = rich
        m["value_ratio"] = round(max(v1, v2) / min(v1, v2), 2)
        if m["shootout"] or not m["winner"]:
            m["richer_result_in_play"] = "D"
        else:
            m["richer_result_in_play"] = "W" if m["winner"] == rich else "L"
        m["richer_won"] = "" if not m["winner"] else int(m["winner"] == rich)


def write(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, restval="")
        w.writeheader()
        w.writerows(rows)


def main():
    matches = load_matches()
    teams = build_teams(matches)
    add_values(teams, matches)
    write(CLEAN / "matches.csv", matches)
    write(CLEAN / "teams.csv", teams)
    print(f"matches.csv: {len(matches)} matches, {len({m['year'] for m in matches})} World Cups, "
          f"{sum(m['shootout'] for m in matches)} shoot-outs")
    print(f"teams.csv:   {len(teams)} team appearances, "
          f"{sum(1 for t in teams if 'value_m' in t)} with squad value")
    for y in sorted({t["year"] for t in teams}):
        champ = next(t for t in teams if t["year"] == y and t["stage"] == "Champion")
        print(f"  {y} champion {champ['team']}")


if __name__ == "__main__":
    main()
