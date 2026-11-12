# Datathon brief: Executive Data Visualization Challenge

Context file for Claude Code. It summarises the assignment guide, the Moodle course page and the lecture slides (Weeks 1–3) of course 2609, Data Visualization for Business Analytics, Nova SBE, T2 2026/27. Compiled 12 Nov 2026.

## 1. Fill in before starting

These are team decisions that are not on Moodle. Claude Code should ask if they are still empty.

- Challenge chosen (A, B or C, see section 4): `TODO`
- Tool for the visualization (the course does not mandate one; Week 4 covers tools and AI): `TODO`
- Team members and roles: `TODO`
- Our presentation class day in Week 5: `TODO`

## 2. The assignment in one paragraph

We are TXA Team 14, a team of 4–5 acting as a strategic analytics consulting team advising a Board of Directors. We pick one of three datasets, analyse it, build an executive data visualization (dashboard), and deliver a recommendation. The Datathon is 40% of the course grade. There is no single correct answer: the grade reflects the strength of the reasoning, the quality of the visual evidence and the persuasiveness of the recommendation.

The work must answer three board questions:

1. What are the key insights?
2. What is driving the results?
3. What should the Board do next?

## 3. Deliverables and deadlines

| Item | Requirement |
|---|---|
| Executive Brief | One PDF, maximum 5 pages. File name `DVBA2026_Team14_ExecutiveBrief`. |
| Executive Presentation | 5-minute boardroom-style pitch plus Q&A. File name `DVBA2026_Team14_Presentation`. |
| Peer evaluation | Moodle feedback form, open 16 Nov, closes Sun 29 Nov 23:59. |

The brief must contain:

- An accessible link to the executive visualization, or screenshots if a live link cannot be shared.
- A concise summary of the decision problem, key insights, recommendation and expected impact.
- A short methods note: data sources, tools, data preparation, assumptions, transformations, limitations.
- A team contribution statement with each member's role.

The presentation must:

- Define the decision problem and why it matters to the organisation.
- Present the most important insights with their supporting evidence.
- Draw out the strategic implications for senior decision-makers.
- End with a clear, actionable recommendation grounded in the analysis.

Timing:

- All teams must be ready to present in Week 5 (23–27 Nov). The order is drawn at random at the start of class. Presentations run over the last two class sessions (Weeks 5 and 6).
- Both files are uploaded to Moodle by 23:59 on the day of our presentation. One member submits for the team. Moodle's hard due date is Fri 27 Nov 23:59.
- Internal target: everything finished by Sun 22 Nov.
- Q&A length is inconsistent in the sources: the guide says "short Q&A", the Week 1 slides say 15 minutes. Prepare for 15.
- Every member must understand the full analysis and be able to answer questions.

## 4. Challenge options

| | Challenge | Data | Executive question |
|---|---|---|---|
| A | Telecom customer retention and commercial strategy | Telco Customer Churn (customer-level: demographics, services, contracts, tenure, billing, churn). `kaggle.com/datasets/blastchar/telco-customer-churn` | Which customer segments are most at risk of churn, what drives their risk, and where should the company focus its retention investment? |
| B | Population health and risk prioritisation | Our World in Data, Global Health (disease burden, life expectancy, risk factors, health-system indicators by country and year). `ourworldindata.org/global-health` | Which health risks and populations should policymakers prioritise, and where could interventions have the greatest impact? |
| C | Football macroeconomics and tournament progression | 2026 FIFA World Cup (team market values, FIFA rankings, match outcomes, 48 teams). `kaggle.com/datasets/mann14/2026-fifa-world-cup` and `kaggle.com/datasets/khayalmammadov/fifa-world-cup-2026-48-teams-dataset` | To what extent does a squad's market value dictate tournament success, and did "undervalued" federations outperform expectations? |

The datasets are suggested starting points, so adding other sources is allowed. The dataset links were copied from a PDF with line breaks; verify them before downloading.

## 5. Grading

| Criterion | Weight |
|---|---|
| Analytical insight and business reasoning | 30% |
| Data visualization design and communication effectiveness | 30% |
| Executive storytelling and communication | 25% |
| Strategic recommendations and expected impact | 15% |

## 6. Workflow suggested by the guide

1. Understand the business context and define the decision problem.
2. Explore, clean and prepare the data.
3. Identify patterns, anomalies, relationships and possible drivers.
4. Develop, test and refine hypotheses against the evidence.
5. Design an executive visualization that highlights the most relevant insights.
6. Build a data story linking evidence to strategic implications.
7. Formulate practical recommendations supported by the analysis.

## 7. What the course teaches (apply these; the graders will look for them)

### Start from a decision, not from the data (Week 1)

Write a "decision contract" before charting:

- Audience and the decision they must make.
- The question and the comparison that answers it.
- The measure and its baseline.
- The qualification that must stay visible (for example, "this locates the problem, it does not prove the cause").
- The action under consideration.

If the question is about a difference, plot the difference itself (for example actual minus plan), sorted, so the reader does no mental arithmetic.

### Perception and cognitive load (Week 1)

