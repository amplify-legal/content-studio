# Platform craft

Most of the writing rules in `SKILL.md` hold anywhere a person reads words. This file holds the
part that is true because of how a specific feed works. Where a rule is LinkedIn-specific, it
says so, and it says what the equivalent is elsewhere.

Platforms change their own mechanics without telling anybody. Treat everything here as the
current shape rather than a law, and re-check anything that starts behaving oddly.

---

## The first line and the fold

**LinkedIn.** The feed shows roughly the first 2 or 3 lines of a post and hides the rest behind
"see more". The exact cut moves with the device, the app version and whether media is attached,
so the only safe assumption is that the first line is the whole post until somebody taps.

What follows from that:

- **The first line has to work alone.** Not as a title, not as a setup for the sentence after
  it. As the thing that makes a tap worth it.
- **Never split a hook across the fold.** "I have woken up in the middle of the night worried
  about" reading as a half sentence in the feed is a post nobody opens.
- **Never spend line 1 on context.** The context goes after the tap. A post that opens with
  "Last week I was at a conference and" has used its only free line on scene-setting.
- **A blank line after the opener costs you nothing and buys whitespace.** It also pushes the
  "see more" right where you want it, at the point of maximum curiosity.

**Elsewhere.** An Instagram caption truncates at roughly 125 characters with the same effect. X
has no fold inside a post, so the constraint becomes the character limit itself and the first
post of a thread carries the same job. An email has 2 folds, the subject line and the preview
text, and both are read before anything else. A newsletter's first sentence is its fold.

---

## Line breaks and whitespace

**LinkedIn.** People read this feed on a phone, with one thumb, between other things. A wall of
text gets scrolled past before it gets judged.

- 1 to 3 sentences a paragraph, then a blank line.
- Single-sentence paragraphs are normal here and look deliberate rather than sparse.
- A long post is fine. A dense post is not. The same 300 words broken into 9 paragraphs get read
  and broken into 2 do not.
- Do not simulate rhythm with a chain of 4-word fragments on their own lines. It reads as an
  imitation of a certain kind of influencer, and the writing rules in `SKILL.md` ban it anyway.

**Elsewhere.** The same is true on Instagram and in email. It is the opposite on X, where
whitespace inside a single post wastes characters that are already scarce.

---

## Length bands

**LinkedIn** allows about 3,000 characters, which is far more than anybody should use by
default. The bands that work:

| Kind of post | Length | Why |
|---|---|---|
| Reflective, seasonal, encouragement | 80 to 150 words | The feeling is the whole payload. More words dilute it |
| A single point or a buyer question answered | 150 to 250 words | Long enough to be useful, short enough to finish on a phone |
| A story with dialogue or named people | 300 to 400 words | The story earns the space |

Length never signals effort. A post padded to look substantial reads as padded.

**Elsewhere.** X gives 280 characters a post, so the band becomes the thread length. Instagram
allows 2,200 caption characters and rewards far shorter. Email has no limit and the same
discipline applies anyway.

---

## The carousel

**LinkedIn.** A carousel is a document post: a PDF uploaded to the feed, which renders as a deck
the reader swipes through. It is the one format that holds somebody on a single post for more
than a few seconds, and the platform can tell you which slide they stopped on.

The shape that works:

- **6 to 8 slides.** One idea a slide, nothing more.
- **The cover carries the promise** in a few large words. It is doing the job the hook line does
  on a text post, so it gets the same care.
- **Slides 2 to 7 carry keywords and structure, never paragraphs.** If a slide needs to be read
  rather than glanced at, it is 2 slides.
- **The last slide carries the single call to action**, and where to find the longer thing.
- **The caption is still a post.** Every rule in `SKILL.md` applies to it. A carousel with a
  throwaway caption wastes the format.

**Elsewhere.** An Instagram carousel is images rather than a document, up to 20 of them, and the
first image does the job of both the cover and the hook line. On X the equivalent is a thread,
where each post has to stand alone because people arrive mid-thread. There is no carousel in
email, and the equivalent is a short piece with subheadings the reader can skim.

---

## Native video posts

**LinkedIn.** A video uploaded to the feed (rather than a link to it elsewhere) has 4 traps, each
found the hard way:

- **The custom thumbnail matches the video's own pixel dimensions, not just its aspect ratio.**
  A 1280x720 thumbnail on a 1920x1080 video was refused with a generic error that named neither
  the thumbnail nor the size. Re-rendered at 1920x1080, it posted first time. So a thumbnail
  builder takes its size from the video rather than defaulting to 720p. (YouTube's own
  thumbnail stays 1280x720, which is what YouTube wants.)
- **Add the thumbnail only after the video's upload bar reaches 100%.** Adding both at once has
  stalled at 0% with a correctly sized thumbnail, and the same video moved the moment the
  thumbnail was left off. If it still stalls after 100%, try the same picture as a PNG, then as
  a lighter JPEG, before changing anything else. Why it stalls is not known.
