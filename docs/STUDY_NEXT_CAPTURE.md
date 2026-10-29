# Continue studying after saving

Both Save to investigation and plain Save Study Find now prepare a fresh capture when used in the Study Find workspace. A new identity clears Pattern, Observation, Notes, move value and attachment references. The investigation opening context is retained; without one, date/instrument/session carry forward from the saved capture. Returning through Open Study Find after changing the calendar reseeds this untouched form from the selected context. Once authored, draft protection applies.

Link-only deliberately keeps the current capture open: it does not save its content. Failed or cancelled saves retain input. Watch's contextual dock retains its existing save-and-return behavior. This slice does not change finding/question retention actions, whose source capture remains ongoing.

View last saved opens a read-only inspector without replacing the new draft. This shortcut lasts for the current application session; saved records remain in Review after restart. Saving does not automatically link the next identity: Save to investigation explicitly associates each captured example.

## Operator checks 343–344

Use the existing findings fixture after publication.

343: Open Study Find from the investigation, enter disposable Pattern/Observation/Notes and save to investigation. Expect a quiet saved confirmation, empty example-specific fields, retained date/instrument/session and a new capture ready to use. Enter a second example and use plain Save Study Find: expect the same fresh-form transition, with no new association for that standalone saved example. Inspect each last saved capture with View last saved; returning must leave the fresh/current draft intact.

344: Enter disposable draft content and use More → Link capture only. Nothing should clear. Save it, change the calendar date and reopen through Open Study Find: the untouched new form should follow the selected date. Enter a note, change the calendar again and reopen: that authored draft should retain its date and note with mismatch guidance. A cancelled differing-context save must retain it too.

This is a workflow checkpoint, not final form/layout approval. Schema 50 unchanged; publication and merge are not implied.

Validation: 26 distinct targeted checks passed across combined/standalone saving, failure preservation, capture context, discard, Watch contextual capture and next-capture inspection. Three old assertions expecting a saved form to remain were updated to assert the new identity and preserved saved record. Diff check passed. Operator checks pending.

Operator acceptance: 343–344 PASS on published #97 (`c36c591`). Both save paths, link-only preservation, last-saved inspection and context protection accepted. PR remains draft/unmerged.
