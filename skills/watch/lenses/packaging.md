# Lens: packaging

The whole package as a viewer meets it: thumbnail, title, first frame, first line,
and whether the 4 agree with each other.

This is the lens for a link, a thumbnail or a creator dropped into a conversation
with no other instruction. **The verbatim capture happens first, before any
analysis.** The reason somebody sent it is the taste; the link is only a pointer,
and the reason is the half that gets lost.

## Before you run

1. Append the entry to `content/taste/packaging/inbox.md`, with `by:` naming
   who sent it and `why (verbatim)` carrying their exact words. Mark
   `teardown: pending` until the file exists. How a taste file works and why it
   belongs to you rather than to the skill is in
   `content/reference/taste-system.md`.
2. Read `content/taste/thumbnails.md`. This lens produces evidence for it, never
   a second copy of it.
3. Pull the thumbnail itself down next to the teardown. On YouTube,
   `i.ytimg.com/vi/<id>/maxresdefault.jpg` is the same pixels yt-dlp would fetch.
4. Run the script with `--hook`, so the open is pinned at 2 fps.

## The bar

A teardown is good when somebody could rebuild the thumbnail without ever seeing
it: the actual colour family, the layout top to bottom, where the eye goes first
and second, and what carries the click when there is no face in the frame.

Most teardowns fail at the same place, and they usually admit it in a line like
"no frames were pulled, so the intro analysis is from the words alone". **That
gap is what this skill exists to close.** You have the frames. Use them.

## Output

## <creator> - "<title>": one video, taken apart

Open with the metadata line: channel, publish date, runtime, views at time of
writing, where the thumbnail sits on disk, which route the transcript came from.
Then **the sender, verbatim**, with their exact reaction quoted.

1. **The thumbnail, as seen.** Layout top to bottom. Colours as families, not
   guesses at hex unless you can read them. What the eye does first, second,
   third. What carries it if there is no face. Any craft detail someone chose on
   purpose.
2. **The title.** What it promises, what kind of promise it is, what it withholds.
3. **The first frame.** From the pinned 0:00 frame, not from imagination. Does it
   continue the thumbnail or contradict it.
4. **The first line.** Verbatim from the transcript, with the timestamp.
5. **Do the 4 agree?** Thumbnail, title, first frame, first line. Name any place
   a viewer would feel a seam.
6. **The mechanics.** Numbered, each one named as a thing that could be run again.
7. **What this shares with the corpus, and what is new.** Compare against the
   teardowns already in `content/taste/packaging/`. A mechanic that is already a written
   rule gets cited, not restated.
8. **What we would have to change to run it.** Honest. Some of these do not
   transfer to your audience, and saying so is the useful part.

## After

Write the file to `content/taste/packaging/<slug>.md`, update the inbox entry's
`teardown:` line, and **only then** consider whether `content/taste/thumbnails.md`
should change. A rule
needs the pattern in more than one place; one video is evidence, not a rule.

---

Rules for this lens:

- Every visual claim comes off a frame you actually read. If you did not pull a
  frame for a moment, do not describe that moment.
- Quote the reaction verbatim. Never smooth it.
- Never invent a logo, a colour or an on-screen word. If you cannot read it at
  512px, re-run that timestamp with `--resolution 1024` and read it properly.
