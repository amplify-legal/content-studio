# Lens: retention

Where a viewer leaves, and the one edit that would have kept them.

This lens wants the whole video, so run at `--detail balanced` (or `deep` if it
is under 10 minutes and the cuts matter). On anything over 10 minutes, run the
full pass first to find the soft regions, then re-run `--start/--end` on each one.

Output this:

## Retention, <creator> - "<title>"

**Runtime** MM:SS, **Predicted shape** one sentence, for example "steep drop
0:15-0:45, recovery at the demo at 2:10, slow bleed after 6:00".

### Where they leave

| Time | What happens | Why they go | The fix |
|---|---|---|---|

3 to 6 rows. Do not pad to fill the table.

### What held

2 to 4 moments where the visual and the audio together earned the next 30
seconds. Name the frame and the transcript line, not the vibe.

### Open loops

Every "we'll come back to this", "but first", or question raised and left. Mark
each **paid off** with its timestamp, or **dropped**.

### The one change

A single specific edit. Not "tighten the pacing", name the cut, the timestamp,
and what goes in its place.

---

Rules for this lens:

- Every claim is anchored to a timestamp.
- Nothing generic. If it is not visible in a frame or audible in the transcript,
  it does not go in.
- A section with nothing real to say says "None significant." That is a finding.
- This lens reads other people's videos. **Your own cuts go through
  `cut-review`**, which has the gates and the checklist. Do not duplicate it here.
