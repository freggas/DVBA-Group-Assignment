# Presentation context: story, slides and charts

Working document for the 5-minute board pitch and the 15-minute Q&A. It covers what we say, in which order, which chart carries each point, and how we defend it. Numbers come from `docs/results.md`, which `src/analysis.py` regenerates (driver numbers in its "Drivers" section).

Course sources: `DATATHON_BRIEF.md` (Weeks 1–3) and the team's Notion notes for Weeks 3 and 4 ("Six moves that win the boardroom", pre-flight checklist, board roles).

## 1. Format

| | |
|---|---|
| Pitch | 5 minutes, boardroom style. Every second has to earn its place: time it out loud. |
| Q&A | 15 minutes. Any teammate may get any question. |
| When | Week 5 (23–27 Nov), order drawn at random. Upload brief + presentation to Moodle by 23:59 that day. |
| Grading | Insight 30% · Visual design 30% · Storytelling 25% · Recommendation 15% (+ peer evaluation) |
| Medium | `story/index.html`: a website with the key insights; scrolling down slides into a deck for "drivers" and "what to do". |

## 2. The message in one sentence

**Squad value buys a place in the knockouts, not the trophy: below about €500m few teams win a knockout match, but once every remaining squad is rich, value stops separating them.**

## 3. Story arc and timing

Open with the answer, build the evidence, end with the action (Knaflic / Duarte). Problem → evidence → implication → recommendation.

| Time | Part | Story phase | Board question |
|---|---|---|---|
| 0:00–0:30 | Hero: decision problem + headline | Setup | Why does this matter to us? |
| 0:30–2:00 | Key insights (website) | Setup → conflict | 1. What are the key insights? |
| 2:00–3:30 | Drivers (slides) | Conflict | 2. What is driving the results? |
| 3:30–4:45 | Recommendation (slides) | Resolution | 3. What should the Board do next? |
| 4:45–5:00 | The ask: one decision, first step | Call to action | |

Audience: Board of a mid-market federation (squad value about €200–500m, e.g. Austria, Scotland, Ghana, Algeria). See `docs/decisions.md` §1.

## 4. Part 1: Key insights (built, `story/index.html`)

| Element | Title (the finding) | Evidence |
|---|---|---|
| Hero | Squad value buys a place in the knockouts, not the trophy | KPIs: 72 of 80 decided matches won by the richer squad (90%); 27/32 top-value squads reached the Round of 32; 4/8 reached the QF; 6/10 close knockout ties |
| Chart 01 | Below €500m, 4 of 30 squads won a knockout match; above it, 12 of 18 did | Scatter: value (log) × stage reached, coloured by stage vs value-expectation |
| Chart 02 | Value secures the knockouts, not the late rounds | Top-k hit rates: 27/32 → 11/16 → 4/8 (top 4, 2, 1 are tiny samples) |

Speaker line: "Value is a reliable floor. The question is what happens above the floor."

## 5. Part 2: What is driving the results (built, `story/index.html`)

Two slides in the pitch, one backup for the Q&A.

### Slide 2.1: At the top, everyone is rich, so value stops deciding

- **Title:** By the semi-finals, opponents were within 1.3× of each other in value, and the richer squad lost both.
- **Chart:** every knockout tie as a dot on a log value-gap axis, one row per round, coloured by which side went through, with the median gap as a tick and "richer squad went through" counted per round (R32 14/16, R16 6/8, QF 4/4, SF 0/2, F 1/1).
- **Supporting numbers:**
  - Ties within 1.5× in value: the richer side went through in 6 of 10 (a coin flip).
  - 68% of knockout matches ended level or by one goal, vs 53% of group matches.
- **Honest caveat:** the median gap does not fall monotonically (R32 2.7×, R16 1.5×, QF 2.0×, SF/F 1.3×), and there are only 2 semi-finals and 1 final. Show the round values, do not draw a trend line.
- **Speaker line:** "Value gets you into the room. Once everyone in the room is rich, small margins decide."

### Slide 2.2: Who beat the value expectation, and who did not

- **Title:** African squads and the three hosts went further than their value predicted; Europe’s squads fell short on average.
- **Chart:** one row per confederation (+ hosts), each squad a dot at its stage-vs-expected value (−2 to +2), with the group average as a navy tick. Blue = beat expectation, orange = fell short, grey = as predicted (same colours as the website).
- **Supporting numbers:**
  - CAF net +5 stages across 10 teams (mean +0.5).
  - Hosts: all 3 reached the Round of 16; USA and Canada +1, Mexico as predicted (mean +0.67, n = 3).
  - UEFA net −5 across 16 teams (France, Germany, Netherlands, Türkiye each −2).
  - Over-performers: Argentina, Switzerland, Paraguay +2; Morocco, Norway, Belgium, Egypt +1.
- **Honest caveat:** small groups. Home advantage is confounded. 8 of 32 Round-of-32 places went to the best third-placed teams, so the draw matters. Treat this as a signal, not a finding.

### Backup slide 2.3 (Q&A): "Undervalued" alone did not predict over-performance

The challenge asks whether undervalued federations outperformed.

