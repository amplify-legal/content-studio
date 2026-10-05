---
name: on-camera-board
description: >-
  Build the surface the creator presents from and draws on while filming. Frames they click
  through on camera, annotate live, and zoom into as emphasis. Use for - "build the board for
  this video", "the filming board", "the deck for recording", "board frames", "I want to circle
  things while I talk", "present from the canvas", "add a frame", "fix frame 4", "reorder the
  frames". Covers building a frame set from a brief or a script, editing an existing one, and
  checking it before the camera turns on. The mechanics section is written against Miro; any
  whiteboard that lets you draw live over the frames works, and the spec, the frame rules and
  the checks are tool-agnostic. NOT for prep docs, reports or the artifact you send
  someone after the call (that is design-dna and whatever presenter skill builds your HTML).
  NOT for ideation or mind-mapping boards. NOT for thumbnails or title cards (that is media-gen).
---

# The on-camera board

**Load before any step:** `content/PRINCIPLES.md` (the constitution: it wins over every step here), then `content/taste/formats.md`, `content/taste/must-dos.md` (what every recording has to carry on screen) and `content/brand.md` (your colours and fonts). `content/reference/taste-system.md` says what each taste file holds.

The surface the creator is looking at, clicking through and drawing on while the camera rolls.
It is the single thing on screen for most of a talking-head video, so it gets built for
performance rather than for completeness.

The distinction this skill exists to protect:

| | Owns |
|---|---|
| **The on-camera board** (this skill) | Everything presented from while filming. Frames, live annotation, zoom, the thing being crossed out. |
| **The HTML presenter** (`design-dna` plus your presenter skill) | The send artifact, the prep doc, the report, the dashboard. Anything a person reads on their own screen at their own pace. |

The board is built from the approved script, never the other way round. When both exist for
the same recording, read them against each other and report the diff: section order,
numbering, every number said aloud versus every number on a frame.

Those are different jobs and conflating them is expensive. A reading surface presented on camera
is a filming deck nobody can read: too many words, type sized for a laptop at arm's length,
and no room left for a hand-drawn circle. A filming board sent to a prospect is a set of
headlines with no argument in them.

Build the board for the take. Build the artifact separately, from the same brief.

---

## What a frame holds

One frame carries **one piece of the spine** and nothing else. If the brief has 7 beats, the
board has 7 frames plus an anchor. A frame that does 2 jobs gets split, never compressed.

Measured off a real before-and-after, where a creator and their editor re-cut a machine-built
frame set by hand the morning of a shoot: **5 frames carrying 214 words became 7 frames carrying
151**, and 56 objects became 46. More frames, fewer words, bigger type.

So the working numbers:

- **About 20 words a frame.** Headlines and numbers. No subtitles, no captions, no footnotes,
  no small print. The creator is the explanation and they say it out loud.
- **If something has to shrink to fit, cut it instead.** Fewer things per frame, and the type
  gets bigger rather than smaller. This is the opposite instinct to a slide deck and it is the
  single most common failure in a machine-built board.
- **Labels that name what the viewer can already see go first.** A chart titled "the chart" is
  20 words of nothing.
- **3 of something is usually 2.** 3 problem chips, 4 numbers, 4 price rows all lost one in
  that re-cut and none of them was missed.
- **Ranges beat precision on camera.** "10 to 15 hours a week" reads and lands; "13.6 hours
  a week" invites arithmetic nobody can do while listening.

The honest version of the rule, from a creator killing a board that was content-correct:
*"Your work was fine in terms of content, but in terms of format and delivery, it's very hard
to deliver in an engaging way."* A dense frame is a frame that cannot be performed.

## What reads at 1080p

A viewer watching on a phone sees your 1920 x 1080 frame at roughly 400px wide. Nothing else
matters as much as this.

| Role | Size on a 1920 x 1080 frame |
|---|---|
| Absolute floor | 28px, and anything at the floor is probably a label that should be cut |
| Body | 32 to 40px |
| Headline | 60 to 90px |
| The hero number | 120px and up |

Frames are sized to **16:9** so they fill the recording with no letterboxing, unless you are
deliberately stacking (see the vertical layout note in `references/frame-craft.md`).

**Brand on canvas.** Map your palette from `content/brand.md` onto roles before the first frame,
and use the roles, never ad hoc colours:

| Role | Placeholder |
|---|---|
| Ink (all main type) | `{BRAND_INK}` |
| The fix, the "good" colour | `{BRAND_ACCENT}` |
| Pale panel behind a fix | `{BRAND_ACCENT_PALE}` |
| The problem, the "before" | `{BRAND_PROBLEM}` (a strong red works for most palettes) |
| Pale panel behind a problem | `{BRAND_PROBLEM_PALE}` |
| Dimmed, not-today, dead weight | `{BRAND_MUTED}` |

