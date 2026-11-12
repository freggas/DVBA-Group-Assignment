# DVBA 2026 · Team 14 · Datathon Challenge C

**Question:** To what extent does a squad's market value dictate World Cup 2026 progression, and did "undervalued" federations outperform?

**Live dashboard:** https://claude.ai/artifact/MR15HuQCyxA7ERqDgLaEbg (private until shared from the page's Share menu)

## Reproduce

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python src/build_dataset.py   # raw → data/processed/teams.csv, matches.csv
.venv/bin/python src/analysis.py        # → dashboard/data.js, docs/results.md, *_metrics.csv
open dashboard/index.html               # local preview
```

## Where things are

- `DATATHON_BRIEF.md`: the assignment brief
- `docs/decisions.md`: decision contract, data prep, hypotheses, limitations, AI-use log (**read this first**)
- `docs/results.md`: every headline number with its denominator (generated)
- `data/raw/`: original Kaggle downloads, untouched
- `dashboard/`: the executive visualization (`index.html` + generated `data.js`)
- `brief/`, `slides/`: to do
