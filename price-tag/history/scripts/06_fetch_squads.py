"""Step 6: download the World Cup squads 2006-2026 with each player's position.

Run:  python3 -I scripts/06_fetch_squads.py   (from the "03 Daten und Analyse" folder)

For every team at every World Cup since 2006, the FIFA live-match API lists the full
registered squad (23 to 26 players) with a position code for each player:
0 = goalkeeper, 1 = defender, 2 = midfielder, 3 = forward.
We take each team's first match of the tournament.

Output: data/raw/fifa_squads/squad_<year>_<team code>.json  (raw, unchanged)
"""
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = RAW / "fifa_squads"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
API = "https://api.fifa.com/api/v3/live/football"
YEARS = [2006, 2010, 2014, 2018, 2022, 2026]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for year in YEARS:
        matches = json.loads((RAW / "fifa_api" / f"matches_{year}.json").read_text())["Results"]
        matches.sort(key=lambda m: m["Date"])
        first = {}
        for m in matches:
            for side in ("Home", "Away"):
                t = m.get(side) or {}
                code = t.get("Abbreviation")
                if code and code not in first:
                    first[code] = m
        for code, m in sorted(first.items()):
            dest = OUT / f"squad_{year}_{code}.json"
            if dest.exists():
                continue
            url = f"{API}/{m['IdCompetition']}/{m['IdSeason']}/{m['IdStage']}/{m['IdMatch']}?language=en"
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read())
            side = "HomeTeam" if d["HomeTeam"]["Abbreviation"] == code else "AwayTeam"
            team = d[side]
            out = {"year": year, "code": code, "match_date": d["Date"],
                   "team": team["TeamName"][0]["Description"],
                   "players": [{"id": p["IdPlayer"],
                                "name": p["PlayerName"][0]["Description"],
                                "short": (p.get("ShortName") or [{}])[0].get("Description", ""),
                                "position": p["Position"]} for p in team["Players"]]}
            dest.write_text(json.dumps(out, ensure_ascii=False, indent=1))
            print(f"  got {year} {code}: {len(out['players'])} players")
            time.sleep(0.3)


if __name__ == "__main__":
    main()
