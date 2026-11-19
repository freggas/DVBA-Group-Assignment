# World Cup history 1930–2026: squad value vs result

Extends the 2026 analysis to earlier World Cups. Every number in `data/clean/history_results.txt` and `data/clean/investment_results.txt` comes from these scripts, run in order from this folder:

```
python3 -I analysis/01_fetch.py            # downloads raw data (once; --force to refresh)
python3 -I analysis/02_squad_values.py     # parses squad values from the published tables
python3 -I analysis/03_build_tables.py     # builds teams.csv and matches.csv
python3 -I analysis/04_analysis.py         # results: rounds, price bands, €500m line, matches, shoot-outs
python3 -I analysis/05_investment_check.py # FIFA development money vs squad value
```
Needs only Python 3 and `pypdf`.

## Data and sources
| What | Years | Source |
|---|---|---|
| All matches, scores, extra time, shoot-outs | 1930–2026 (23 World Cups, 1,068 matches) | FIFA API `api.fifa.com/api/v3/calendar/matches`, competition 17 |
| Squad market value 2006 | 32 teams | Baur & Lehmann, TCD IIIS DP 217, Table 2 p. 10 (Transfermarkt data; published after the tournament) |
| 2010 | 32 | Gerhards & Wagner, FU Berlin Research Note 36, Table 1 p. 7 (Transfermarkt, 27 May 2010) |
| 2014 | 32 | ING "Cup-o-nomics", p. 4 (2 June 2014; squads not final yet, 23-player estimates) |
| 2018 | 32 | DIW aktuell 12, Tabelle 1 p. 4 (Transfermarkt, 13 June 2018) |
| 2022 | 32 | Planet Football, 16 Nov 2022 (Transfermarkt; article edited since) |
| 2026 | 48 | project data set `../data/raw/khayalmammadov` (Transfermarkt) |
| FIFA development money per association | 211 associations | FIFA Forward impact map (`ipt.fifa.com`), data embedded in the page |

Checks built into the scripts: each value table must yield exactly the teams the FIFA API lists for that year; every match without a winner must be level; every shoot-out must be level after extra time. Two cross-checks done by hand on 19 Nov 2026: all 160 values 2006–2022 equal the ones in an earlier, uncommitted collection (`data/historical_world_cups/teams.csv`, local only, not in the repo), and the 2026 rounds and wins from the FIFA API equal `../data/clean/teams_merged.csv` for all 48 teams.

No squad values before 2006: Transfermarkt does not publish historical team values for old tournaments (its participant pages always show today's values), and no sourced table was found.

## Outputs (`data/clean/`)
- `teams.csv`: one row per team per World Cup: furthest round (`stage`), W/D/L, goals, shoot-out wins and losses, value, value rank in that edition, value vs median.
- `matches.csv`: one row per match: shoot-out flag (`result_type` 2), richer squad, value gap, result for the richer squad.
- `rounds_by_value_band.csv`: chart-ready table for the price-band chart.
- `fifa_forward_by_association.csv`: FIFA Forward entitlement and commitments, 211 associations.
- `history_results.txt`, `investment_results.txt`: all results as text.

## Can we say "invest X to reach a €500m squad"? Not with available data
- **Squad value is not federation spending.** It is the sum of Transfermarkt values of players whose clubs trained and pay them. Federations do not buy players.
- **FIFA's own development money is flat:** every association is entitled to $17.75–20.65m (1.16x spread) while 2026 squad values differ 40x. Rank correlation with 2026 squad value: −0.02. This money cannot explain squad value. FIFA does not say on the map which years the amounts cover.
- **UEFA HatTrick is flat too:** €5m one-off plus €3m a year for each of the 55 associations (UEFA budget 2023/24).
- **Associations' own budgets** (youth academies, coaching) are published only in each association's annual report, in different currencies, years and categories, and many do not publish at all. No comparable data set across the 48 teams exists that we could find. A few case studies would be possible (e.g. Canada's accounts, already in the repo folder), but not a "€ in → € squad value out" curve.
- What the data does support: the descriptive link between squad value rank and how far a team gets (see `history_results.txt`).
