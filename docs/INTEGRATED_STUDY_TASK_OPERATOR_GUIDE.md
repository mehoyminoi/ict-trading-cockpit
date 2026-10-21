# Integrated Study task — operator guide

This branch is not published yet. Wait for publication confirmation before pulling. Use a **new separate directory** for the first run; reuse it on restart:

```bash
python tools/integrated_study_task_demo.py --data-dir /tmp/ict-integrated-study-task-v0
```

The trial uses schema 47. Do not point it at your regular database or another demo directory.

## 301 — Question and reference together

The demo opens AMDX Lab. Enter `How did London manipulate Asia?` in **Study question**. Set **Historical reference · New York** to `2026-10-09` and `09:15`. Leave **Interpretation** at **Observed**. Select any quarter in the existing seven-layer table. The question remains nearby; normal legal entry still uses the existing immediate AMDX action. The definition area truthfully says no published AMDX criteria are configured. No run starts.

## 302 — Explicitly link a capture

Click **Open Study Find**. The investigation context appears above the form, initially labeled navigation context only. Enter:

- Date: `2026-10-09`
- Instrument: `MNQ`
- Session: `NYAM`
- Pattern: `Study task trial`
- Observation: `Testing retained investigation context`

Click **Link this capture to investigation**. Expect **Linked investigation** showing the question, October 9 reference with timezone, Observed, plan revision and actual recording time. This retains a draft; it does not yet save a completed Study Find or create competency evidence. If an existing draft was present, opening the route must preserve its text and date rather than replacing them. Linking is your explicit choice to associate that capture.

## 303 — Preserve the original association

Click **Return to AMDX investigation**. Change the question to `A later question`. Click **Open Study Find** again. The current navigation context can show the later question, but **Linked investigation** still shows the original one. Clicking **Link this capture to investigation** again must report that the capture cannot be reassigned. This is expected, not a test failure. Return and reopen capture to see the original saved association again.

## 304 — Save, Review and restart

Click **Save Study Find** (scroll down if needed). Return to the investigation, click **Review saved finds**, and select `Study task trial`. Its details must include the original linked question/reference. Click **Return to AMDX investigation**, close the window, and reopen the same command/directory. The later editable question and calendar orientation restore; Review still shows the original association. **New investigation** clears the editable question only; it does not alter that saved find. No new process run or competency evidence is implied.

## 305 — Smaller window and active-run preservation

Resize to approximately 1280×720. Scroll as needed to reach controls; the window should not force itself taller than the screen. In normal application startup, an existing active run still restores to its runtime. Investigation/capture/Review navigation must not conclude or replace it. A separate run need not be created just to repeat the already accepted startup test.

Report 301–305 PASS / FAIL / QUESTION / NOT TESTED. These checks accept this bounded integration, not final styling or the complete mature Lab.
