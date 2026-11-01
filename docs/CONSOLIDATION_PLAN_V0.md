# Consolidation execution record — Study/TDA/Watch main

**Completed under explicit operator authorization, 2026-11-01 UTC.** PRs #76–115 were retargeted to main and marked ready as needed, then merged in ascending dependency order using merge commits. All source branches are retained. No rebase, squash, force update, branch deletion or protection bypass was used.

Starting main: `6aa8d4ec990d8d371440271278bbb7368f186a64`. Final code merge: `4242c157c77b1cbc88c9ae3d3a1ffe0b358f69db`. Final tree: `169ac1902902497181a8d2b6227067a186d197a4`, byte-identical to the accepted #115 tip. The documentation-only main handoff follows this merge; it deliberately changes the full repository tree without changing runtime/tests/tools/schema.

For every PR, execution checked the frozen head, current main, commit statuses, successful GitHub merge, exact expected tree, ordered parents (previous main and PR head), merged PR state and retained source branch. The final audit repeated all 40 PR/base/head/merge and branch-preservation checks and verified the complete 40-commit first-parent sequence. No content conflict occurred, including the documented #83 smoke-result difference. No statuses were returned during the merge checks; this is not a claim of CI execution. GitHub accepted each operation without a gate override.

The full regression gate below remains valid because the final merge tree is exact. Operator 281–370 PASS is preserved unchanged. Final handoff validation checks Markdown, local links, the smoke-results file, and the documentation-only diff. No new application behavior or operator trial is introduced. Sync instructions are in `COCKPIT_MAIN_SYNC_GUIDE.md`; the current development checkpoint remains in `PROJECT_STATE.md` / `NEXT_CHAT_PROMPT.md`.

## Verified merge results

Each tree matched the corresponding frozen snapshot below; all rows were verified, not inferred.

