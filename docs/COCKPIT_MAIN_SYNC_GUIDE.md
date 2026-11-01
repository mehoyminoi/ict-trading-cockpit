# Use the consolidated main cockpit

PRs #76–115 are merged. Final code merge: `4242c157c77b1cbc88c9ae3d3a1ffe0b358f69db`; validated tree: `169ac1902902497181a8d2b6227067a186d197a4`. A following documentation-only commit publishes this guide and handoff. Your normal workspace remains `$HOME/ict-study-workspaces/study-v0`, schema 53. No data move, restore or migration is needed when continuing from the accepted #115 setup.

## 1. Close Cockpit and inspect local changes

```bash
cd /home/jesse/projects/ict-trading-cockpit &&
git status --short &&
git branch --show-current
```

If the only change is `docs/SMOKE_TEST.md`, preserve it before switching:

```bash
git diff -- docs/SMOKE_TEST.md &&
git stash push -m "Smoke notes before consolidated main sync" -- docs/SMOKE_TEST.md &&
git status --short
```

If there are other changes, stop and review them before switching. Do not reset, discard, pop old stashes or delete branches. Already-committed local work remains on its existing branch. Main already contains operator PASS results 281–370, so do not automatically apply old smoke-result stashes over it. The stash above preserves any extra notes for later review.

## 2. Switch to main and fast-forward only

Continue only with a clean working tree. This handles repositories whose fetch configuration previously tracked only a feature branch.

```bash
git fetch origin refs/heads/main:refs/remotes/origin/main &&
if git show-ref --verify --quiet refs/heads/main; then
    git switch main
else
    git switch --track -c main origin/main
fi &&
git merge --ff-only origin/main &&
git merge-base --is-ancestor 4242c157c77b1cbc88c9ae3d3a1ffe0b358f69db HEAD &&
git log -1 --oneline &&
git status --short
```

The latest commit should be the documentation handoff or a later verified main checkpoint. The ancestor check confirms this consolidation is included. If fetch, switch or fast-forward fails, stop and share the output; do not pull with rebase, force/reset, or merge local divergence blindly. The final publication message provides the exact handoff commit to compare immediately after publication.

## 3. Open the same retained workspace

Using your existing project virtual environment:

```bash
source .venv/bin/activate &&
python tools/open_cockpit.py --workspace "$HOME/ict-study-workspaces/study-v0"
```

Normal idle startup opens Study; an active run restores through the existing routing. Database, images and settings stay in the same workspace. Keep existing backups and the accepted recovery procedure in `STUDY_DURABLE_WORKSPACE.md`. This sync does not create a new fixture, import data or confer additional trading eligibility. Do not use the old default module/fixture commands as substitutes for this explicit-workspace launch.

No new smoke-test number is required. Continue ordinary use; report meaningful friction or continuity issues so the next slice can be chosen from evidence.
