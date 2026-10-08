# Smoke Test Runner

Developer-only UI for completing `docs/SMOKE_TEST.md` without manually editing
status tokens.

Run from the repository root with the project virtual environment active:

```bash
python tools/smoke_test_runner.py
```

Or pass another Markdown checklist:

```bash
python tools/smoke_test_runner.py path/to/checklist.md
```

The runner edits only validation items already marked with one of:

- `[PASS]`
- `[FAIL]`
- `[QUESTION]`
- `[NOT TESTED]`

It preserves the validation wording and other Markdown. Comments entered in the UI
are saved as indented bullets beneath the validation item.

The summary reports `ACCEPTED` only when every parsed validation item is
`PASS`. Saving is still allowed while unresolved items remain so failures and
questions can be committed as evidence when appropriate.
