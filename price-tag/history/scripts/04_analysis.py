"""Step 4: how far did squad value carry teams at the World Cups 2006-2026?

Run:  python3 -I analysis/04_analysis.py
Output: data/clean/history_results.txt (also printed) and data/clean/rounds_by_value_band.csv

All counts come from data/clean/teams.csv and data/clean/matches.csv (step 3).
"""
import csv
from collections import defaultdict
from statistics import median
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data" / "clean"
OUT_LINES = []


def say(line=""):
    print(line)
    OUT_LINES.append(line)


def pct(a, b):
    return f"{a}/{b} = {100 * a / b:.0f} %" if b else f"{a}/0"


def load(name):
    with open(CLEAN / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


teams = [t for t in load("teams.csv") if t["value_m"]]
for t in teams:
    t["year"], t["stage_n"], t["value_rank"] = int(t["year"]), int(t["stage_n"]), int(t["value_rank"])
    t["value_m"] = float(t["value_m"])
    for k in ("shootout_wins", "shootout_losses", "wins", "wins_in_play", "matches"):
        t[k] = int(t[k])
matches = [m for m in load("matches.csv") if m["richer"]]
YEARS = sorted({t["year"] for t in teams})
STAGE = {"Round of 16": 3, "Quarter-final": 4, "Semi-final": 5, "Final": 6, "Champion": 7}
# (Round of 32 = 1, only 2026; the 2026 knockout starts one round earlier.)


def reached(t, stage):
    return t["stage_n"] >= STAGE[stage]


# ---------------------------------------------------------------- 1. per edition
say("=" * 78)
say("1. WHO GOT HOW FAR, PER WORLD CUP (value rank 1 = most expensive squad)")
say("=" * 78)
for y in YEARS:
    ts = sorted([t for t in teams if t["year"] == y], key=lambda t: t["value_rank"])
    top = ts[0]
    say(f"\n{y}  ({len(ts)} teams, most expensive {top['team']} €{top['value_m']:,.0f}m, "
        f"median €{median(t['value_m'] for t in ts):,.0f}m)")
    for st in ("Champion", "Final", "Semi-final", "Quarter-final"):
        row = [t for t in ts if t["stage"] == st]
        say(f"  {st:14s} " + ", ".join(f"{t['team']} (#{t['value_rank']}, €{t['value_m']:,.0f}m)" for t in row))

# ---------------------------------------------------------------- 2. value bands
say("\n" + "=" * 78)
say("2. HOW FAR EACH PRICE BAND GOT, 2006-2026 POOLED (rank within its own World Cup)")
say("=" * 78)
say("Ranks are used instead of euros because the median squad value rose sixfold from 2006 to 2026.")
say("2026 had 48 teams and an extra round of 32, so its lower bands are larger.")
BANDS = [("Top 4", 1, 4), ("Rank 5-8", 5, 8), ("Rank 9-16", 9, 16), ("Rank 17+", 17, 99)]
band_rows = []
for label, lo, hi in BANDS:
    ts = [t for t in teams if lo <= t["value_rank"] <= hi]
    row = {"band": label, "teams": len(ts)}
    parts = []
    for st in ("Quarter-final", "Semi-final", "Final", "Champion"):
        n = sum(reached(t, st) for t in ts)
        row[f"reached_{st}"] = n
        parts.append(f"{st[:5]} {pct(n, len(ts))}")
    band_rows.append(row)
    say(f"  {label:9s} n={len(ts):3d}  " + " | ".join(parts))
with open(CLEAN / "rounds_by_value_band.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(band_rows[0]))
    w.writeheader()
    w.writerows(band_rows)

for st in ("Champion", "Final", "Semi-final"):
    ts = [t for t in teams if reached(t, st)]
    what = "won the title" if st == "Champion" else f"reached the {st.lower()}"
    in_top4 = sum(t["value_rank"] <= 4 for t in ts)
    in_top8 = sum(t["value_rank"] <= 8 for t in ts)
    cheapest = max(ts, key=lambda t: t["value_rank"])
    say(f"  Of all {len(ts)} teams that {what}: {in_top4} were a top-4 squad, "
        f"{in_top8} a top-8 squad; cheapest was {cheapest['team']} {cheapest['year']} "
        f"(#{cheapest['value_rank']}, €{cheapest['value_m']:,.0f}m)")

# ---------------------------------------------------------------- 3. €500m line
say("\n" + "=" * 78)
say("3. THE €500m LINE PER WORLD CUP (nominal euros, not adjusted)")
say("=" * 78)
for y in YEARS:
    ts = [t for t in teams if t["year"] == y]
    big = [t for t in ts if t["value_m"] >= 500]
    small = [t for t in ts if t["value_m"] < 500]
    say(f"  {y}: {len(big):2d} squads >= €500m | semi-finalists from them: "
        f"{sum(reached(t, 'Semi-final') for t in big)}/4 | finalists: {sum(reached(t, 'Final') for t in big)}/2"
        f" | champion >= €500m: {'yes' if any(t['stage'] == 'Champion' for t in big) else 'no'}")
big = [t for t in teams if t["value_m"] >= 500]
small = [t for t in teams if t["value_m"] < 500]
for st in ("Quarter-final", "Semi-final", "Final"):
    say(f"  pooled {st:13s}: >= €500m {pct(sum(reached(t, st) for t in big), len(big))} | "
        f"< €500m {pct(sum(reached(t, st) for t in small), len(small))}")
n06 = sum(t["value_m"] >= 500 for t in teams if t["year"] == YEARS[0])
n26 = sum(t["value_m"] >= 500 for t in teams if t["year"] == YEARS[-1])
say(f"  Caution: {YEARS[0]} had {n06} squads above €500m, {YEARS[-1]} had {n26}. The same euro line means")
say("  something different each time, so use ranks (section 2) for the cross-year story.")

# ---------------------------------------------------------------- 4. matches
say("\n" + "=" * 78)
say("4. DOES THE MORE EXPENSIVE SQUAD WIN THE MATCH? (2006-2026)")
say("=" * 78)
for label, sel in (("Group matches", lambda m: m["phase"] == "Group"),
                   ("Knockout matches", lambda m: m["phase"] != "Group")):
    ms = [m for m in matches if sel(m)]
    w = sum(m["richer_result_in_play"] == "W" for m in ms)
    d = sum(m["richer_result_in_play"] == "D" for m in ms)
    l = sum(m["richer_result_in_play"] == "L" for m in ms)
    say(f"  {label:17s} n={len(ms):3d}: richer squad won {w}, drew {d}, lost {l} in play "
        f"(wins {100 * w / len(ms):.0f} %)")
ko = [m for m in matches if m["phase"] != "Group"]
decided = [m for m in ko if not int(m["shootout"])]
so = [m for m in ko if int(m["shootout"])]
say(f"  Knockouts decided in play or extra time: richer squad won "
    f"{pct(sum(m['richer_won'] == '1' for m in decided), len(decided))}")
say(f"  Knockouts decided on penalties:           richer squad won "
    f"{pct(sum(m['richer_won'] == '1' for m in so), len(so))}")
for y in YEARS:
    k = [m for m in ko if int(m["year"]) == y]
    dk = [m for m in k if not int(m["shootout"])]
    sk = [m for m in k if int(m["shootout"])]
    say(f"    {y}: in play {pct(sum(m['richer_won'] == '1' for m in dk), len(dk))} | "
        f"penalties {pct(sum(m['richer_won'] == '1' for m in sk), len(sk))}")

say("\n  Knockouts by size of the value gap (decided in play only):")
for lo, hi, lab in ((1, 1.5, "richer by < 1.5x"), (1.5, 3, "1.5x to 3x"), (3, 1e9, "3x or more")):
    ms = [m for m in decided if lo <= float(m["value_ratio"]) < hi]
    say(f"    {lab:17s} richer squad won {pct(sum(m['richer_won'] == '1' for m in ms), len(ms))}")

# ---------------------------------------------------------------- 5. shoot-outs
say("\n" + "=" * 78)
say("5. PENALTY SHOOT-OUTS 2006-2026")
say("=" * 78)
for m in so:
    winner = m["team_1_name"] if m["winner"] == m["team_1"] else m["team_2_name"]
    say(f"  {m['year']} {m['phase']:13s} {m['team_1_name']} {m['score_1']}-{m['score_2']} "
        f"{m['team_2_name']} (pens {m['pen_1']}-{m['pen_2']}), won by {winner} "
        f"({'richer' if m['richer_won'] == '1' else 'cheaper'} squad, gap {m['value_ratio']}x)")
sw = defaultdict(lambda: [0, 0])
for t in teams:
    sw[t["team"]][0] += t["shootout_wins"]
    sw[t["team"]][1] += t["shootout_losses"]
say("  Shoot-out record by team (won-lost): " + ", ".join(
    f"{k} {v[0]}-{v[1]}" for k, v in sorted(sw.items(), key=lambda kv: (-kv[1][0], kv[1][1])) if sum(v)))

# ---------------------------------------------------------------- 6. over/under
say("\n" + "=" * 78)
say("6. BEAT THEIR PRICE TAG (reached at least the quarter-final from value rank 12 or lower)")
say("=" * 78)
for t in sorted([t for t in teams if reached(t, "Quarter-final") and t["value_rank"] >= 12],
                key=lambda t: (t["year"], t["value_rank"])):
    say(f"  {t['year']} {t['team']:22s} rank #{t['value_rank']:2d} €{t['value_m']:6,.0f}m -> {t['stage']}"
        f" (shoot-outs won {t['shootout_wins']})")

(CLEAN / "history_results.txt").write_text("\n".join(OUT_LINES) + "\n", encoding="utf-8")
print("\nwrote data/clean/history_results.txt and data/clean/rounds_by_value_band.csv")
