"""Step 2: read the squad market values out of the published sources.

Run:  python3 -I analysis/02_squad_values.py

Output: data/clean/squad_values.csv  (year, code, team_in_source, value_m, source, page)

Every value is parsed from the downloaded file, not typed in by hand. The script stops
if a source does not give exactly one value for each of the 32 (2026: 48) teams that
the FIFA API lists for that edition.
"""
import csv
import html
import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "raw" / "squad_value_sources"
OUT = ROOT / "data" / "clean"
KHAYAL_2026 = ROOT.parent / "data" / "raw" / "khayalmammadov" / "World Cup 2026.csv"

# Team names as the sources write them (English and German) -> FIFA code
NAME_TO_CODE = {
    "Algeria": "ALG", "Algerien": "ALG", "Angola": "ANG", "Argentina": "ARG", "Argentinien": "ARG",
    "Australia": "AUS", "Australien": "AUS", "Austria": "AUT", "Belgium": "BEL", "Belgien": "BEL",
    "Bosnia": "BIH", "Bosnia & Herz.": "BIH", "Brazil": "BRA", "Brasilien": "BRA",
    "Cameroon": "CMR", "Canada": "CAN", "Cape Verde": "CPV", "Chile": "CHI", "Colombia": "COL",
    "Kolumbien": "COL", "Costa Rica": "CRC", "Cote d'Ivoire": "CIV", "Ivory Coast": "CIV",
    "Croatia": "CRO", "Kroatien": "CRO", "Curacao": "CUW", "Czech Republic": "CZE", "Czechia": "CZE",
    "Denmark": "DEN", "Dänemark": "DEN", "DR Congo": "COD", "Ecuador": "ECU", "Egypt": "EGY",
    "Ägypten": "EGY", "England": "ENG", "France": "FRA", "Frankreich": "FRA", "Germany": "GER",
    "Deutschland": "GER", "Ghana": "GHA", "Greece": "GRE", "Haiti": "HAI", "Honduras": "HON",
    "Iceland": "ISL", "Island": "ISL", "Iran": "IRN", "Iraq": "IRQ", "Italy": "ITA", "Japan": "JPN",
    "Jordan": "JOR", "Mexico": "MEX", "Mexiko": "MEX", "Morocco": "MAR", "Marokko": "MAR",
    "Netherlands": "NED", "The Netherlands": "NED", "New Zealand": "NZL", "Nigeria": "NGA",
    "North Korea": "PRK", "Norway": "NOR", "Panama": "PAN", "Paraguay": "PAR", "Peru": "PER",
    "Poland": "POL", "Polen": "POL", "Portugal": "POR", "Qatar": "QAT", "Russia": "RUS",
    "Russland": "RUS", "Saudi Arabia": "KSA", "Saudi-Arabien": "KSA", "Scotland": "SCO",
    "Senegal": "SEN", "Serbia": "SRB", "Serbien": "SRB", "Serbia and Montenegro": "SCG",
    "Slovakia": "SVK", "Slovenia": "SVN", "South Africa": "RSA", "South Korea": "KOR",
    "Südkorea": "KOR", "Spain": "ESP", "Spanien": "ESP", "Sweden": "SWE", "Schweden": "SWE",
    "Switzerland": "SUI", "Schweiz": "SUI", "Togo": "TOG", "Trinidad and Tobago": "TRI",
    "Tunisia": "TUN", "Tunesien": "TUN", "Turkiye": "TUR", "Ukraine": "UKR", "United States": "USA",
    "USA": "USA", "Uruguay": "URU", "Uzbekistan": "UZB", "Wales": "WAL",
}


def pdf_pages(name):
    return [p.extract_text() or "" for p in PdfReader(SRC / name).pages]


def num(s):
    """'98,9' -> 98.9 ; '1,08' -> 1.08 ; '281' -> 281.0"""
    return float(s.replace(".", "").replace(",", ".")) if "," in s else float(s)


def parse_2006():
    # Baur & Lehmann (2007), Table 2, page 10: "Nation Home Imports Exports Value in million Euro"
    name, page = "2006_baur_lehmann.pdf", 10
    text = pdf_pages(name)[page - 1]
    text = text.replace("Serbia and \nMontenegro \n", "Serbia and Montenegro ")
    rows = re.findall(r"^([A-Z][A-Za-z' ]+?)\s+\d+ \d+ \d+ ([\d,]+)\s*$", text, re.M)
    return [(t.strip(), num(v), name, page) for t, v in rows]