| PR | Actual merge commit | Verified resulting tree |
| --- | --- | --- |
| #76 | `782323293e9801c95d8ff5072246748d3bc98a24` | `c88c1788dbfe898d568bec01c52cb9b29aef6806` |
| #77 | `955db05f0e13f5d8f8ebb31dccf0d659a2639b06` | `7bedde39b781c0d9ffa72aead8ed05500d9c0418` |
| #78 | `25b118546ee6529dbb9b9ef67764bd581f4a3323` | `db05ab07d1ddfce89582578d75e5548279018e6b` |
| #79 | `d9e747274c36bc919e50dac29b21aa8655f9dd58` | `1aa7a5eb4d25b5654513890406404ee7d706df53` |
| #80 | `ed95829650b80f211edb13e08d8b1b5f5f462b8e` | `b252e08177ff48e437894a755af96bbcc6fff6d8` |
| #81 | `48883920f9232514e81f0be9c23bf5b4cc2cc6cf` | `b5f8e5ea2ce677e343333b69960ef74af35813a7` |
| #82 | `065143b90cdcb85d03e5e03dad4b9f99832d5868` | `b0a358d807e61f7adc859f5ec6a31be502a74173` |
| #83 | `496dfe6cdc89e2b384f2c659d7c7e3bf9024e1df` | `9c3810977c0b5479567ab551da52a982f9a406ef` |
| #84 | `78de7ea3405b89385ee14727b3b65c51e46fa216` | `afff3064ae5c45ea881ea2aba01033a109761b36` |
| #85 | `cf22023e2e041d15ffe4830502d4a38c80de2742` | `4c3e472622561bf15364d240793883bb0e306f34` |
| #86 | `0cb73697f7b75fe39bebaf5e797ba98722e74304` | `a40c4f7191755adb26790e5bc76f83d09b03f6ea` |
| #87 | `f57f83c5cfdb1fb1ae7efbf74ecd9fef3e632a9c` | `2bd1ecfa51751e1630d9bb6e62ac7b05092907ae` |
| #88 | `b7516eb6a9aa2043a769e21cfd1f878c0ef7a222` | `96258c7199eb890f1ec7766a07f64ee58e2dd480` |
| #89 | `fef813a7d2a4f209ff5e1c7a12cc18ff9021e59a` | `bf9f0a1b473aa3a1413a3adc506d464a860ceea2` |
| #90 | `6d112dd1d04662e58fb1e40ffeed4e55eae51856` | `0a9f7021adc868c2543d599f26ed8ad019be57e4` |
| #91 | `3641f416ebb12ade3c351e212c3ffa8a226e6029` | `9476248b177a22f3be29a7569ffddb5b6beb695d` |
| #92 | `4908c3e316722cf8d7cc5788045ef1f34772382d` | `725ce2f5109d2783c4908ab0cb6ae250073c6006` |
| #93 | `7d83f8cb36cf60bf024098d1dab7a80f4fe8e531` | `ac80c8a74449e7e3a6b47120ffa2761ccaf9d39b` |
| #94 | `270bc1eb837716175cda0892e4c944b78c18f559` | `d9a790ec0931b33ece1f2b230589f36a077213fa` |
| #95 | `e086bdf0cb849b0886e97b5b33b23667a1f4c7ae` | `c747c01a6e7c5fce69ca266bf720ec052b733e16` |
| #96 | `43b503d14ec824daca7d004c0b15d37a046617e8` | `c58202b5c630f698894c8479b41c678270df6297` |
| #97 | `7bf820d34786f4352ece6809bc5b9e251b9ec0c4` | `c56dd7602e834bd88e9655b8534df12e61dc8d8d` |
| #98 | `25482fca4b52c8ce59f3ae2f32aad310f3587321` | `7fdcdce10db4b0004876150be392efcfe708510d` |
| #99 | `9a741dda6b293081ee2e4df91df4a29dc6a52076` | `10a691df81e7f3b6796e3e858c7dbc79c540bc04` |
| #100 | `97816e4b088acb8d0c60304208108fb816db3904` | `58791137d475e401c6ad08964bda8fce3a63a070` |
| #101 | `106ac8b65bc5b334cd743bad346b5572b30f4bbe` | `1bb4882a3f0c1717014a2a397864a2e784029569` |
| #102 | `9e88e9df4268deb09d9cdf6d4f74eab380edb501` | `07e87dbb2bc622fad91ff3bb137576d616802eff` |
| #103 | `800924b615e343eb1ef2c019433f06a406767bfa` | `b452e36627c2e8d4cfa0b9c4cc3acaeef99976dc` |
| #104 | `b40064df959f3579a6c55430cdc0c61ad4b08e95` | `6f224c7eb042dc2b0634a7ff66a395ce542c87f7` |
| #105 | `259a2e0157127d0c7b9fb74875692bcb796c7f5f` | `5104dd0ceeda8177575d5db692a7770e6f36f16b` |
| #106 | `37286a470e72e146821f0488d2d7e70998a4456d` | `782e35944a3f272a31b282796f217ff59afe0420` |
| #107 | `7285ba81a2630c4cc3764ed62b54b828292fffa9` | `0540534accdacdbb6529869d367d3461f8a75129` |
| #108 | `358ffe4e495b11bfa5363371ab931acfc24013ed` | `b0eff8b84406cef100c11adaf9a2f56dec39a235` |
| #109 | `d3ffdc459fb24e3ed10ad18a1cc914220a330be0` | `6b007d44512ca3144c744a48ed65a7734752873e` |
| #110 | `d93b0831776289973f037cee081b3d69fad39798` | `5034338a875e5d499eb267ea4450e3e38031c135` |
| #111 | `dbca58b51634e9efed4d3e3241f93995ab94c453` | `9177e46cfa0b1c46fec7dd5f487896b7a40383b1` |
| #112 | `a8d82e1e166c76846388fe3b2a218cf0e03d2492` | `dff6ab48ae3c95a4b565f11e71143d0b1aa474e0` |
| #113 | `9be954e5cf30ddd2a554d400c8534e9e8f0cb667` | `755469cd22eec2e843277df6602b9bbdf92ebb7c` |
| #114 | `9679ab38c3b507b454f05f9e92bcab01756e75d6` | `f0102dadfecb0f56bb049fd5a42a7a834134251b` |
| #115 | `4242c157c77b1cbc88c9ae3d3a1ffe0b358f69db` | `169ac1902902497181a8d2b6227067a186d197a4` |

