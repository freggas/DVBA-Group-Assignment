"""Step 1: download every raw input once and keep it unchanged in data/raw/.

Run:  python3 -I analysis/01_fetch.py          (from the history/ folder)
      python3 -I analysis/01_fetch.py --force  (download again)

Downloads
  data/raw/fifa_api/seasons.json             all men's World Cups (idCompetition 17)
  data/raw/fifa_api/matches_<year>.json      every match of that edition (FIFA calendar API)
  data/raw/squad_value_sources/*             the published squad-value tables (see SOURCES)
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
FORCE = "--force" in sys.argv
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"

API = "https://api.fifa.com/api/v3"

# Published squad-value tables. All of them are based on Transfermarkt market values
# taken just before the tournament (2006: published afterwards, see README).
SOURCES = {
    "2006_baur_lehmann.pdf": "https://www.tcd.ie/triss/assets/PDFs/iiis/iiisdp217.pdf",
    "2010_gerhards_wagner.pdf": "https://www.polsoz.fu-berlin.de/en/soziologie/arbeitsbereiche/seniorprofessur/mitarbeiter/lehrstuhlinhaber/dateien/research_note_36_money_vs_chance_06_10.pdf",
    "2014_ing_cuponomics.pdf": "https://think.ing.com/uploads/reports/IIS_cuponomics_special_report_2014.pdf",
    "2018_diw_aktuell_12.pdf": "https://www.diw.de/documents/publikationen/73/diw_01.c.591704.de/diw_aktuell_12.pdf",
    "2022_planetfootball.html": "https://www.planetfootball.com/quick-reads/ranking-every-2022-world-cup-squad-by-transfer-value-england-brazil",
}


def get(url: str, dest: Path) -> None:
    if dest.exists() and not FORCE:
        print(f"  have {dest.relative_to(ROOT)}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=90) as r:
        dest.write_bytes(r.read())
    print(f"  got  {dest.relative_to(ROOT)} ({dest.stat().st_size:,} bytes)")
    time.sleep(1)


def main() -> None:
    print("FIFA API: seasons")
    seasons_file = RAW / "fifa_api" / "seasons.json"
    get(f"{API}/seasons?idCompetition=17&count=100&language=en", seasons_file)
    seasons = json.loads(seasons_file.read_text())["Results"]

    print("FIFA API: matches per edition")
    for s in seasons:
        year = int(s["StartDate"][:4])
        get(f"{API}/calendar/matches?idCompetition=17&idSeason={s['IdSeason']}&count=500&language=en",
            RAW / "fifa_api" / f"matches_{year}.json")

    print("Squad-value sources")
    for name, url in SOURCES.items():
        get(url, RAW / "squad_value_sources" / name)


if __name__ == "__main__":
    main()
