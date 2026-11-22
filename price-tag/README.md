# The Price Tag: interactive board dashboard (Emre's version)

A second, independent take on Challenge C. It lives only on the branch `emre/price-tag-dashboard` and does not change anything on `main`.

**Question:** Does money decide who wins the World Cup? Or can a cheaper squad beat its price tag?
**Answer:** About half. Squad value buys a place in the knockouts; penalties and the last rounds are where it stops working.

## What it is

One web page (`dashboard/index.html`):

1. **Executive summary + dashboard** at the top: question, answer, four KPIs, three recommendations, and an explorable chart of all 48 squads (filter by confederation, value-split slider, team search, click a squad for its matches).
2. **The story** below, one chapter per screen: stakes (prize money), what drives results, the €900m line, who beat the money, penalties, recommendation, method.
3. **Present mode**: the orange *Present* button (or `P`) scrolls through the chapters on its own. `→`/`←` next/previous, `Space` pause, `Esc` stop.

## Open it

```bash
cd price-tag/dashboard && python3 -m http.server 8766
```
Then open http://127.0.0.1:8766.

## Rebuild the numbers

```bash
cd price-tag
python3 -I analysis/01_clean_merge.py
python3 -I analysis/02_analysis.py
python3 -I analysis/03_story_numbers.py
python3 -I analysis/04_dashboard_data.py   # writes dashboard/data.js, checks the headline counts
```

Data: Kaggle `mann14/2026-fifa-world-cup` (all 104 matches) and `khayalmammadov/fifa-world-cup-2026-48-teams-dataset` (Transfermarkt squad values, FIFA ranking, bookmaker odds, April 2026). Prize money: FIFA Council (Dec 2025, Apr 2026).

AI use: built with Claude Code (Anthropic); the team reviews every number before submission.
