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

Verify that archive with `verify_study_backup.py ARCHIVE --original-root "$HOME/ict-study-workspaces/study-v0"`. The verifier now understands preserved historical paths through the manifest. A second relocation of an already-relocated archive is deliberately refused by the restore tool; restoring a later archive to another path needs an explicit extension. No symlinks back to temporary storage or silent snapshot rewriting are used.

## Validation

30 targeted tests PASS: nine restore/backup/next-capture checks and 21 existing capture/review/media checks. Diff check passed. Automated checks cover unchanged database bytes, original preservation, resolution with originals absent, no fallback to original images when a copied image is missing, refusal to overwrite, invalid/external path handling and verification of a subsequent durable archive. Original archive verification was operator PASS: schema 51, three saved finds/associations, one draft/question/image reference and five reviews. Archive SHA-256 `a08968ccebad82561714b5db03a2b117556027c30d54e1beb38c8859a38c7889`. This does not certify work created after that archive.

Operator 351 pending. Local implementation; publication requires authorization as a draft stacked on #101. Do not merge.
