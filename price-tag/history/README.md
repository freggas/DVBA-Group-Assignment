# Team 14: Road to 2030 (Portugal), data and analysis

Data Visualization for Business Analytics, Nova SBE, 2026. Companion to the Executive Brief and the deck.

**Start here:** open `Team14_Appendix.html` in a browser. It shows every step, every table and every chart with its output. The same page is online at https://felixl44.github.io/team14-appendix/.

To rerun it: open `Team14_Appendix.ipynb` from this folder with Python 3 (pandas, SciPy, matplotlib, Jupyter) and run all cells. Each cell asserts the numbers shown on the slides, so the notebook stops if anything changes.

## Sources (as in Appendix B of the Executive Brief)

| ID | Dataset | Folder |
|---|---|---|
| S1 | World Cup matches and squad lists 2006–2026, FIFA API | `data/raw/fifa_api`, `data/raw/fifa_squads` |
| S2 | FIFA World Cup 2026, 48 teams dataset (Kaggle, Khayal Mammadov) | `data/raw/khayalmammadov` |
| S3 | transfermarkt-datasets (David Cariboo, dcaribou) | `data/raw/transfermarkt_dcaribou` |
| S4 | Squad market values 2006–2022 in published studies | `data/raw/squad_value_sources` |
| check data | Kaggle mann14, "2026 FIFA World Cup", only for the data checks | `data/raw/mann14` |

## Scripts

| Step | Script | What it does |
|---|---|---|
| 1 | `scripts/01_fetch.py` | Downloads raw data (FIFA match API, published squad-value tables). Already done. |
| 2 | `scripts/02_squad_values.py` | Squad values 2006–2026 |
| 3 | `scripts/03_build_tables.py` | Team and match tables |
| 4 | `scripts/04_analysis.py` | Results by value band, the €500m line, knockouts and shoot-outs |
| 5 | `scripts/05_investment_check.py` | Side check, not used in the deck |
| 6 | `scripts/06_fetch_squads.py` | FIFA squad lists with positions, 208 squads. Already done. |
| 7 | `scripts/07_player_values.py` | Matches 4,972 players to Transfermarkt value histories, value per line |
| 8 | `scripts/08_story_numbers.py` | All numbers on the slides, written to `data/clean/story_numbers.txt` |

Run any script from this folder with `python3 -I scripts/<name>.py`. The clean tables are in `data/clean/`.
