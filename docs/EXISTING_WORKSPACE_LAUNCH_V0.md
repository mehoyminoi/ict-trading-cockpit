# Existing-workspace launch

**Operator 370: PASS (2026-10-31).** Accepted on PR #115 implementation `06cf18a`; draft/unmerged, stacked on #114. The explicit command below is now the accepted everyday entry for the existing durable Study workspace. No repeat check is requested.

This route opens the operator's existing durable Study workspace through the shared application. It removes the trial launcher's forced Calendar navigation and does not seed a question, criterion, trading run, date or interpretation. Existing records and fixture provenance remain; the title identifies the selected path as a retained trial workspace. This is not adoption of synthetic definitions as a Trade Plan.

## Bounded launch contract

- `python tools/open_cockpit.py --workspace DIRECTORY` requires an explicit existing directory. It uses that directory's `demo.db`, `demo.db.workspace.ini` and `xdg` media root. The module entry also accepts `--workspace`; the historical no-option module route remains the separate default application database.
- The supported directory retains its `study-criterion-v0.txt` marker, settings file and media directory. Unrecognized/missing files, external symlinked managed entries, invalid origin manifests and overlapping roots are refused. A typo cannot create an empty database. This is an existing retained Study route, not a general database picker or new-workspace creator.
- Only the current schema (53) is accepted. No schema initializer or migration is called for this route. Older/newer databases fail explicitly; an upgrade requires a separately reviewed procedure. SQLite validates required tables, quick integrity and foreign keys before the application is constructed. This is not a replacement for backup verification.
- Version-1 and version-2 origin manifests use the existing image resolver. Historical image references and manifest contents are not rewritten. Missing media does not fall back to original locations for restored workspaces.
- MainWindow owns normal routing: idle opens Study; an active run restores its process. No automatic run creation, environment change, progression credit or eligibility bypass. Existing timers, capture guards and normal saves operate as before.
- Per-database settings remain in place. Existing geometry recovery still adjusts offscreen or oversized windows to available screens. Normal close saves ordinary UI preferences; this is not a read-only viewer.
- Open only one Cockpit process against this workspace. There is no new cross-process locking mechanism in this slice.

## Operator check 370 — normal launch and reopen

Use this only after the branch is published and checked out. Close all Cockpit windows first. From the repository with your usual Python environment active, back up the current workspace and launch it:

```bash
cd ~/projects/ict-trading-cockpit
mkdir -p "$HOME/ict-study-backups"
study_launch_archive="$HOME/ict-study-backups/study-before-launch-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf "$study_launch_archive" -C "$HOME/ict-study-workspaces" study-v0 &&
python tools/open_cockpit.py --workspace "$HOME/ict-study-workspaces/study-v0"
```

1. The title identifies your `study-v0` directory. If no run was active, Study opens first instead of forcing Calendar. If a run was already active, it restores normally; do not create a new run just for this check.
2. Open a familiar investigation and saved capture using the existing Study controls. Confirm the question, observation and chart image are present. No new Study entry is required.
3. Close Cockpit and reopen with the same command below. Confirm the appropriate startup destination and familiar material remain, with window geometry recovered within the current screen bounds.

```bash
python tools/open_cockpit.py --workspace "$HOME/ict-study-workspaces/study-v0"
```

If the directory is rejected, stop and share the error. Do not create missing marker files, rename a database, change schema numbers or point this launcher at the separate TDA/Watch trial. The error does not mean your original data has been replaced.

After a pass, this becomes the normal command for the existing durable Study workspace. Keep the backup and recovery copies. The older Study demo command remains available for its original trial purpose, but forces Calendar and is no longer the recommended everyday entry once this check passes.

## Validation and limits

Developer validation: 39 checks PASS in 53.51s, covering 15 new launcher cases plus existing Study startup, geometry, recovery and MainWindow behavior. Rejected closed workspaces retain their files and environment; absent paths are not created; copied manifests v1/v2 preserve image resolution without originals; active Replay IDs and idle material/settings survive reopen. CLI help, Python 3.10 syntax and diff checks pass. Operator acceptance is separate. Check 370 is operator PASS. No broad redesign, workspace relocation, data merge, schema migration, new-workspace policy, installer, desktop shortcut or PR consolidation is included. Cumulative 1,317-test evidence on #114 remains prior evidence, not a claim that this new launcher has received a fresh full-suite run.
