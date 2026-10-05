# Editing checklist (starter)

The mechanical layer. Every line is a yes/no with a timestamp.

**This file is data, and it belongs to you, not to the skill.** The skill is the engine that
runs a checklist; what is on the checklist is your taste, and it gets better every time a
review finds something this list did not. Grow it from real reviews: a miss that repeats
becomes a new line, dated. How a taste file works, and why the skill never restates it, is in
`content/reference/taste-system.md`. Your live copy is `content/taste/editing-checklist.md`;
this file is the starter it was seeded from.

Delete anything here that does not match your format. A checklist you do not believe gets
skipped, and a skipped checklist is worse than a short one.

## On-screen text
- [ ] On-screen words minimal, keywords and structure, never sentences. If a card reads like
      a subtitle, cut words until it doesn't
- [ ] Capitalization consistent across every card, banner and title (pick one convention per
      video, sentence case is the safe default)
- [ ] Number formats consistent and correct for the audience's locale (`$5,000` not `$5.000`,
      `1,000,000` not `1.000.000`, and the right date order on screen)
- [ ] Nothing under 44px when read at phone size (render a frame at 375px wide and read it)
- [ ] No spelling errors in any card, lower third or title
- [ ] **Spoken options appear on screen.** Whenever the speaker says "path A or path B" or
      "you have 3 options", the options show up as a few words, animated if there is
      bandwidth. Grep the transcript for "option A / path A / 2 options / 3 options /
      either ... or" and confirm each one has a counterpart in the cut
- [ ] On-screen text for quoted speech inside a long-form (a recorded call, a line being read
      out) is 2 or 3 word phrases, never one-word karaoke. One word flashing is too much

## Structure
- [ ] Opening is on camera, 0:00 to 0:05
- [ ] Step arrows or progress markers present on tutorials, so a viewer scrubbing knows the
      shape
- [ ] Every visual change is purposeful. No cut, zoom or card without a reason, and motion
      for motion's sake fails the check
- [ ] Sections end with a beat of tail, not a hard chop on the last syllable

## Audio
- [ ] Loud moments tamed (check `volumedetect` max_volume)
- [ ] Music bed sits under the voice, not over it
- [ ] No clipped word at the head or tail of any cut

## Call to action
- [ ] Exactly one CTA, never stacked asks
- [ ] Placed where the brief says (the creator's recorded placement), not where a template
      defaults to
- [ ] No subscribe interruptions mid-argument. The retention curve is the ask

## Delivery
- [ ] `+faststart` set (the file opens instantly in a player and on socials)
- [ ] A/V sync: video stream duration matches audio, drift under one frame
- [ ] Correct aspect ratio and resolution for the destination
- [ ] On a 9:16 short, nothing in the platform's action rail or the top and bottom bands
      (`check_safe_area.py`: no ink above y=200, below y=1500, or right of x=940 from y=960
      down, and no face whose mouth and chin sit below y=1500)
- [ ] Captions pass the size gate (`check_caption_size.py`)
- [ ] Audio delivered at 48 kHz (a safe rate for every platform; one stream copy fixes it:
      `-c:v copy -c:a aac -ar 48000`)

## Privacy
- [ ] Every frame that will be posted as a still checked at full resolution: no attendee
      faces, name labels, client names, or private interface (sidebars, conversation titles,
      file paths, tabs, notifications)
- [ ] On recordings with other people or private screens, exposures swept at 1 second or
      finer
- [ ] A third party who is heard in the cut and has not consented: voice anonymised with a
      pitch change on their voice only, face and name gone. One who is not seen, heard or
      named needs nothing
- [ ] Every on-camera promise ("link below", "free resource") listed for the launch step

## Added from real reviews

Date each addition and name where it came from. 2 lines to start you off, both from live
review calls:

- **Spoken options go on screen** (see the on-screen text section). Stated as standing after
  a review where the speaker offered 2 paths out loud and the screen showed neither.
- **Quoted speech is phrased, not karaoke.** 2 or 3 word phrases. The verbatim complaint was
  "one word flashes, that's too much".
