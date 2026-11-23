"""Step 7: give every World Cup player 2006-2026 a position and a market value.

Run:  python3 -I scripts/07_player_values.py   (after 06_fetch_squads.py)

Inputs
  data/raw/fifa_squads/*.json                 squads with positions (FIFA API, step 6)
  data/raw/transfermarkt_dcaribou/players.csv.gz, player_valuations.csv.gz
      public "transfermarkt-datasets" project (github.com/dcaribou/transfermarkt-datasets,
      also on Kaggle as davidcariboo/player-scores): Transfermarkt market-value history per player

Matching (FIFA name -> Transfermarkt player), within the player's country, age 16-42 at
the tournament:
  1. same name after removing accents, case and punctuation
  2. every word of the shorter name appears in the longer one
  3. FIFA short name equals the Transfermarkt name or last name
If a rule finds several namesakes, the one with the highest market value at the time is taken
(a World Cup player is almost always the most valuable player of that name in his country).
Value = the last Transfermarkt valuation on or before the opening match, at most 18 months old.
Position = FIFA's code (goalkeeper, defender, midfielder, forward); where FIFA gives none
(code 4, mostly substitutes in 2018 and 2022) the Transfermarkt position is used.

Outputs (data/clean/)
  players.csv            one row per player per World Cup: position, matched id, value
  squad_positions.csv    one row per squad: value per position, coverage vs published total
"""
import csv
import glob
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
POS = {0: "GK", 1: "DF", 2: "MF", 3: "FW"}
TM_POS = {"Goalkeeper": "GK", "Defender": "DF", "Midfield": "MF", "Attack": "FW"}
COUNTRY = {  # FIFA team name -> Transfermarkt citizenship name
    "Bosnia and Herzegovina": ["Bosnia-Herzegovina"], "Cabo Verde": ["Cape Verde"],
    "Congo DR": ["DR Congo"], "Curaçao": ["Curacao"], "Czechia": ["Czech Republic"],
    "Côte d'Ivoire": ["Cote d'Ivoire"], "IR Iran": ["Iran"], "Korea DPR": ["Korea, North"],
    "Korea Republic": ["Korea, South"], "USA": ["United States"],
    "Serbia and Montenegro": ["Serbia and Montenegro", "Serbia", "Montenegro"],
}


# Reviewed FIFA identities that collided in the automatic name match.
# None means the local Transfermarkt extract has no confirmed counterpart.
REVIEWED_IDS = {
    "176534": None,    # Gilberto Melo
    "187267": None,    # Gilberto Silva
    "187204": None,    # Miguel, Portugal defender
    "357006": None,    # Alex Rodríguez, Panama goalkeeper
    "395427": 238223,  # Ederson, Brazil goalkeeper
    "485069": 607854,  # Éderson, Brazil midfielder
    "335656": 145707,  # Danilo, Brazil defender
    "429392": 808509,  # Danilo Santos, Brazil midfielder
}


def words(s: str) -> list:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z ]", " ", s.replace("-", " ")).split()


