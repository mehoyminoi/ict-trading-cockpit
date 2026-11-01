# Verify the retained Study backup

This is a preservation step before changes to investigation storage. It checks a closed-workspace archive in isolation; it does not open the application, migrate data, rewrite saved paths or modify the original workspace/archive.

After publication, activate the existing virtual environment and run:

```bash
python tools/verify_study_backup.py "$HOME/ict-study-backups/REPLACE-WITH-YOUR-ARCHIVE.tar.gz"
```

Use the exact filename created earlier (list with `ls -lt "$HOME/ict-study-backups"`). The original root defaults to `/tmp/ict-study-review-v0`; use `--original-root` only if that archive was created from a different directory. If making another archive, close Cockpit first so database/settings/images are captured together.

Expected output: `status: PASS`, archive SHA-256, schema 51, per-table row counts and a unique image-reference count. Report PASS and that image count; do not paste study content. Failure exits nonzero and explains the problem. Preserve originals and archive on either outcome. A zero image count means no references were found, not that image restoration was exercised.

The checker rejects links, traversal and unexpected archive roots; extracts regular files into a disposable temporary directory; checks database integrity/foreign keys; requires the demo marker and workspace-settings file; and scans image columns plus nested JSON image references, including review/question/finding snapshots. Every referenced image must be nonempty and readable within the restored workspace. It never falls back to the original file. Temporary verification files are removed on exit.

Limits: no GUI restoration or image decoding, no assertion that the backup contains work created after it, no semantic validation of all stored records or settings, and no relocation/migration certification. Archives are local trusted backups; there is no resource-size limit for untrusted archives. Absolute historical image references remain unchanged. Durable relocation requires a separate path-resolution design rather than rewriting immutable historical records or pointing a new workspace back into `/tmp`.

Validation: five targeted automated tests using the actual schema cover recovery with the original removed, missing archived images despite available originals, external references, traversal, and symlinks. Operator verification of the real archive remains pending. No numbered UI smoke test is added.
