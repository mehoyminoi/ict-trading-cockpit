# Durable Study workspace

This slice restores a verified archive into a new persistent directory without rewriting database records or historical image references. A `study-workspace-origin.json` manifest maps the original root to this workspace at display time. Capture and saved-find preview/copy/enlargement use the mapped image exclusively; new captures use the new workspace media directory. Raw historical path text remains original provenance. Schema 51 unchanged; this remains the existing mixed synthetic/real fixture, not a declaration that fixture rules are adopted.

## Before switching

Close Cockpit. If you have made entries since the earlier archive, create a fresh one using the previous backup commands. Restoring an old archive does not include newer work. Keep originals and archives. Use a new destination; existing destinations are refused.

After publication, from the repository and active virtual environment:

```bash
python tools/restore_study_workspace.py "$HOME/ict-study-backups/YOUR-ARCHIVE.tar.gz" --destination "$HOME/ict-study-workspaces/study-v0"
python tools/study_criterion_demo.py --data-dir "$HOME/ict-study-workspaces/study-v0"
```

The restore command first performs isolated archive verification. It does not launch or migrate the application. The normal demo launcher can then open the copied database and settings. Restoration carries only state actually stored in the archive; it does not repair the previously identified in-memory pending capture destination limitation. Check any unfinished capture's displayed investigation destination before saving. Safe investigation resumption remains next.

## Operator 351 — copied workspace and images

1. Open the durable workspace with the command above. Confirm your known saved captures, question and reviews are present. Saved-find chart preview, enlargement and Copy Selected Image should work.
2. Inspect the retained unfinished draft without saving it to a new investigation. Confirm its text and any attached image survive.
3. Create a clearly disposable capture with a pasted image, save it, close/reopen the same durable workspace and confirm the image remains viewable. This checks new writes use durable storage. Do not remove original files for the test.
4. Use the durable launch path for subsequent work. Preserve `/tmp` originals as recovery material; do not keep editing both copies.

For later backups, close Cockpit and archive the entire durable directory (including manifest):

```bash
mkdir -p "$HOME/ict-study-backups"
tar -czf "$HOME/ict-study-backups/study-durable-$(date +%Y%m%d-%H%M%S).tar.gz" -C "$HOME/ict-study-workspaces" study-v0
```

Verify that archive with `verify_study_backup.py ARCHIVE --original-root "$HOME/ict-study-workspaces/study-v0"`. The verifier now understands preserved historical paths through the manifest. The original implementation refused a second relocation. The recovery extension below supersedes that limitation; use the matching updated application and tools for version-2 manifests. No symlinks back to temporary storage or silent snapshot rewriting are used.

## Validation

30 targeted tests PASS: nine restore/backup/next-capture checks and 21 existing capture/review/media checks. Diff check passed. Automated checks cover unchanged database bytes, original preservation, resolution with originals absent, no fallback to original images when a copied image is missing, refusal to overwrite, invalid/external path handling and verification of a subsequent durable archive. Original archive verification was operator PASS: schema 51, three saved finds/associations, one draft/question/image reference and five reviews. Archive SHA-256 `a08968ccebad82561714b5db03a2b117556027c30d54e1beb38c8859a38c7889`. This does not certify work created after that archive.

Operator 351 pending. Local implementation; publication requires authorization as a draft stacked on #101. Do not merge.


## Durable backup recovery extension — checkpoint 369

The restore tool now accepts archives from an already-restored durable workspace. Each recovery retains all earlier root mappings and the previous manifest, plus the new archive digest and verification report. Historical database bytes, saved image references and workspace settings are copied unchanged. Images created before and after earlier restores remain resolvable using only the restored directory. No fallback to old directories is allowed. Existing destinations, ambiguous nested roots, invalid manifests and unsafe archive members are refused.

Initial relocation still writes manifest version 1. A subsequent relocation writes version 2 with explicit `reference_roots` and the unchanged `previous_manifest`. This is a media-location format extension, not a database migration (schema 53 unchanged). Older clients do not understand version 2: use this branch or a later integrated version to open the recovery copy. Keep the working original and archives; do not switch between old/new clients on the recovery copy. Manifest provenance is retained metadata, not cryptographic authentication of the operator's files.

### Operator check 369 — recover a current backup into a separate copy

Do this only after the recovery branch is published and checked out. Close all Cockpit windows first. From the repository directory, run:

```bash
mkdir -p "$HOME/ict-study-backups"
study_recovery_stamp="$(date +%Y%m%d-%H%M%S)"
study_recovery_archive="$HOME/ict-study-backups/study-durable-$study_recovery_stamp.tar.gz"
study_recovery_copy="$HOME/ict-study-workspaces/recovery-check-$study_recovery_stamp"
tar -czf "$study_recovery_archive" -C "$HOME/ict-study-workspaces" study-v0 &&
python tools/restore_study_workspace.py "$study_recovery_archive" \
  --original-root "$HOME/ict-study-workspaces/study-v0" \
  --destination "$study_recovery_copy" &&
python tools/study_criterion_demo.py --data-dir "$study_recovery_copy"
```

The chained commands stop before opening a copy if backup or restore fails. A `Restored workspace:` message is expected. In the copy, open a familiar investigation and saved Study Find. Check its question, observation, chart image and retained review material. Close and reopen the same copy with:

```bash
python tools/study_criterion_demo.py --data-dir "$study_recovery_copy"
```

The variable remains available only in that terminal; the restore output prints the exact path if needed later. Confirm the same material remains available. This is an inspection: no new Study session or disposable capture is required. Close the copy and resume everyday study with your unchanged normal path:

```bash
python tools/study_criterion_demo.py --data-dir "$HOME/ict-study-workspaces/study-v0"
```

Keep the archive, original and recovery copy. Do not delete, rename or relocate original data. Automated disposable tests cover recovery when original directories are absent; you do not need to simulate data loss manually.

### Verification and remaining scope

Developer checks: 16 backup/restore tests PASS, including three successive recoveries with new image references at each generation, exact database/settings preservation, retained manifest provenance, archive/source preservation, invalid formats, overlapping roots, symlink escape and no fallback to old media. Eight existing media, window-restoration and next-capture tests PASS. Standalone restore CLI help and diff checks passed. No full-suite run or operator acceptance is claimed; checkpoint 369 is pending. This closes one recovery gap, not all daily-continuity or stack-consolidation gates.