def main() -> None:
    tm = pd.read_csv(RAW / "transfermarkt_dcaribou" / "players.csv.gz",
                     usecols=["player_id", "name", "first_name", "last_name", "country_of_citizenship",
                              "country_of_birth", "date_of_birth", "position"])
    tm["dob"] = pd.to_datetime(tm["date_of_birth"], errors="coerce")
    tm["w"] = tm["name"].map(words)
    by_country = defaultdict(list)
    for r in tm.itertuples():
        for c in {r.country_of_citizenship, r.country_of_birth}:
            if isinstance(c, str):
                by_country[c].append(r)

    val = pd.read_csv(RAW / "transfermarkt_dcaribou" / "player_valuations.csv.gz",
                      usecols=["player_id", "date", "market_value_in_eur"])
    val["date"] = pd.to_datetime(val["date"])
    val = val.sort_values("date")
    val_by_id = {pid: g[["date", "market_value_in_eur"]].to_numpy() for pid, g in val.groupby("player_id")}

    published = pd.read_csv(CLEAN / "squad_values.csv").set_index(["year", "code"])["value_m"].to_dict()
    teams = pd.read_csv(CLEAN / "teams.csv")
    teams = teams[teams.year >= 2006].set_index(["year", "code"])

    rows = []
    for f in sorted(glob.glob(str(RAW / "fifa_squads" / "*.json"))):
        sq = json.loads(Path(f).read_text())
        start = pd.Timestamp(sq["match_date"][:10])
        cands = []
        for c in COUNTRY.get(sq["team"], [sq["team"]]):
            cands += by_country.get(c, [])
        cands = [r for r in cands if pd.notna(r.dob) and 16 <= (start - r.dob).days / 365.25 <= 42]
        def value_at(pid):
            hist = val_by_id.get(pid)
            if hist is None:
                return None
            before = hist[hist[:, 0] <= start]
            if len(before) and (start - before[-1][0]).days <= 548:
                return float(before[-1][1]) / 1e6
            return None

        def pick(lst):
            if not lst:
                return None
            if len(lst) == 1:
                return lst[0]
            return max(lst, key=lambda r: value_at(r.player_id) or -1)

        for p in sq["players"]:
            fw, sw = words(p["name"]), words(p["short"])
            hit, how = pick([r for r in cands if r.w == fw]), "exact"
            if hit is None:
                hit, how = pick([r for r in cands if r.w and fw and (set(fw) <= set(r.w) or set(r.w) <= set(fw))]), "words"
            if hit is None and sw:
                hit, how = pick([r for r in cands if r.w == sw or (isinstance(r.last_name, str) and words(r.last_name) == sw)]), "short"
            if p["id"] in REVIEWED_IDS:
                player_id = REVIEWED_IDS[p["id"]]
                hit = None if player_id is None else next(r for r in cands if r.player_id == player_id)
                how = "reviewed"
            if hit is None:
                how = ""
            value = None if hit is None else value_at(hit.player_id)
            pos = POS.get(p["position"]) or (TM_POS.get(hit.position) if hit is not None else None) or "?"
            rows.append({"year": sq["year"], "code": sq["code"], "team": sq["team"],
                         "fifa_name": p["name"], "position": pos,
                         "tm_id": None if hit is None else hit.player_id,
                         "tm_name": None if hit is None else hit.name, "match": how,
                         "value_m": value})

    df = pd.DataFrame(rows)
    assigned = df.dropna(subset=["tm_id"])
    if assigned.duplicated(["year", "tm_id"]).any():
        raise ValueError("A Transfermarkt player is assigned twice in the same World Cup")
    df.to_csv(CLEAN / "players.csv", index=False)

    out = []
    for (y, c), g in df.groupby(["year", "code"]):
        r = {"year": y, "code": c, "team": g.team.iloc[0], "players": len(g),
             "matched": int(g.tm_id.notna().sum()), "valued": int(g.value_m.notna().sum())}
        for k in ["GK", "DF", "MF", "FW"]:
            r[f"{k}_m"] = round(g.loc[g.position == k, "value_m"].sum(), 1)
            r[f"{k}_top_m"] = round(g.loc[g.position == k, "value_m"].max() or 0, 1)
        r["sum_m"] = round(g.value_m.sum(), 1)
        r["published_m"] = published.get((y, c))
        r["coverage"] = round(r["sum_m"] / r["published_m"], 2) if r["published_m"] else None
        t = teams.loc[(y, c)] if (y, c) in teams.index else None
        r["stage"] = None if t is None else t["stage"]
        r["stage_n"] = None if t is None else t["stage_n"]
        r["value_rank"] = None if t is None else t["value_rank"]
        out.append(r)
    sp = pd.DataFrame(out)
    sp.to_csv(CLEAN / "squad_positions.csv", index=False)

    print(f"players {len(df)}, matched {df.tm_id.notna().mean():.0%}, valued {df.value_m.notna().mean():.0%}")
    print(sp.groupby("year")[["valued", "players", "coverage"]].agg({"valued": "sum", "players": "sum", "coverage": "median"}))


if __name__ == "__main__":
    main()
