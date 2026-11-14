# Decisions log: Team 14, Challenge C (World Cup 2026: squad value vs progression)

Living document. It records the decision contract, data preparation, hypotheses tested, assumptions, limitations and AI use. All numbers come from `docs/results.md`, which `src/analysis.py` regenerates.

## 0. Open team decisions

- Team members and roles: `TODO`
- Presentation day (Week 5, 23–27 Nov): `TODO`
- Board framing (section 1): Claude proposed the one below. Confirm it or change it as a team.

## 1. Decision contract (Week 1 template)

| Element | Our answer |
|---|---|
| Audience | Board of Directors of a mid-market national football federation (squad value roughly €200–500m, e.g. Austria, Scotland, Ghana, Algeria). |
| Decision | Where to put long-term investment to improve World Cup results by 2030: raise squad market value (a pathway that gets players into top leagues), or rely on other levers. Plus how to set and judge tournament targets. |
| Question | To what extent does squad market value dictate tournament progression, and who beat the expectation that value sets? |
| Comparison | Stage each team reached vs. the stage its value rank predicts (k-th most valuable squad is expected to reach the k-th best finish). Match by match: did the more valuable squad win? |
| Measure and baseline | Stage reached (1 = group stage … 7 = champion). Baseline is the value-only expectation, with FIFA ranking and bookmaker odds as alternative baselines. |
| Qualification that stays visible | One tournament, 48 teams: this shows association, not cause. Market value is a proxy for player quality, not a lever you can pull directly. |
| Action under consideration | Set a squad-value target of about €500m by 2030, and judge the team and coach against value-adjusted expectations. |

### Story in one sentence

Squad value buys a place in the knockouts, not the trophy: below about €500m, few teams win a knockout match, but once every remaining squad is rich, value stops separating them.

### Three board questions

1. **Key insights.** The more valuable squad won 72 of 80 decided matches (90%), and 27 of the 32 most valuable squads reached the Round of 32. Only 4 of the 8 most valuable reached the quarter-finals.
2. **What drives the results.** The value gap between opponents shrinks round by round: the median is 2.7× in the Round of 32 and 1.3× in the semi-finals and final. Where squads were within 1.5× of each other in value, the more valuable side went through in only 6 of 10 knockout ties.
3. **What the Board should do.**
   - Treat about €500m as the threshold. In the model, P(Round of 16) rises from 10% at €250m to 41% at €500m.
   - Judge performance against value-adjusted expectations.
   - Study the over-performers (Switzerland, Paraguay, Morocco, Norway) for the levers that value does not capture.

## 2. Data sources

| Source | Content | Notes |
|---|---|---|
| Kaggle `khayalmammadov/fifa-world-cup-2026-48-teams-dataset` | Pre-tournament data per team: squad market value (€m, attributed to Transfermarkt), FIFA ranking, bookmaker probabilities (attributed to Yahoo Sports), history | Snapshot of April 2026, so it is a true pre-tournament expectation. Values are rounded (to €5–10m). |
| Kaggle `mann14/2026-fifa-world-cup` | All 104 matches with scores, penalties and stage, plus each team's elimination round | Community-compiled. Results spot-checked against press reports on 12 Nov 2026: the final (Spain 1–0 Argentina after extra time), Norway 2–1 Brazil (Round of 16) and Morocco 3–0 Canada (Round of 16) all match. |

Both were downloaded on 12 Nov 2026 into `data/raw/`, which stays untouched.

## 3. Data preparation (`src/build_dataset.py`)

1. Harmonised one team name: `Bosnia & Herz.` → `Bosnia and Herzegovina`. After that, the join covers all 48 teams 1:1 with no missing values, and the group assignments agree between the two sources.
2. **Stage reached is derived from the match list, not from the `eliminated_round` label.** The label says South Africa went out in the group stage, but the match list shows them playing (and losing 1–0) to Canada in the Round of 32. Only the counts derived from the match list reconcile with the format (48/32/16/8/4/2/1). The script asserts this.
3. The third-place match is not counted as a stage. England (won it) and France (lost it) both count as "semi-final".
4. A match result is the score after 90 or 120 minutes; penalty shoot-outs count as draws. Progression in knockout ties uses the actual winner, including shoot-outs.
5. Value rank: 1 = most valuable. Ties (Argentina, Portugal and Germany at €980m; Spain and England at €1,250m) are broken by FIFA ranking.

## 4. Metrics and method (`src/analysis.py`)

- **Value-only expectation.** If value alone decided, the k-th most valuable squad would reach the stage of the k-th best finish: #1 champion, #2 final, #3–4 semi-final, #5–8 quarter-final, #9–16 Round of 16, #17–32 Round of 32, #33–48 group stage. Over/under-performance = stage reached − expected stage (in stages). This needs no fitted model and is easy to explain to a board.
- **Association.** Spearman ρ between stage reached and each predictor, with a bootstrap 95% CI (4,000 resamples, seed 42). Rank correlation is used because stage is ordinal.
- **Value curve.** A logistic regression of "reached stage s" on log(value), fitted separately for the Round of 32, Round of 16 and quarter-final. It is used only to read out an indicative "what does more value buy". n = 48, so the intervals are wide.
- **Match level.** Value gap = richer squad's value ÷ poorer squad's value. Results are tabulated by gap band and by knockout round.

## 5. Hypotheses tested

| # | Hypothesis | Result |
|---|---|---|
| H1 | More valuable squads progress further | Supported: ρ = 0.72 [0.53, 0.85]. |
| H2 | Value predicts better than FIFA ranking or bookmaker odds | Not supported: the three overlap (ρ 0.64–0.74, CIs overlap heavily). In an OLS with both, log FIFA rank carries more weight than log value, and the result depends on the specification. **Do not claim value is the best predictor.** |
| H3 | Value matters less in the later rounds | Supported descriptively: the median gap falls from 2.7× (Round of 32) to 1.3× (semi-final and final), and the more valuable side lost both semi-finals. n is tiny (2 semi-finals). |
| H4 | Hosts beat expectations | All 3 hosts reached the Round of 16: USA and Canada +1 stage vs. value, Mexico exactly as value predicted (mean +0.67). n = 3 and home advantage is confounded, so this is mentioned as context only. |
| H5 | Confederation (CAF, CONCACAF) over-performed | Mean vs. expectation: CAF +0.5, CONCACAF +0.33, UEFA −0.31, AFC −0.22. Small groups; 8 of 32 Round-of-32 places went to "best third-placed" teams, so the group draw matters. Treat as a signal, not a finding. |

To check before we present: Simpson-type reversals within confederations (UEFA alone vs. all teams).

## 6. Assumptions and limitations

- One tournament, n = 48 teams and 104 matches. Knockout results are noisy, so single upsets (Norway over Brazil) carry no statistical weight.
- Market value reflects club-market valuations of players, which mixes ability with age, league exposure and hype. It is a proxy for quality, not a cause you can fund directly.
- The values are a rounded April 2026 snapshot from a community dataset, not checked against Transfermarkt line by line.
- The value-only expectation is mechanical: it ignores how hard each group was and the bracket path.
- Association ≠ causation. The recommendation's "expected impact" comes from a cross-sectional model, not an experiment.

## 7. AI use log (for the methods note)

- 12 Nov 2026: Claude Code (Anthropic, model Claude Opus 5.5) set up the repository, downloaded the data, wrote `src/build_dataset.py` and `src/analysis.py`, drafted this log and built the dashboard (`dashboard/`). The team must review every step and be able to explain it.