If your display font is not in the canvas tool's font list (`{BRAND_FONT_DISPLAY}` usually is
not), pick the nearest neutral sans once, write it into `content/brand.md`, and stop
rediscovering it.

Colour runs **louder on camera than on a page**. A brand palette tuned for a white HTML report
reads washed out through a screen capture and a compression pass. Brighter reds, brighter
greens. Keep the roles (one colour means the problem, one means the fix, one is dead weight
you are dimming) and push the saturation.

## Read this before designing frames

`references/frame-craft.md` holds the argument for why a canvas beats a slide list, the 6 moves
that only work on a canvas, the restraint rules that stop it inducing motion sickness, and
every ruling learned from real edits. Read it first. A frame set that would work just as well
as a scrolling web page has missed the point of being on a canvas at all.

---

## Build it from a spec, never by hand-placing items

Whatever tool you use, drive it from one JSON file and one builder script. Placing 90 objects
with 90 individual API calls is slow, unrepeatable, and impossible to diff when the creator
wants frame 4 changed.

The spec shape that has survived a lot of boards:

```json
{
  "board_id": "<your board id>",
  "frames": [
    {
      "key": "hook",
      "title": "01 - Hook",
      "x": 0, "y": 0, "w": 1920, "h": 1080,
      "items": [
        {"t": "shape", "shape": "round_rectangle",
         "content": "<p><strong>2x FASTER</strong></p>",
         "x": 640, "y": 650, "w": 620, "h": 200,
         "fill": "<pale panel hex>", "color": "<ink hex>", "size": 72,
         "key": "hook_fast"}
      ]
    }
  ],
  "connectors": [
    {"from": "hook_fast", "to": "hook_half", "shape": "straight", "stroke": "<problem colour hex>", "width": 5}
  ]
}
```

`key` is only needed on items a connector points at; the builder resolves keys to whatever ids
the tool hands back. The builder needs 4 behaviours and your AIOS can write it in one sitting:

1. **A `--dry-run` that prints the layout without touching the board.** Geometry bugs are
   cheaper to find in a table than on a canvas.
2. **Bulk creation wherever the API offers it**, falling back to single calls for item types
   the bulk endpoint refuses (images, usually).
3. **Idempotent repair.** Re-running the spec after a partial failure fixes the gaps rather
   than duplicating everything.
4. **A preview renderer.** Dump the same spec to a scrollable HTML page so the whole story
   reads in one scroll without opening the canvas tool. This is the fastest way to catch a
   frame that says nothing, and it costs one function.

---

## If you are on a different canvas tool

FigJam, Excalidraw, tldraw, a Canva whiteboard, even a long scrolling HTML page with a
frame-by-frame keyboard nav. Check 4 things before you commit, because every mechanic in the
Miro section below depends on them:

1. **Can you draw on it live, on camera, over the frames?** If not, stop. That is the whole
   reason this surface is not a slide deck.
2. **Does it present frame by frame, and can you reorder frames without rebuilding them?**
3. **Does it take hex colours on the objects you plan to use?** Sticky-note enums are a trap in
   more tools than Miro.
4. **Does it have an API worth using, and what is the editable-board ceiling on the free tier?**

A previous version of this ran on FigJam and needed a local bridge on port 3000, the desktop app
open and a plugin started by hand before a single frame could be created. That is a real answer
to the API question and it is why that version is gone.

---

## If you do not want to wire an API at all

**Build the board by hand. 7 frames of 6 objects is about 20 minutes** for anyone who knows the
tool, and the result is identical. The API pays for itself only when you are building a frame
set every week, or when you want the spec in git so a board can be rebuilt after somebody
deletes half of it.

The sane middle is to have your AIOS write the spec as a JSON file and a preview page, read the
preview, and then place the frames by hand from it. You keep the thinking and skip the OAuth.

---

## Our implementation is Miro, and here is exactly what that means

No pretending this is tool-agnostic. The mechanics below are Miro's, and a member on a
different canvas tool has real work to do.

**Any whiteboard that lets you draw live works.** Miro is named here because it is what this
was built and tested on, not because it is required.

**Auth.** The Miro REST API needs an OAuth access token. You create a developer app in your own
Miro account (free), give it `boards:read` and `boards:write`, and install it to your team. The
token is the key, there is no separate API fee, and the rate limits on the free tier are
generous enough that the ceiling you hit first is the plan's board count. Raw REST works with
the token in an `Authorization: Bearer` header. If you already use a tool-integration layer
that wraps Miro's OAuth for you, that works identically; it is optional.