## Original approved proposal — historical

Prepared 2026-10-31. **Proposal only: no merges, retargeting, draft-state changes, rebases or branch deletion performed.** Operator authorization is still required. This document is the concrete integration procedure; current checkpoint remains in PROJECT_STATE/NEXT_CHAT and operator-facing stages remain in the bundled roadmap.

## Scope and evidence

- Starting main: `6aa8d4ec990d8d371440271278bbb7368f186a64`.
- Accepted stack tip: #115 `6a5605f5137d4b92597b9be75495bd546f0320af`, tree `169ac1902902497181a8d2b6227067a186d197a4`.
- GitHub inspection: all 40 PRs #76–115 are open drafts, each targeting the preceding branch except #76 targeting main. No merge authorization has been inferred from operator PASS.
- SMOKE_TEST maps all 90 checkpoints 281–370 to PASS. Preserve earlier qualifications and deferred features; this is not blanket UX approval, competency certification or trading permission.
- #83's head `a447a6b` is one smoke-results commit beyond inherited `0f38a09`. It changes only 311–312 to PASS. Both results already appear at the tip. Read-only `git merge-tree` previews for #84–115 are conflict-free; previewing #83 into #115 yields the exact tested tip tree. These previews write no branch refs or working files.
- No status checks or PR-triggered Actions runs were returned for the inspected tip. That is absence of CI evidence, not a CI pass or permission to bypass GitHub protection rules.
- Fresh cumulative regression result is recorded below after completion. The earlier #114 result predates the launcher and is not substituted for this gate.

## Authorized execution would proceed as follows

1. Re-read main and every PR head against the snapshot below. Stop on unexpected movement, new failures, required reviews/checks or merge restrictions. Do not force, reset, rebase or bypass a gate.
2. Process **#76, #77, …, #115**, in ascending dependency order. For each PR: retarget to main if needed, mark ready for review, satisfy applicable GitHub gates, and merge with a **merge commit** using the inspected head SHA as the guard. Do not squash, rebase or delete source branches. These actions require explicit authorization; changing draft/base state is included in the proposed scope.
3. After each merge, verify main's tree against that PR's expected integration tree below. This accounts for #83's retained smoke-result delta. A mismatch stops the sequence for investigation; no automatic conflict resolution is authorized.
4. After #115, main must equal `169ac1902902497181a8d2b6227067a186d197a4` exactly. Confirm all 40 PRs are merged, their source branches retained, and the final application/test tree matches the freshly validated tree. If exact, retain the completed test evidence rather than repeat unchanged tests. Any changed product/test content reopens relevant validation and acceptance.
5. Publish a documentation-only final main handoff: exact merge SHA/tree, validation results, preserved acceptance, accepted launch command and sync instructions; update the existing roadmap. This publication must be covered by the same explicit authorization. Preserve runtime/tests/tools/schema content exactly. Do not silently fold in the separate unpublished workflow-efficiency documentation branch.
6. Give the operator exact commands to preserve local smoke notes, fetch/switch main, and verify its checkpoint. Do not overwrite or delete local commits/stashes. Keep using `python tools/open_cockpit.py --workspace "$HOME/ict-study-workspaces/study-v0"`. No directory move, data import, fresh study exercise or migration is needed for this already-schema-53 workspace.

## Guardrails and rollback

This is Git integration only. Existing user databases, images, settings, archives and recovery copies remain untouched. Database schema stays 53 / Alpha 0.7. The accepted launcher refuses older/newer schemas and retains fixture provenance. No broker connection, order entry or broader Live eligibility follows from merging.

