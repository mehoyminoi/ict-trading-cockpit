> Superseded operational instructions: use `STUDY_CONNECTED_WORKFLOW_REVIEW.md` and the durable workspace. The temporary fixture and pre-save/review sequence below are historical; do not follow them for retained work.

# Real Study session: observation, interpretation and larger context

## Checkpoint and purpose

Draft-discard 336–337 PASS is published at `f410179`. Capture context, question parking/direct save and discard now support another real session. This is the third step in STUDY_REAL_SESSION_FINDINGS.md, not another isolated control-polishing round. No new production behavior, schema change or numbered PASS/FAIL gate is introduced.

Use one already-familiar historical day, preferably the London → NYAM example that prompted the original question. A useful session can stop after one capture; no need to find a fresh pattern or prove a rule. Optional time box: about 15–20 minutes. The goal is learning utility and field design, not sample size.

## Separate work area

The existing published application is sufficient; no new pull is needed if already on the accepted draft-discard branch. To keep this research separate from synthetic test captures:

```bash
python tools/study_criterion_demo.py --data-dir /tmp/ict-study-narrative-v0
```

Use a new directory for the initial run; reuse it to resume. This is the existing synthetic demo shell, not a new real-market data integration. Replace the seeded investigation question; leave the synthetic criterion evaluator aside. No automatic task promotion from the question inbox exists yet.

## One question

Suggested wording, editable:

> What information supported the London interpretation, and what later NYAM information changed it, in the context of the higher-timeframe narrative?

Do not assume either interpretation is correct. If using fully revealed historical charts, label the notes retrospective; do not present them as prospective predictions.

## One connected pass

1. Open the day in TradingView and the same explicit reference in the cockpit. Select the session being captured. Verify the capture date/instrument/session instead of assuming a hidden association.
2. Capture one useful chart, optionally with a second view showing the broader timeframe. Record the chart timeframe and relevant New York event times in text for now. The application cannot detect TradingView timeframe or extract these semantics automatically.
3. Use **Observation** for the chronological price action and what was visible at each point. Try plain prose. If useful, indicate `London — …` and `NYAM — …`; no mandatory template or acronym expansion.
4. Use **Notes** for interpretation, uncertainty, competing explanations and the connection to the higher-timeframe narrative. If helpful, distinguish `What I could infer then` from `What I noticed afterward`. No need to fill every conceptual dimension.
5. When another worthwhile question appears, select it and Keep question for later, then continue. Do not force a tangent just to exercise the button.
6. Explicitly link and save the capture. Inspect it from Investigation overview. Can the saved material reconstruct the sequence, broader context and reason your interpretation changed?
7. Briefly report what you learned, what remains uncertain and the next useful question. These can be reported in chat; the current application does not yet provide a complete research-conclusion/next-step handoff. Do not manufacture competency evidence just to finish the exercise.

Available Move can remain unused. Its multi-target meaning, hypothetical entry basis and broader statistical comparisons need their own design; this session should not force an arbitrary distance.

## Feedback that will determine implementation

- Which facts did you repeatedly retype (date, session, timeframe, event time, HTF thesis, source)?
- Did Observation versus Notes reduce ambiguity or require needless mental sorting?
- Where did local detail make the wider narrative hard to retain or revisit?
- Did the saved result help you learn/reconstruct the argument, and what would make the next session easier to begin?

Report any other friction freely. These are lenses for evaluation, not restrictions on feedback. If a defect blocks the session, stop there and report the exact step; do not spend the time box working around it.

## Design decisions intentionally left open

Structured timeframe/event-window fields versus light text guidance; how to keep HTF narrative nearby; explicit conclusion/next-action retention; selecting a queued question as the next investigation without displacing unfinished work. Proposed fields are not requirements until the need is demonstrated. Vocabulary links, multiple moves and Trilium integration remain recorded future directions.
