# DVBA 2026 · Team 14 · Road to the 2030 World Cup

Board briefing for the Portuguese Football Federation: Portugal has had a top-10 squad by market value at six World Cups (2006–2026) but has never reached a final. What separates finalists, and what should Portugal do before 2030?

- **Deck:** `DVBA_Team14_final_presentation.pptx`
- **Appendix (every number and chart in the deck, with sources):** `price-tag/history/Team14_Analysis.ipynb`, also as `Team14_Analysis.html` (open it in a browser, no Python needed)
- **Scripts and data:** `price-tag/history/` (see its README)

## Reproduce

```bash
git clone https://github.com/freggas/DVBA-Group-Assignment.git && cd DVBA-Group-Assignment
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd price-tag/history
../../.venv/bin/python -m nbconvert --to notebook --execute --inplace Team14_Analysis.ipynb
../../.venv/bin/python -m nbconvert --to html Team14_Analysis.ipynb
```

All raw data is in `price-tag/history/data/raw/`, so no download is needed.
