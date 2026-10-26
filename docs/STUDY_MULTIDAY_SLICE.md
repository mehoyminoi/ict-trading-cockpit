# UX4e — One retained criterion across selected references

Based on operator 321–324 PASS at `1258b43` on draft #87. The accepted Study dialog gains explicit New York date/time selection, Use this reference, and Previous day/Next day. This removes repeated dialog opening when collecting several days for one investigation.

The task/question and selected immutable criterion revision stay the same across a deliberate reference change. The shared calendar resolver provides the quartet for the existing layer. Observation values and sources start empty; available-at controls visibly start at the new reference. No fact or result is copied forward. Fixed input identities remain fixed; reusable scopes bind within the new quartet.

A proposed date/time disables Explain/Save until applied. A failed resolution or nonexistent New York clock time leaves the active reference and observations unchanged. Repeated autumn hours expose the existing first/second-occurrence choice. Discarding unsaved observations/preview requires confirmation; Cancel restores the original reference controls and leaves the original preview saveable. No-op reference application retains current work.

Saved results remain separate immutable records in schema 48. The list identifies reference, outcome, criterion revision and question. A small coverage summary counts saved records, distinct New York reference dates and distinct criterion revisions; it does not treat repeated results as independent outcomes or calculate performance. Reading an older result never retargets current input fields. Reopening recovers all saved task results using the existing storage. Last unsaved dialog navigation/input is not restart-persistent.

No schema migration, classifier, plan adoption, calendar revision or Trading Run. No automatic weekend skipping, sampling policy, price import or cross-date statistical comparison. Selecting another date in a higher layer can remain within the same quartet; reference dates are not represented as distinct quartet samples. Dialog date navigation does not move the underlying calendar or its pinned operating-run context.

The existing seeded demo uses a new directory for operator 325–327; see `STUDY_MULTIDAY_OPERATOR_GUIDE.md`. Review focuses on coherent multi-day study and truthful evidence ownership, not final styling. Subsequent work should address a concrete study need before adding automatic comparisons or scoring.

## Verification

72 focused tests pass: 12 multi-day and existing independent Study checks, plus 60 shared calendar-context, smoke-document, MainWindow and integrated Study regressions. New coverage includes two-date result retention/reopen, blank new-date observations, unchanged fixed scopes, pending-date save protection, canceled/discarded navigation, invalid spring clock times, and explicit autumn repeated-hour selection. The 12 Study checks were repeated after correcting temporary old-field overlap during form rebuilding. Native renders inspected at 1000×800 and 720×600; controls remain accessible with scrolling. Python 3.10 syntax and diff checks pass. Operator 325–327 remains pending.
