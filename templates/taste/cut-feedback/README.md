> **`content/taste/cut-feedback/README.md`** · the files in this folder hold your own words from real cut reviews, captured verbatim by `cut-review` when a review closes · read by `cut-review` (its checklist learns from them), `long-form-editor`, `shorts-editor`, `taste-builder` (when promoting a rule).

# Cut feedback, the raw record

> What you actually said in a cut review, captured verbatim. This is the corpus the `cut-review` checklist learns from. **Learn first, automate after:** the checklist only gains a rule once your real feedback shows the same thing twice, and any clever upgrade (automatic audio or video analysis) is earned by evidence, never assumed.

## Where entries come from

Written at the moment a review closes, by `cut-review`'s retro, from the review conversation or the call recording. A weekly sweep can be the backstop, never the mechanism: if capture only happens weekly, the checklist can only learn one rule a week, and the next video ships before it does.

If 2 writers file the same review, the one written at the review wins.

## One file per review

`YYYY-MM-DD-<video-slug>.md`

```
# <video>, review <n> (post-cut | launch-readiness)
cut: <path or link> · reviewed: YYYY-MM-DD

## What was said
- [timestamp] "<verbatim>" → what it means for the cut
- [timestamp] "<verbatim>" → ...

## What the checklist missed
<the mechanical pass said pass, the person said fix. This is the learning.>

## What the checklist caught before anyone watched
<so the value of the gate is visible, and so you notice when it stops adding any>

## Candidate rule
<only if the same thing has now appeared twice; name the earlier file. Otherwise: "not yet, first instance.">
```

## The upgrade trigger (do not build early)

Once several files show the checklist missing things a machine could catch, propose the upgrade (audio analysis for dead air, video analysis for cuts that run long), with the evidence files named. Never build it before the evidence exists. A taste model built on guesses is the exact failure this system was written to end.
