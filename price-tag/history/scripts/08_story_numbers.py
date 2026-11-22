"""Step 8: every number on the Portugal slides, in one place.

Run:  python3 -I scripts/08_story_numbers.py   (after steps 2-4 and 7)
Writes data/clean/story_numbers.txt; the notebook Team14_Analysis.ipynb shows the same tables.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data" / "clean"
LINES = ["GK", "DF", "MF", "FW"]
NAMES = {"GK": "Goalkeepers", "DF": "Defence", "MF": "Midfield", "FW": "Attack"}
CONTENDERS = ["FRA", "ARG", "ESP", "GER", "POR", "BRA", "ENG"]
out = []


def say(s=""):
    out.append(str(s))


def pct(a, b):
    return f"{a}/{b} = {a / b:.0%}" if b else f"{a}/0"


def band(r):
    return "Top 4" if r <= 4 else "Rank 5-8" if r <= 8 else "Rank 9-16" if r <= 16 else "Rank 17+"


teams = pd.read_csv(CLEAN / "teams.csv")
teams = teams[teams.year >= 2006].copy()
teams["band"] = teams.value_rank.map(band)
matches = pd.read_csv(CLEAN / "matches.csv")
matches = matches[matches.year >= 2006]
sp = pd.read_csv(CLEAN / "squad_positions.csv")
players = pd.read_csv(CLEAN / "players.csv")

say("=" * 78)
say("A. DATA")
say("=" * 78)
say(f"World Cups 2006-2026: {teams.year.nunique()}, squads {len(teams)}, matches {len(matches)}, "
    f"knockout matches {len(matches[matches.phase != 'Group'])}")
say(f"Players in FIFA squads: {len(players)}; matched to Transfermarkt {players.tm_id.notna().sum()}, "
    f"with a value {players.value_m.notna().sum()}")
say("Median squad value per World Cup (€m): " +
    ", ".join(f"{y} {g.value_m.median():.0f}" for y, g in teams.groupby("year")))
t10 = sp[sp.value_rank <= 10]
say("Player values traced, as share of published squad value (median of the top-10 squads): " +
    ", ".join(f"{y} {g.coverage.median():.0%}" for y, g in t10.groupby("year")))
say("Median over all squads: " + ", ".join(f"{y} {g.coverage.median():.0%}" for y, g in sp.groupby("year")))

say()
say("=" * 78)
say("B. WHAT A TOP-10 SQUAD IS (2026)")
say("=" * 78)
t26 = teams[teams.year == 2026].sort_values(["value_rank", "team"])
for r in t26.head(12).itertuples():
    say(f"  #{r.value_rank:.0f}  {r.team:12s} €{r.value_m:,.0f}m  {r.stage}")
say(f"  Median of 48 squads: €{t26.value_m.median():.0f}m")
say("Portugal's value rank: " + ", ".join(f"{r.year} #{r.value_rank:.0f} (€{r.value_m:.0f}m, {r.stage})"
                                          for r in teams[teams.code == "POR"].itertuples()))

say()
say("=" * 78)
say("C. THE CONTENDERS: top-10 squad at all six World Cups")
say("=" * 78)
always = teams[teams.value_rank <= 10].groupby("code").year.nunique()
always = always[always == 6].index.tolist()
for c in always:
    g = teams[teams.code == c]
    say(f"  {g.team.iloc[0]:10s} finals {(g.stage_n >= 6).sum()}, semis {(g.stage_n >= 5).sum()}, "
        f"titles {(g.stage == 'Champion').sum()}, ranks {g.value_rank.astype(int).tolist()}")

say()
say("=" * 78)
say("D. MONEY AND THE FINAL: share of squads reaching each round by value rank, 2006-2026")
say("=" * 78)
rates = {}
for b in ["Top 4", "Rank 5-8", "Rank 9-16", "Rank 17+"]:
    g = teams[teams.band == b]
    rates[b] = ((g.stage_n >= 6).mean(), (g.stage_n >= 5).mean())
    say(f"  {b:10s} n={len(g):3d} final {pct((g.stage_n >= 6).sum(), len(g))} | "
        f"semi {pct((g.stage_n >= 5).sum(), len(g))} | QF {pct((g.stage_n >= 4).sum(), len(g))}")
teams["exp_final"] = teams.band.map(lambda b: rates[b][0])
teams["exp_semi"] = teams.band.map(lambda b: rates[b][1])
say("Expected finals from value rank alone vs actual:")
for c in always:
    g = teams[teams.code == c]
    say(f"  {g.team.iloc[0]:10s} expected {g.exp_final.sum():.2f}, actual {(g.stage_n >= 6).sum()} | "
        f"semis expected {g.exp_semi.sum():.2f}, actual {(g.stage_n >= 5).sum()}")

say()
say("=" * 78)
say("E. WHERE THE MONEY SITS: value per line (GK, DF, MF, FW), 2010-2026")
say("=" * 78)
say("2006 left out: only 32% of published squad value could be traced to players.")
p = sp[sp.year >= 2010].copy()
for k in LINES:
    p[k + "_r"] = p.groupby("year")[k + "_m"].rank(ascending=False, method="min")
top = p[p.value_rank <= 10].copy()
say(f"Top-10 squads (by published value) 2010-2026: {len(top)}")
for k in LINES:
    a, b = top[top[k + "_r"] <= 5], top[top[k + "_r"] > 5]
    say(f"  {NAMES[k]:11s} top 5 in that line: final {pct((a.stage_n >= 6).sum(), len(a))}, "
        f"semi {pct((a.stage_n >= 5).sum(), len(a))} | not top 5: final {pct((b.stage_n >= 6).sum(), len(b))}, "
        f"semi {pct((b.stage_n >= 5).sum(), len(b))}")
fin = p[p.stage_n >= 6]
say(f"Finalists 2010-2026: attack value rank {sorted(fin.FW_r.astype(int).tolist())} "
    f"-> {(fin.FW_r <= 5).sum()} of {len(fin)} had a top-5 attack")
say("Control for total value (top-10 squads):")
for lo, hi in [(1, 5), (6, 10)]:
    g = top[(top.value_rank >= lo) & (top.value_rank <= hi)]
    a, b = g[g.FW_r <= 5], g[g.FW_r > 5]
    say(f"  overall rank {lo}-{hi}: top-5 attack final {pct((a.stage_n >= 6).sum(), len(a))} | "
        f"other final {pct((b.stage_n >= 6).sum(), len(b))}")
say("Rank correlation (Spearman) of each line's value rank with the round reached, all squads 2010-2026:")
p["tot_r"] = p.groupby("year")["sum_m"].rank(ascending=False, method="min")
for k in LINES + ["tot"]:
    say(f"  {NAMES.get(k, 'Whole squad'):11s} {-p[k + '_r'].corr(p.stage_n, method='spearman'):.2f}")

say()
say("Portugal by line (€m, value rank of that line in its World Cup):")
por = p[p.code == "POR"]
for r in por.itertuples():
    say(f"  {r.year}: " + ", ".join(f"{k} €{getattr(r, k + '_m'):.0f}m #{getattr(r, k + '_r'):.0f}" for k in LINES) +
        f" | attack share {r.FW_m / r.sum_m:.0%} | {r.stage}")
for y in [2010, 2014, 2018, 2022, 2026]:
    g = players[(players.code == "POR") & (players.year == y)].sort_values("value_m", ascending=False).head(3)
    say(f"  {y} top 3: " + ", ".join(f"{r.tm_name} ({r.position}, €{r.value_m:.0f}m)" for r in g.itertuples()))

say()
say("=" * 78)
say("F. GROUP PLACE (top-8 squads by value, 2006-2026)")
say("=" * 78)
def group_places(m):
    """Group place from points, goal difference, goals (as in the deck)."""
    places = {}
    for y, g in m[m.phase == "Group"].groupby("year"):
        par = {}

        def root(x):
            while par.setdefault(x, x) != x:
                x = par[x]
            return x
        st = {}
        for r in g.itertuples():
            par[root(r.team_1)] = root(r.team_2)
            for t, a, b in ((r.team_1, r.score_1, r.score_2), (r.team_2, r.score_2, r.score_1)):
                v = st.setdefault(t, [0, 0, 0])
                v[0] += 3 if a > b else 1 if a == b else 0
                v[1] += a - b
                v[2] += a
        groups = {}
        for t in st:
            groups.setdefault(root(t), []).append(t)
        for mem in groups.values():
            mem.sort(key=lambda t: st[t], reverse=True)
            for i, t in enumerate(mem, 1):
                places[(y, t)] = i
    return places


gp = group_places(matches)
teams["group_place"] = [gp.get((r.year, r.code)) for r in teams.itertuples()]
t8 = teams[teams.value_rank <= 8]
for place in [1, 2]:
    g = t8[t8.group_place == place]
    say(f"  Top-8 squads, place {place}: quarter-final {pct((g.stage_n >= 4).sum(), len(g))}, "
        f"semi {pct((g.stage_n >= 5).sum(), len(g))}, final {pct((g.stage_n >= 6).sum(), len(g))}")
allp = teams[teams.group_place.isin([1, 2])]
for place in [1, 2]:
    g = allp[allp.group_place == place]
    say(f"  All squads, place {place}: quarter-final {pct((g.stage_n >= 4).sum(), len(g))}")
say("  Portugal: " + ", ".join(f"{r.year} place {r.group_place} -> {r.stage}" for r in teams[teams.code == "POR"].itertuples()))

say()
say("=" * 78)
say("G. KNOCKOUTS AND PENALTIES 2006-2026")
say("=" * 78)
ko = matches[(matches.phase != "Group") & matches.richer.notna()]
inplay, pens = ko[ko.shootout == 0], ko[ko.shootout == 1]
say(f"  richer squad wins in 90/120 min: {pct(int(inplay.richer_won.sum()), len(inplay))} "
    f"(of these, decided: {len(inplay)})")
say(f"  richer squad wins on penalties: {pct(int(pens.richer_won.sum()), len(pens))}")
por_ko = ko[(ko.team_1 == "POR") | (ko.team_2 == "POR")]
for r in por_ko.itertuples():
    opp = r.team_2_name if r.team_1 == "POR" else r.team_1_name
    say(f"  Portugal {r.year} {r.stage_fifa}: vs {opp} {r.score_1}-{r.score_2}"
        f"{' (pens ' + str(int(r.pen_1)) + '-' + str(int(r.pen_2)) + ')' if r.shootout == 1 else ''}, winner {r.winner}")

(CLEAN / "story_numbers.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