- **The thumbnail cannot be changed once the post is live.** So "post first, add the thumbnail
  after" is never an option. If every custom thumbnail stalls, render the video with the
  thumbnail image as its first second; the feed has been seen to use that frame as the cover.
- **A generic error does not mean nothing posted.** The feed has accepted several retries while
  still showing "we encountered a problem". After any publish that took more than one attempt,
  open the profile, count what is actually there, and report duplicates to the creator. Deleting
  is their call.

**Finding the cause of a refused upload.** Post the smallest honest version of the same thing
first: a 60-second cut of the same encode. If it goes up, the account, the session, the composer
and the text are all ruled out in one move, and only the variables that differ are left. Then
add those back one at a time. A smaller file is not the same test as a smaller clip.

**Audio.** 48 kHz is the safest audio rate to hand any platform, and converting is a single
stream copy of the video with the audio re-encoded. Treat it as a precaution: in the case above,
a 96 kHz file was suspected, rebuilt at 48 kHz, and failed in exactly the same way.

**Instagram Reels.** At the time of writing: 48 kHz audio at most, a 2,200-character caption, and
very long Reels are not shown to people who do not follow you. Check the current limits on
Instagram's own help pages before a long upload.

**YouTube Shorts.** A thumbnail set through the API does not show on a Short. Pick the cover by
hand in the app.

**A publish is proven by reading the surface back**, never by the composer going quiet. For a
scheduled upload that means the platform reports the video processed with a real duration, not
that a row appeared in a list.

---

## Links

**Everywhere.** A link carries `https://` on the front. Without it, the app decides whether the
text becomes a link, and the same message has linked on one domain ending and stayed plain text
on another in the same app. A whole batch of messages can go out holding a correct address that
does nothing when tapped.


**LinkedIn.** An external link in the body of a post reliably reduces how many people see it,
because the platform would rather people stayed. The workaround everybody uses: post without the
link, then put the link in the first comment.

How to point at it without sounding like bait:

- One plain line in the body saying the link is in the comments. That is all it needs.
- Post the comment yourself, immediately, before the post gets any reach.
- Never turn it into a keyword game. "Comment WORD and I will send it to you" asks the reader to
  perform for a thing you could just give them, and the buyers who read without ever commenting
  are exactly the people who will not play along.

**Elsewhere.** The same suppression is real on Instagram, where links do not work in captions at
all, so the answer is the profile link. X tolerates links better than it used to but a thread
still travels further with the link in the last post. In email, the link goes in the body where
it belongs, and burying it is the mistake.

---

## 2 people posting about the same thing

**Everywhere.** When co-hosts or partners both post about one event, launch or video, most of the
people who follow one of them follow both. 2 posts with the same announcement in 2 voices still
read as one announcement twice.

- The second post gets its own hook, its own structure, and at least one thing only that person
  can say.
- **The check is mechanical: 0 shared 5-word phrases between the 2 posts.** A short script that
  lists every 5-word sequence in each and prints the overlap does it in a second.
- Measure against what actually posted for the first one, never the draft that was handed over,
  because people edit on the way in.

---

## Scheduling tools and reach

**Everywhere.** At the time of writing, no controlled study has found that posting through a
scheduling tool or a platform's official API costs reach compared with posting by hand, and the
platforms' own teams say it does not. Most of the studies were paid for by scheduling vendors,
so treat that as an absence of evidence rather than proof.

What does measurably cost reach: another app's watermark on a video, an external link in the
body of a post on some feeds, mostly reposting other people's content, and stuffing hashtags.
Replying to comments in the first hour after posting is the lever that reliably helps.

---

## The call to action mix

**Everywhere.** 80% of what gets posted sells nothing. 20% carries a call to action. That ratio is the
single most broken rule in this whole file, and the failure is always the same: somebody posts 5
times, pitches in 4 of them, gets nothing, and concludes that posting does not work.

Inside the 20%:

- **One call to action a post.** A post that asks for a booking and a follow and a download asks
  for nothing.
- **The story posts end at the problem.** They are not soft pitches, and they are not building
  toward anything. That is what makes the 20% land later.
- **Match the ask to the temperature.** People who have read 4 of your posts will read a 5th.
  They will not book a call because one post asked them to.

**LinkedIn-specific.** Comments are a weak proxy for reach here, because a large share of the
people you want are lurkers who read everything and comment on nothing. Judge a post by profile
visits, by who appears in the inbox 3 weeks later, and by who mentions it on a call. Do not
rewrite the strategy because a good post got 4 comments.

---

## Cadence

**Everywhere.** Consistency beats quality. 2 posts a week for 6 months beats 12 excellent posts
scattered across a year, and it is not close. The feed forgets faster than anybody expects.

Pick the cadence the creator can actually hold in a bad week, not the one they can hold in a
good one.
