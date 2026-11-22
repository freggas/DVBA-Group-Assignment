# Daten und Analyse (Team 14, Road to 2030)

**Start here:** `Team14_Analysis.ipynb` (runs every step and prints all slide numbers).

| Step | Script | What it does |
|---|---|---|
| 1 | `scripts/01_fetch.py` | Downloads raw data (FIFA match API, published squad-value tables). Already done. |
| 2–4 | `02_squad_values.py` … `04_analysis.py` | Squad values 2006–2026, team and match tables, results by value band, shoot-outs |
| 6 | `06_fetch_squads.py` | FIFA squad lists with positions, 208 squads 2006–2026. Already done. |
| 7 | `07_player_values.py` | Matches 4,972 players to Transfermarkt value history (dcaribou transfermarkt-datasets) → value per line |
| 8 | `08_story_numbers.py` | All numbers on the slides → `data/clean/story_numbers.txt` |

Run any script from this folder with `python3 -I scripts/<name>.py`.
Main outputs in `data/clean/`: `teams.csv`, `matches.csv`, `players.csv`, `squad_positions.csv`, `history_results.txt`, `story_numbers.txt`.
Caveat: player values cover 81–99 % of top-10 squad value from 2010, only about half in 2006, so the position analysis starts in 2010.