def parse_2010():
    # Gerhards & Wagner (2010), Table 1, page 7: "National team  Ø Market value  Total value"
    name, page = "2010_gerhards_wagner.pdf", 7
    text = pdf_pages(name)[page - 1]
    rows = re.findall(r"^([A-Z][A-Za-z ]+?) [\d,]+ € ([\d,]+) €", text, re.M)
    return [(t.strip(), int(v.replace(",", "")) / 1e6, name, page) for t, v in rows]


def parse_2014():
    # ING Cup-o-nomics (June 2014), ranking table, page 4. Two columns per line; the PDF
    # breaks "Netherlands" and "Switzerland" over two lines, so join those first.
    name, page = "2014_ing_cuponomics.pdf", 4
    text = pdf_pages(name)[page - 1]
    text = text.replace("Netherland\ns\n", "Netherlands ").replace("Switzerlan\nd\n", "Switzerland ")
    rows = re.findall(r"(?:^|\s)\d{1,2} ([A-Z][A-Za-z ]+?) €\s?(\d+)\s?million", text, re.M)
    return [(t.strip(), float(v), name, page) for t, v in rows]


def parse_2018():
    # DIW aktuell 12 (14 June 2018), Tabelle 1, page 4. Transfermarkt, as of 13 June 2018.
    name, page = "2018_diw_aktuell_12.pdf", 4
    text = pdf_pages(name)[page - 1]
    rows = re.findall(r"^\s*([A-ZÄÖÜ][\wäöüÄÖÜ\- ]+?)\s+\d\d,\d\s+([\d,]+) (Mrd|Mio)\.", text, re.M)
    return [(t.strip(), num(v) * (1000 if unit == "Mrd" else 1), name, page) for t, v, unit in rows]


def parse_2022():
    # Planet Football, "Ranking every 2022 World Cup squad by transfer value" (16 Nov 2022),
    # values from Transfermarkt. Each team is "<rank>. <Team> – €<x>million|billion".
    name = "2022_planetfootball.html"
    raw = (SRC / name).read_text(encoding="utf-8")
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S)
    lines = [l.strip() for l in html.unescape(re.sub(r"<[^>]+>", "\n", raw)).split("\n") if l.strip()]
    text = " ".join(lines).replace("\xa0", " ")
    rows = re.findall(r"\b\d{1,2}\. ([A-Z][A-Za-z ]+?) – ?€([\d.]+) ?(million|billion)", text)
    return [(t.strip(), float(v) * (1000 if u == "billion" else 1), name, "")
            for t, v, u in rows]


def parse_2026():
    # Project data set (Kaggle, khayalmammadov), column "Squad Market Value (€m)", Transfermarkt.
    with open(KHAYAL_2026, encoding="utf-8-sig") as f:
        return [(r["Team"], float(r["Squad Market Value (€m)"]), "khayalmammadov/World Cup 2026.csv", "")
                for r in csv.DictReader(f)]


def fifa_codes(year):
    res = json.loads((ROOT / "data" / "raw" / "fifa_api" / f"matches_{year}.json").read_text())["Results"]
    return {t["IdCountry"] for m in res for t in (m["Home"], m["Away"]) if t}


def main():
    parsers = {2006: parse_2006, 2010: parse_2010, 2014: parse_2014, 2018: parse_2018,
               2022: parse_2022, 2026: parse_2026}
    out = []
    for year, parse in parsers.items():
        rows = parse()
        codes = [NAME_TO_CODE[t] for t, *_ in rows]
        expected = fifa_codes(year)
        missing, extra = expected - set(codes), set(codes) - expected
        dupes = {c for c in codes if codes.count(c) > 1}
        assert not (missing or extra or dupes), f"{year}: missing {missing} extra {extra} dupes {dupes}"
        for (team, value, src, page), code in zip(rows, codes):
            out.append({"year": year, "code": code, "team_in_source": team,
                        "value_m": round(value, 2), "source": src, "page": page})
        print(f"{year}: {len(rows)} teams, total €{sum(r[1] for r in rows):,.0f}m, "
              f"top {max(rows, key=lambda r: r[1])[0]} €{max(r[1] for r in rows):,.0f}m")

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "squad_values.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(f"wrote data/clean/squad_values.csv ({len(out)} rows)")


if __name__ == "__main__":
    main()