If a merge step fails or produces an unexpected tree, stop at the last verified main commit and report the PR/head/error. Do not undo history, revert commits, delete branches or modify user data without a separately reviewed recovery action. Retained feature branches and backups provide reference points; they are not an instruction to run older application code against newer data.

## Frozen head and expected integration-tree snapshot

The tree column includes #83's two smoke-result changes where necessary. Refresh before execution; this snapshot does not authorize merging a later changed head.

| PR | Inspected head | Expected main tree after merge |
| --- | --- | --- |
| #76 | `611c8ff033e53c101780879c51e026e0c310d351` | `c88c1788dbfe898d568bec01c52cb9b29aef6806` |
| #77 | `be6439d3b5110fafab91919f4a3f092117a83780` | `7bedde39b781c0d9ffa72aead8ed05500d9c0418` |
| #78 | `0988b4b722cb02b93997ffb440355e41a0caf7c0` | `db05ab07d1ddfce89582578d75e5548279018e6b` |
| #79 | `6561f2ce1eed7e6025162fff21d8c906189496c6` | `1aa7a5eb4d25b5654513890406404ee7d706df53` |
| #80 | `953c812db0b21404471d8171881226b94b6c44ce` | `b252e08177ff48e437894a755af96bbcc6fff6d8` |
| #81 | `6b04866417d255606f70cd501e70eeaf9f59be3d` | `b5f8e5ea2ce677e343333b69960ef74af35813a7` |
| #82 | `bbf44f8dcc9c9647b972e03175f5e29b831de133` | `b0a358d807e61f7adc859f5ec6a31be502a74173` |
| #83 | `a447a6bcb803a19bce5af044b59f5a8cf7a0dc66` | `9c3810977c0b5479567ab551da52a982f9a406ef` |
| #84 | `e9460fe2776e565b974956a65e7faa4c64a11afb` | `afff3064ae5c45ea881ea2aba01033a109761b36` |
| #85 | `cf9f660307c04f65a9353b674f1a186353d33409` | `4c3e472622561bf15364d240793883bb0e306f34` |
| #86 | `2b9fca56f2040faada29c449900fb647e87b24f9` | `a40c4f7191755adb26790e5bc76f83d09b03f6ea` |
| #87 | `1258b435931fa891920f984e02356d55e6fdb16d` | `2bd1ecfa51751e1630d9bb6e62ac7b05092907ae` |
| #88 | `51ba1e5edc5e5263ce6342c7bb72b73df0b83335` | `96258c7199eb890f1ec7766a07f64ee58e2dd480` |
| #89 | `c732866c0af134c9dba9b8dc8dbb624458a4b83d` | `bf9f0a1b473aa3a1413a3adc506d464a860ceea2` |
| #90 | `212ddcf29d448359b74eb7c3cdc6c89b699f86a4` | `0a9f7021adc868c2543d599f26ed8ad019be57e4` |
| #91 | `6454e04892fb3d87956d44734ee40bcace9054bb` | `9476248b177a22f3be29a7569ffddb5b6beb695d` |
| #92 | `e733f41c9ffdb1ddc5020ff60b21c1378a21b9ba` | `725ce2f5109d2783c4908ab0cb6ae250073c6006` |
| #93 | `f410179c6cf63c4b0516941a742f64f670e2b437` | `ac80c8a74449e7e3a6b47120ffa2761ccaf9d39b` |
| #94 | `6908b14e258e8b323947f932dc2394564d93f689` | `d9a790ec0931b33ece1f2b230589f36a077213fa` |
| #95 | `b8510d22bf460b084020159971c07c26fd590270` | `c747c01a6e7c5fce69ca266bf720ec052b733e16` |
| #96 | `53ce5b8a21e4ff839a07737a29b9ba91c351498c` | `c58202b5c630f698894c8479b41c678270df6297` |
| #97 | `c36c5916d832ecf4a692345cd6827d7e2f4c0215` | `c56dd7602e834bd88e9655b8534df12e61dc8d8d` |
| #98 | `93ce461ef43bf35469fdd6d30dabc778743273fa` | `7fdcdce10db4b0004876150be392efcfe708510d` |
| #99 | `fedd532aec4513ad96729eabb5d1e921e539c639` | `10a691df81e7f3b6796e3e858c7dbc79c540bc04` |
| #100 | `a744dc961a78cf6c4062b6d3ee81f5c2738327a7` | `58791137d475e401c6ad08964bda8fce3a63a070` |
| #101 | `294e908c2f06937033dd0ed8fe47e71214e84c54` | `1bb4882a3f0c1717014a2a397864a2e784029569` |
| #102 | `fac47c4fbe3ffba0db29c1e0446c9b66b1f5874a` | `07e87dbb2bc622fad91ff3bb137576d616802eff` |
| #103 | `5a6df7b2c530f654eeb779ab2e90e99ff6f5a791` | `b452e36627c2e8d4cfa0b9c4cc3acaeef99976dc` |
| #104 | `40f8069d2925e1f40ee1db8b7479a3e6f0a1b219` | `6f224c7eb042dc2b0634a7ff66a395ce542c87f7` |
| #105 | `6aafebad91930f5accfa82215d2a9cae13b052ac` | `5104dd0ceeda8177575d5db692a7770e6f36f16b` |
| #106 | `a561bb680940a38266859b86b2f68ce61ae3f859` | `782e35944a3f272a31b282796f217ff59afe0420` |
| #107 | `2843baf9bced560f995b07e257f89e916d73af1e` | `0540534accdacdbb6529869d367d3461f8a75129` |
| #108 | `ed8b24735baa1a042cbae509cb0710e11991514a` | `b0eff8b84406cef100c11adaf9a2f56dec39a235` |
| #109 | `9059e7046ca755379bf8e1522640542e5189c479` | `6b007d44512ca3144c744a48ed65a7734752873e` |
| #110 | `7917471b55ca2e3fff188cada1ff0e1b7c177708` | `5034338a875e5d499eb267ea4450e3e38031c135` |
| #111 | `b8f7b42336ddd168cb176a5e884bfb76aa0d251a` | `9177e46cfa0b1c46fec7dd5f487896b7a40383b1` |
| #112 | `64d72d85db5806f908ed05dfad13ee63a0c251a8` | `dff6ab48ae3c95a4b565f11e71143d0b1aa474e0` |
| #113 | `3d99dacfa7607ad2ec32ed661ad56b5812c61385` | `755469cd22eec2e843277df6602b9bbdf92ebb7c` |
| #114 | `a174ea51febfbb7243674c4a7ba99dc2f74068b9` | `f0102dadfecb0f56bb049fd5a42a7a834134251b` |
| #115 | `6a5605f5137d4b92597b9be75495bd546f0320af` | `169ac1902902497181a8d2b6227067a186d197a4` |


## Final gate — PASS

Fresh full collection and execution on accepted #115 head `6a5605f5137d4b92597b9be75495bd546f0320af` / tree `169ac1902902497181a8d2b6227067a186d197a4`: **1,332 PASS across 128 isolated module processes in 173.30 seconds**. Four workers; independent HOME/XDG config/data/cache per module; offscreen Qt. Every module exited 0 and its JUnit count matched collection; zero failures, errors, skips, timeouts or pytest warning summaries. All validation processes finished. Runtime Python 3.12.14 / PySide6 6.12.0 / pytest 9.1.1. No product/test corrections or reruns were needed for this gate. This is one clean complete module-isolated run, not a single-process Qt session.

The accepted launcher, restored-image paths, old E6 migration, startup/resume, Study, TDA and Watch tests are included. This supersedes the pending final-gate status; earlier partial/rerun histories remain accurate for their own checkpoints. No additional operator trial is requested. GitHub rules/checks must still be honored at execution time.

This plan/handoff/roadmap update is documentation-only, based on the tested tree. It is prepared locally, not yet published or merged. Final main documentation may incorporate this plan and the completed execution record under explicit authorization; it must not alter the tested runtime/tests/tools/schema.
