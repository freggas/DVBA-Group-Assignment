"""Step 5: is there country-level data on what associations invest, and does it line up
with squad value?

Run:  python3 -I analysis/05_investment_check.py
Output: data/clean/fifa_forward_by_association.csv, data/clean/investment_results.txt

The only investment figures available for all 211 FIFA member associations in one
consistent format are FIFA's own development payments (FIFA Forward programme). They
come from the data embedded in FIFA's Forward impact map (downloaded in step 1). FIFA
does not say on that page which years the amounts cover; treat them as the cumulative
amounts shown on the download date.

What this is NOT: the association's own budget, government money, or what clubs spend
on academies. Those are not published in a comparable form for many countries (see README).
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "fifa_forward" / "forward_page.html"
CLEAN = ROOT / "data" / "clean"
LINES = []


def say(s=""):
    print(s)
    LINES.append(s)


def spearman(x, y):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    return cov / (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5


def main():
    page = RAW.read_text(encoding="utf-8")
    data = json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', page, re.S).group(1))
    layers = data["props"]["pageProps"]["association"]["pageData"]["fifaForwardProgramme"]["allLayers"]
    rows = []
    for layer in layers:
        for feat in layer.get("features", []):
            p = feat["properties"]
            if p.get("fdcp", {}).get("type") == "Confederation" or p.get("parentId") == "_GENERAL":
                continue
            projects = (p.get("dataTable") or {}).get("dataTableRows") or []
            ent = sum(p.get(k) or 0 for k in ("entitlementOperationalCosts", "entitlementProjects",
                                               "entitlementTravelEquipment"))
            com = ((p.get("committedOperationalCosts") or 0) + (p.get("committedTravelEquipment") or 0)
                   + sum(r.get("commitmentCommitted") or 0 for r in projects))
            rows.append({"code": p["id"], "name": p["fdcp"]["name"], "confederation": p["parentId"],
                         "population": p.get("population") or "",
                         "entitlement_usd": ent, "committed_usd": com, "projects": len(projects)})
    rows.sort(key=lambda r: r["code"])
    with open(CLEAN / "fifa_forward_by_association.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    ents = sorted(r["entitlement_usd"] for r in rows)
    coms = sorted(r["committed_usd"] for r in rows)
    say("FIFA FORWARD DEVELOPMENT MONEY PER ASSOCIATION (USD, FIFA impact map)")
    say(f"  associations: {len(rows)}")
    say(f"  entitlement: min {ents[0]:,} | median {ents[len(ents) // 2]:,} | max {ents[-1]:,}")
    say(f"  richest-funded vs least-funded association: {ents[-1] / ents[0]:.2f}x")
    say(f"  committed:   min {coms[0]:,} | median {coms[len(coms) // 2]:,} | max {coms[-1]:,}")

    vals = {}
    with open(CLEAN / "squad_values.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            vals[(int(r["year"]), r["code"])] = float(r["value_m"])
    fwd = {r["code"]: r for r in rows}
    for year in (2026,):  # amounts are cumulative up to the download date, so only 2026 fits in time
        teams = [(c, v) for (y, c), v in vals.items() if y == year and c in fwd]
        teams.sort(key=lambda cv: -cv[1])
        x = [fwd[c]["committed_usd"] for c, _ in teams]
        y = [v for _, v in teams]
        say(f"\n  World Cup {year}: {len(teams)} teams matched")
        say(f"    squad value, most vs least expensive: {y[0] / y[-1]:.0f}x")
        say(f"    Spearman rank correlation, FIFA Forward money committed vs squad value: "
            f"{spearman(x, y):+.2f}  (0 = no relation)")
        for c, v in teams[:5] + teams[-3:]:
            say(f"    {fwd[c]['name']:22s} squad €{v:7,.0f}m | Forward entitlement "
                f"${fwd[c]['entitlement_usd'] / 1e6:5.2f}m | committed ${fwd[c]['committed_usd'] / 1e6:5.2f}m")
    say("\n  Reading: FIFA pays (almost) every association the same, so this money cannot")
    say("  explain why one squad is worth €1.5bn and another €50m.")
    (CLEAN / "investment_results.txt").write_text("\n".join(LINES) + "\n", encoding="utf-8")
    print("\nwrote data/clean/fifa_forward_by_association.csv and data/clean/investment_results.txt")


if __name__ == "__main__":
    main()