**The free plan allows 3 editable boards.** Boards past that go view-only, and a view-only board
cannot be annotated on camera, which defeats the whole point. So: **one standing board, a fresh
frame set per video**, laid out in a new row well clear of the last one. Not one board per
video.

**What the API will not do for you.** Worth knowing before you plan around it.

- It cannot drive the presentation camera. Zoom and pan during a take are the creator's mouse,
  not a script.
- It cannot draw. Live annotation is a human with a pen tool in the browser. The API's job ends
  when the frames exist.
- It cannot add a font. Miro's font list is fixed, and your brand face is probably not in it.
  Ours is not; `plex_sans` is the nearest neutral. Losing the brand font is a real cost of
  leaving HTML and it is better to know that now than to discover it mid-build.
- Sticky notes cannot carry a brand colour. They take a 16-name enum (`gray light_yellow yellow
  orange light_green green dark_green cyan light_pink pink violet red light_blue blue dark_blue
  black`), no hex, and whatever your brand colour is, it is not in it. Shapes, frames and text all take hex. **Use
  shapes.**

**The 7 gotchas that each cost a session.** Every one found live, none of them in the docs.

- **2 coordinate systems, and mixing them throws a 400.** A frame's own position is relative
  to canvas centre. Anything parented into a frame is relative to that frame's top-left, with
  `origin: center` on the item. Inside a 1920 x 1080 frame, `x: 960` is centred and `x: -500`
  returns `new position is outside of parent boundaries`.
- **`fontSize` is a string on the single-item text endpoint and a number in bulk create.** Same
  field, 2 types.
- **Bulk create takes 20 items maximum and is transactional.** One malformed item fails the
  whole batch and creates nothing.
- **Deleting a frame orphans its children** rather than removing them, unlike the UI. Delete
  children explicitly or they pile up invisibly under the next frame. Listing a frame's children
  takes `parent_item_id`, not `frame_id`; pass the wrong name and it reports 0 children, which
  is how the orphaning happens in the first place.
- **Frames present in creation order, not left-to-right.** A frame that fails and gets rebuilt
  lands at the end of the running order. Repairing a frame in the middle of a row means
  rebuilding every frame after it too, or reordering by hand in the frames panel.
- **Images go on one call each, after the bulk calls.** Bulk create only takes an image by
  public URL, so a logo on disk goes through the single-item local-file upload endpoint (the
  absolute file path as the resource, the frame as parent, and width OR height, never both).
  Upload images after the bulk calls so they sit on top of their panels. Use real product logos,
  normalised to one square size, never a drawn imitation.
- **Transient 500s under sustained load.** A 15-frame build running alongside a delete sweep
  lost 2 frames and 1 bulk call and reported success. Always re-verify frame and item counts off
  the live board after a build. Never trust the builder's own "done" line.

**Pagination.** List the board's items with a `cursor`. Passing an explicit `limit` alongside it
returned nothing at all in our runs, silently, which reads exactly like an empty board.

---

## Check it before the camera turns on

You cannot see the rendered board from a script, and "it built without errors" is not the same
as "it reads". Run 2 geometry checks off the board's own item list:

- every parented item sits inside its frame bounds
- no item overlaps another inside the same frame

Then look at the preview page. Then say plainly that neither check tells you whether it reads at
1080p, and that nobody has watched it at video size yet. Do not imply a board is approved
because the geometry passed.

The last check is the creator's and it happens in the room: they click through the frame set
once, out loud, before recording. A frame they cannot talk over for 30 seconds is a frame that
is wrong, and it is always faster to find that out before the take.

---

## Where it hands off

The board link goes to the creator, who presents from it. Frames run in creation order and can
be dragged into a new order in the frames panel. After the recording, the raw footage goes to
whatever cutting skill you use, and any frame the creator drew all over is worth flagging to
the editor, because hand strokes mark the moments that mattered.

## Any page shown on camera follows the same rules

A web page, a table or a document shown on screen while you talk is an on-camera surface too.
A dense FAQ table with a full sentence in every cell cannot be presented from: there is too much
text to guide a viewer through. The shape that works:

1. **Recommendations first.** A few "if you are X" boxes, each with one big answer.
2. **Then a colour-coded table** (green, amber, red), 1 to 4 words per cell, with superscript
   note numbers.
3. **Then the nuance as numbered notes at the bottom, with clickable sources.** The same page
   becomes a resource to share afterwards, and the screen stays readable during the take.

## The maintenance rule

If you use this skill and find something not documented here, add it before you finish. One line
each. Past 10 items, fold them into the body above.

A correction from the creator lands where the next session will see it, in the same session.
A fix that only touches today's video says so out loud and says why.