- teams the market values lower than their FIFA ranking ("undervalued") did **not** beat the value expectation more often (Spearman ρ = 0.11, p = 0.46; the 9 most undervalued averaged +0.1 stages).
- Over-performance is not explained by a cheap-but-strong squad that the market missed. It points to things outside our data (coaching, cohesion, the draw, home advantage).
- Simpson check: within UEFA alone, value and stage still correlate at ρ = 0.72 (n = 16), the same as overall. The headline is not an artefact of confederation mix.
- Group draw: a squad's value relative to its group opponents predicts reaching the Round of 32 (ρ = 0.56). Group difficulty does not explain who beat expectation (ρ = −0.08).

## 6. Part 3: What should the Board do next (built, `story/index.html`)

### Slide 3.1: one slide, three actions, one ask

- **Title:** Target a €500m squad by 2030: it turns the Round of 16 from a long shot (10%) into a realistic goal (41%).
- **Chart:** modelled P(reach stage) by squad value (logistic regression, log x-axis). Round of 16 in blue with its 95% confidence band; Round of 32 and quarter-final in grey for context. The €200–500m band is shaded "You are here"; €250m and €500m are marked on the Round-of-16 curve. Hovering shows all three probabilities at any value.
- **Actions** (each with impact and owner):
  1. **Set a squad-value target of about €500m by 2030.** Round of 16: 10% at €250m → 41% at €500m (95% interval 23–59%). Route: a player pathway into top leagues. *Owner:* sporting director.
  2. **Judge the team and coach against a value-adjusted expectation.** At €250m the Round of 32 is par (64%), the Round of 16 a bonus (10%). *Owner:* Board, at each tournament review.
  3. **Study the squads that won a knockout match on less than €500m.** Only 4 of 30 did: Switzerland (QF), Canada (R16, host), Egypt and Paraguay (R16). *Owner:* technical director. (This replaces the earlier list "Switzerland, Paraguay, Morocco, Norway": Morocco and Norway are above €500m, so they are not peers of a mid-market federation.)
- **The ask:** approve the €500m target and a value-adjusted scorecard today. First step: the sporting director maps where the current squad plays and returns a pathway plan within 90 days. The owners and the 90 days are our proposal, not something the data says.
- **Caveat on the slide:** one tournament, association not cause, wide interval. Value is a proxy, not a lever. That a player pathway raises it is an assumption.
- **Be ready for:** "41% is still below 50%." Yes. €500m makes the Round of 16 realistic, not likely. Value rank alone would still place a €500m squad (about #19) in the Round of 32.
- **Speaker line:** "Value is not the trophy, but it is the ticket. At €250m the Round of 16 is a lottery; at €500m it is a plan."

## 7. Chart rules (course + our design system)

- **Title = the finding**, not the topic. Readers scan headings first (layer-cake pattern).
- **One message per visual.** Cut anything that does not serve it.
- **Colour:** white background, navy ink, one bright blue accent. Diverging scale for "vs expectation": blue (beat) / grey (as predicted) / orange (fell short). No red/green. Never colour alone: use a legend plus direct labels.
- **Position and length** for comparisons. Area only for composition.
- **Honest scales:** bars start at zero. The log scale for value is disclosed on the axis. Show n and denominators ("27 of 32", not just "84%").
- **Uncertainty visible:** small-n rounds are flagged in the chart, not only in the footnote.
- **Three-second test:** each chart shows its point at a glance, and the numbers can be checked on inspection.
- **Association ≠ causation**, stated on the slide where the recommendation relies on it.

## 8. Q&A preparation (board roles)

| Role | Likely question | Our answer |
|---|---|---|
| CEO | What decision do you want from us? | Adopt €500m squad value by 2030 as the planning target and evaluate the team against value-adjusted expectations. |
| CFO | Do the numbers reconcile? | Stage counts are asserted to be 48/32/16/8/4/2/1; every headline number has its denominator in `docs/results.md`; the stage is derived from the match list (the South Africa label fix). |
| Operations | What would we actually change? | The player pathway into top-5 leagues, the youth set-up and how we set targets. Owner: sporting director. *Constraint:* value follows player development with a lag of years. |
| Evidence challenger | What else could explain this? | FIFA ranking and odds explain about as much as value (ρ 0.64–0.74, overlapping CIs). One tournament, n = 48. Hosts and the draw matter. "Undervalued" did not predict over-performance (backup 2.3). |

## 9. Pre-flight checklist

- [ ] Message stated in one sentence, with the decision it supports
- [ ] Each chart shows its point in three seconds
- [ ] Baselines, units, denominators and caveats are honest
- [ ] Opening sentence rehearsed aloud three times; pause before the ask
- [ ] Timed run under 5:00
- [ ] Every member can explain every chart and the method

## 10. Open items

- [x] Driver numbers (§5) moved into `src/analysis.py`
- [x] Slides 2.1, 2.2 and backup 2.3 built in `story/index.html` (→ / ← keys jump between slides)
- [x] Part 3 slide 3.1 built (curve now has a 95% interval, computed in `src/analysis.py`)
- [ ] Team to confirm the recommendation, owners and the 90-day first step
- [ ] Update `docs/decisions.md` §1 ("Study the over-performers") to the under-€500m peer list
- [ ] Team members, roles and presentation day (`docs/decisions.md` §0)