- Use pre-attentive attributes (colour, size, position) to make one thing stand out. Combining too many cues makes search harder.
- Position and length support the most accurate comparisons. Area attracts attention but is read imprecisely.
- Working memory is small: chunk information, label lines and bars directly, avoid remote legends.
- Match colour to data type: distinct hues for categories, a light-to-dark ramp for ordered values, a diverging scale for deviation from a midpoint.
- A chart should work at two speeds: the issue is noticeable at a glance, and the numbers can be verified on inspection.

### Design and integrity (Week 2)

- Gestalt principles: proximity, similarity, enclosure, continuity, connection. Make sure cues do not conflict.
- Data-ink: remove borders, heavy gridlines, redundant legends and decoration, but keep reference points and definitions.
- Selective emphasis: grey for context, one accent colour for the message. The title states the finding, not the topic.
- Accessibility: avoid red/green pairs, never rely on colour alone, check in grayscale.
- Honest scales: bars start at zero, time periods are equal, the time window is not cherry-picked.
- Distinguish level, share and change. Show the denominator. Distinguish totals from rates.
- Averages can hide distributions and subgroup reversals (Simpson's paradox): check segments before claiming an overall effect.
- Correlation is a screen, not a diagnosis. State that association does not establish causation.
- Maps: use them only when location helps explain. Class boundaries change the impression.
- Every chart should make its claim inspectable: claim, scope, measure, comparison, uncertainty.

### Dashboard architecture (Week 3)

- A dashboard is a few coordinated views on one screen that support one decision. State the purpose before the format.
- Structure by progressive disclosure, each level triggered by a reader question:
  1. Overview: what is the status? (KPI plus exception flag)
  2. Comparison: where does it differ? (ranked comparison)
  3. Diagnosis: what might explain it? (driver breakdown)
  4. Evidence: can we verify it? (records, definitions, method)
- Keep the selected scope and period always visible and give a clear route back to the overview.
- Titles and labels must carry the message, because readers scan headings first.
- A KPI tree makes the headline number reconcile with its components.
- Interaction shown in class: filter, select to link views, drill down to evidence.
- The lecturer's own example dashboard title is a finding ("growth is real, Spain is the margin priority"), with KPI cards on top, a ranked bar chart against a target, and a linked scatter plot.

### Storytelling and delivery (Week 3)

- Story arc: setup (baseline), conflict (turning point), resolution (what followed and what to do).
- Duarte's shape: contrast "what is" with "what could be", name the cost of waiting, end on a call to action with the first step.
- Four moves: know the context, choose the view, focus attention, tell the story. Open with the answer, build the evidence, end with the action.
- Output test: one sentence for the message and one chart that shows it in three seconds.
- Pre-flight checklist: message in one sentence with the decision it supports; each chart shows its point in three seconds; baselines, units and caveats are honest; opening, pause and ask are rehearsed.

### Questions the board will ask (rehearse answers)

- CEO: what decision do you want from us? (one recommendation and its consequence)
- CFO: do the totals and ratios reconcile? (definitions, scope, verified calculations)
- Operations: what would we actually change? (a plausible action, owner and constraint)
- Evidence challenger: what else could explain this pattern? (limitations, alternatives, uncertainty)

## 8. Rules on AI and integrity

- Analytical, visualization, coding and generative AI tools are allowed.
- External sources, templates and AI-assisted output must be acknowledged in the brief (methods note).
- The team stays responsible for accuracy and must be able to explain every analytical choice, so Claude Code should explain what it does and keep the analysis reproducible.
- No misleading visualizations, unsupported claims, omitted context or selective evidence. State assumptions, uncertainty and data limitations wherever they affect interpretation.

## 9. What Claude Code should produce

Suggested repository layout:

```
data/raw/          original downloads, untouched
data/processed/    cleaned tables used by the dashboard
notebooks/         exploration and hypothesis testing
src/               cleaning and metric code
dashboard/         the executive visualization
brief/             executive brief (max 5 pages) and exported PDF
slides/            5-minute presentation
docs/decisions.md  decision contract, hypotheses tested, assumptions, limitations, AI use log
```

Working order:

1. Write the decision contract (section 7) for the chosen challenge.
2. Profile and clean the data; log every transformation and assumption in `docs/decisions.md`.
3. Test hypotheses about drivers, checking segments and denominators.
4. Pick two or three insights that answer the three board questions.
5. Build the dashboard with the four-level structure, finding-style titles and one accent colour.
6. Draft the brief and the 5-minute storyline (roughly: decision problem, insight 1, insight 2, driver, recommendation and expected impact).
7. Run the pre-flight checklist and prepare answers to the four board questions.

## 10. Not available yet

- Week 4 material (tools, AI and interactive visual analytics) had not been posted on 12 Nov.
- The Week 3 "Cases for class" file (PowerPoint) was not read; its cases also appear in the Week 3 slides.

## 11. Contacts

- Instructor: Filipa Matos Baptista, filipa.baptista@novasbe.pt
- Teaching assistants: Marta Vaz, marta.vaz@novasbe.pt; Svitlana Sivitska, svitlana.sivitskaya@novasbe.pt
