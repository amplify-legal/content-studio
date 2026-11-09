# Content lessons that cross every lane

> Installed to `content/reference/lessons.md`. The durable rules a working content system paid for, written as generic rules. Each one exists because something went wrong once. They apply to every format: long form, shorts, posts and pages. Lane-specific craft lives in `content/reference/podcast-edit.md`, `content/reference/workshop-edit.md` and `content/reference/long-form-lessons.md`. Your own taste lives in `content/taste/` and `content/taste/lessons.md` is where your own lessons go.

---

## Publishing

### 1. A native LinkedIn video's custom thumbnail matches the video's pixel dimensions, and goes on after the upload reaches 100%

- **Match the video's own pixel dimensions, not just its aspect ratio.** A 1280x720 thumbnail on a 1920x1080 video failed the whole post with a generic error that named neither. Re-rendering the same thumbnail at 1920x1080 posted first try. A thumbnail builder takes its size from the video rather than defaulting to 720p. (YouTube thumbnails stay 1280x720, which is what YouTube wants.)
- **Order matters.** Add the video, wait until its upload bar reaches 100%, and only then add the thumbnail. With the thumbnail added early, 2 uploads sat at 0% and posted nothing even with a thumbnail that already matched the frame; without it, the upload ran. Why is untested. If it still stalls, try the same picture as PNG, then as a lighter JPEG, before anything else changes.
- **Never "post first, add the thumbnail later".** A LinkedIn video's thumbnail cannot be changed once the post is live.
- **The fallback when every custom thumbnail stalls** is a render with the thumbnail as the video's first second. LinkedIn showed that frame as the cover on the post where it was measured.
- If you post through an official API rather than the composer, check whether that route can carry a custom video thumbnail at all. If it cannot, refuse the leg rather than drop the thumbnail. The posting module's LinkedIn adapter carries it through LinkedIn's own Videos API and refuses a video leg with no thumbnail (`posting/README.md`).

### 2. A publish is proven by reading the surface back, never by the composer going quiet

- **A generic refusal can be untrue about the outcome.** A platform kept showing "We encountered a problem sharing your post" while it was accepting several of the retries. 4 near-identical copies ended up live.
- **After any publish that took more than one attempt, read the profile or channel back and count what is actually there**, before recording it as done.
- **Deleting a duplicate is the human's call.** Report the count; never tidy it yourself.
- On YouTube, proof of an upload is the processing status reading succeeded plus a real duration, never a row appearing in a listing.

### 3. Diagnose an upload failure with the smallest honest clip of the same encode

When a platform refuses an upload with a generic message, **post the smallest honest version of the same thing first**: a 60 second cut of the same encode, same settings. If it goes up, the account, the session, the composer and the text are all ruled out in one move, and only the variables that actually differ are left. Then add back one variable at a time. That turned an hour of guessing into one answer.

### 4. A claim about how a tool behaves is quoted from what implements it, or labelled untested

- **48 kHz audio is a precaution, not a diagnosis.** One session found the edit pipeline writing 96 kHz audio, asserted the platform's spec did not accept it, and rebuilt at 48 kHz. The 48 kHz file failed in exactly the same way, and no spec page was ever cited. 48 kHz is still the safer rate to hand any platform, and the rebuild is one stream copy (`-c:v copy -c:a aac -ar 48000`), so keep doing it. But do not call it the fix.
- **The general rule:** any statement about how a tool, a page or a platform behaves is quoted from the file, the doc or the measurement that shows it, with the source named, or it says "untested". Keep wrong claims in your notes as corrections rather than deleting them, so the next session does not re-derive them.

### 5. Upload caps are per toolkit

The same 376 MB file was refused by one connector's Google Drive upload with a payload-too-large error, while a YouTube multipart upload through the same kind of connector took a 394 MB file. **A size cap is a property of the specific tool route, not of the file or the platform.** When a big file must reach Drive, use a resumable upload session and send the bytes directly.

### 6. On-camera promises are live URLs before the video publishes

If a video says "link below", "a free resource", "the prompt", "no email needed", then **every one of those promises is a live URL in the description, fetched and returning HTTP 200 in the launch session.** An open flag in a description file is not a gate. The launch step greps the take notes for every on-camera promise and checks each against the description itself. Before calling a resource missing, search your own records for it: in the incident that made this rule, the resource had been live for days and the description writer did not know it existed. Somebody cancelled an appointment because they thought the video was clickbait.

### 7. On a recorded call, never a live CTA date and never a real contact's name on screen

A peer call can describe the stack and the price. It never shows a date that will be stale by the time the video is watched (that turns the video into an expired ad), and never puts a real contact's name on screen (that is somebody else's privacy, in a file that never comes back down).

### 7b. Every post of a short links the full video in its comments, and the short never waits for the link

On every platform: the first comment on a written-platform post, a comment under the reel and the short, the first-comment text on a hand-posted card. **The short goes out on its slot even when the full video is not live yet; the link is added the day the full video goes live**, and the plan keeps a list of shorts still owed a link so none is forgotten. Why: shorts once rolled from week to week waiting on episodes that were not out, and the creator ruled that the short going out matters more than any one element of it, while the work keeps moving toward every post carrying everything (2026-11-04; it replaced an earlier "hold the short until the link exists" rule). The exception is the creator's to name per launch: when a long video is meant to lead, its shorts wait behind it, and that order is written on the plan.

### 7c. A guest on a podcast short is added as a collaborator, and the invite is actually delivered

Where a platform supports collaborators, every short or clip from an episode carries the guest as collaborator. Check how the platform delivers the invite: one platform sends the guest no notification and only creates a link ("active after you save") that has to be emailed to them, so a guest's team once waited 5 days on an invite that existed only as an unsent link.

### 7d. Before a machine posts, it proves the connected account is the creator's own

2 shorts once went out on a co-host's profile instead of the creator's: the poster called the platform without naming an account, and a second account linked to the same tool answered. Why: a post on the wrong profile cannot be moved, only deleted, and deleting is a person's call. The fix: read the connection's own identity (the platform's "who am I" call) before the upload and refuse when it belongs to anyone but the creator; with several accounts on one tool, name the account on every call (2026-11-06).

### 7e. A hand-posted video is marked posted only by reading the channel back

A board once called 3 published videos unposted, because the editor uploaded them by hand in the platform's own studio and nothing read the channel afterwards. Why: a status that only the machine's own posts can update is wrong every time a person posts. The day's page reads the channel and marks a row posted when its video is public (2026-11-06).

### 7f. An approval counts once it reaches the copy the poster reads

Approvals made on a second computer never reached the computer that posts, because that machine had stopped syncing 2 days earlier; their slots passed unposted. Why: an approval in a file nobody posting can read is no approval. Before a slot, the poster's own copy is checked for the approval, and a sync that has gone quiet for a day is a fault someone hears about (2026-11-06).

### 7g. Decide the mix before the upload: a platform file cannot be swapped

A video was uploaded private, then the creator wanted music under it. YouTube Studio offers trims, blurs and its own audio library on an uploaded video, but no way to replace the file with a new render (as found in Studio, untested through the API), so the only route was a new upload and a new link. Why: a link that has already gone out somewhere points at the old file. Music, the final mix and the cover are settled before the first upload (2026-11-06).

### 7h. A testimonial carries a name only with that person's permission on file

On a testimonial wall or any page quoting people, a name comes off until an explicit yes is recorded, unless the words are ones the person posted publicly themselves. A hidden name shows the role and the shape instead ("operations lead, a 40-person accounting practice") and stays in your own records so one flag restores it. Why: words from an email, a DM, a call or a private community post were said to you, not to the public. A request to include somebody is a go to show their words anonymized, never a go to show their name (2026-10-28).

### 7i. A cause in a script is sourced, or said as your own reading

A reel's script had a beat implying a new technology caused a company's collapse. No report named it as a cause, so the beat had to be said as an implication ("now imagine adding X"), never as the reason. Why: a cause stated as fact is a claim a viewer can check, and one unsupported cause costs the whole video its credibility. Every "because" in a script carries a source or is phrased as the creator's own view (2026-11-05).

### 7j. A number on a cover says exactly what was counted

A cover read "we had 40 conversations with founders", but the 40 calls included coaches, assistants and repeat callers. The count was flagged to the creator before posting. Why: a viewer who knows the field reads the number literally. Either the number counts only what the words say, or the words change to fit the number ("40 calls") (2026-11-05).

### 7k. A live apply lists every write it plans, and a kind of write nobody asked for is held

A run sent to fix one video's description would also have uploaded a caption track, because the video's pack carried a captions file path. It was caught in the dry run. Why: an ask for one change is not an ask for everything the tool can do in the same call. The dry run prints every write by kind (description, tags, captions, playlist), and a kind the run was not asked to make is held and asked (2026-11-04).

---

## Privacy and frames

### 8. Every frame pulled from a recording is checked at full resolution before it can be posted

Check for **attendee faces and name labels, client names, and private UI behind the work** (sidebars, conversation titles, file paths, tab strips, address bars, notification badges). A frame cleared as "clean, no names anywhere" carried an uncleared attendee's face and name in a webcam tile, and a second carried an undimmed sidebar of private conversation titles. **Where the recording is a screen share with a webcam column, cropping the column off is usually the whole fix.** Clients are described by shape in videos, never named.

### 9. A workspace surface going on camera is rebuilt clean, never the real page blurred in motion

Copy the real page's own file so the layout is identical rather than imitated, replace every person's name with who they are ("a podcast host"), remove every client name, replace every figure with one of the same shape, and **record that copy**. It scrolls and moves like the live thing, and there is nothing private in the file to leak.

The alternative was rejected on measured failures, all in `content/reference/workshop-edit.md` section 7: a layout hand-off timed to the half second let 10 frames of unblurred faces through; a 1.8 second exposure survived an OCR sweep sampling every 5 seconds; over-blur smeared about 90 of 800 seconds of teaching; and `boxblur` radius caps fail silently. A still has none of these, because one frame is checked once.

**2 checks before the copy is recorded:**

- **Read the rendered text, never one tag.** A heading grep on a live page found 1 item where 3 were on it, because the titles sat in a styled class the grep could not see. Strip the tags and read the text (`sed -e 's/<[^>]*>//g'`, or a page-text tool).
- **Read the HTML comments.** A published page carried 3 workspace paths and a contact's name in a build comment, one right-click from its audience.

Then the full-resolution frame check (rule 8) runs on every captured frame, and **a separate reviewer clears the set**, because the person who built the copies is the wrong person to clear them.

### 10. The consent test is seen, heard or named

A third party who is not **seen, heard or named** in a cut needs no consent: there is nothing of theirs in it. Where their speech genuinely makes the cut better, keep it and **anonymise the voice**: a pitch change on their voice only (ElevenLabs or your equivalent voice tool), nothing that sounds creepy. The full-resolution frame check for faces, names and private UI still runs.

---

## Review

### 11. Cut-review runs before any cut reaches the person

A staged cut, from any builder, spin-off or pipeline, goes through `cut-review` before it is put in front of the creator, whatever question is still open about it. **The open question rides with the review; it never replaces it.**

### 11b. A short goes on the posting plan only after the creator has seen it or cut-review has cleared it

Shorts once went onto a plan before the creator had watched them, and the creator had to hold the week. Approval is the gate once posting is automated, so nothing reaches the plan unseen.

### 11c. The director runs before every recording

Every recording plan and recording session runs the `director` (on a podcast, see 11k; the 7 questions in `content/taste/director.md`, asked only where the brief has not answered them), and the frame is written into the brief before the camera turns on. Every cut review, edit session and planning page reads the kind's sheet (`content/taste/kinds/<kind>.md`) and the newest lines from the review calls first. Why: an edit with no written frame is judged against whatever the reviewer likes that day; the frame gives the edit, the review and the packaging one thing to serve. A line repeated 3 times on review calls is put to the creator to promote; the machine never promotes it to a rule itself.

### 11d. A pass that rejected nothing is not a verdict on taste

2 options once passed every mechanical check and the creator rejected both as "way too basic", built without awareness of the taste files. A cut the creator rejected stays rejected until they accept a revision against a reference they picked.

### 11e. One board per round, letters never reused, and the board named when asking for a letter

The creator picked option C from the first cover board; the session built the C from the second board, which was a different picture. Why: a letter that names 2 things across 2 boards makes the creator's pick ambiguous, and the wrong one gets built. Every option on every board in a series has its own letter, and a question names the board and the letter together (2026-11-05).

### 11f. Build what was asked; offer the rest

The creator said they wanted to add music to a short themselves, in their own app; a session rendered 2 music versions for them instead. The creator asked the session to wait for the ask next time. Why: unasked work spends the creator's attention at the moment they were deciding something else. A good idea for an extra version is one line offered, then built on a yes (2026-11-06).

### 11g. An independent review repeats until one comes back with nothing blocking, and every repeat checks each folded fix on the new render

On one episode an independent reviewer read 4 versions. Of 13 fixes folded into version 2, 6 had not reached the render: a level change written into the notes while the step that writes the levels file was never re-run, a music bed that ran out under the title card, a compressor that still flattened the laughs. Why: "fixed" in the notes is not fixed in the file. Each repeat lists every fix from the round before and checks it on the new render, by frame or by measure (2026-11-05).

### 11h. Options put to the creator are 3 good ones, none with a known fault

An option with a fault the builder already knows about is fixed or dropped before the creator sees it. Why: the creator's pick is spent on choosing between good things, not on spotting the machine's mistakes. 3 options of each thing the creator picks (trailer moments, frames, music), each one finished (2026-11-04).

### 11i. A video the creator never watched is not a reference either way

A finished video that went out without the creator ever watching it is neither a model to copy nor a mistake to avoid, until they watch it and say. Why: copying it makes the machine's unreviewed choices into taste (2026-11-04).

### 11j. A format new to the system is learned from real winners before it is built

The first carousel was a video frame as the background, a dark box and 50 to 80 words per slide; the creator rejected it as a pile of screenshots with too much text. Why: a format built from the machine's idea of it looks like the machine's idea of it. Before the first one, study carousels that actually performed in your niche (what each slide carries, how few words, the type size on a phone), then show 5 designs that differ on a real axis, side by side, labelled; the creator picks (2026-11-04). The rejection and the rules go in `content/taste/carousels.md`.

### 11k. On a podcast, the conversation comes first

The prep for a podcast goes into making the conversation valuable for the guest: good questions built on what you know about them and the last time you spoke. What the audience gets is a bonus when something good can be given or pointed out. Why: a great conversation is valuable to the audience on its own, and a host steering for audience takeaways interrupts it. The director's audience questions are never a gate on a podcast recording (2026-11-04).

### 12. The end-of-run review is a separate reviewer

Every video's end-of-run review is a separate sub-agent reading the whole conversation, never the session reviewing itself.

### 13. Green is not done

A self-verifying render loop never promotes a finding's tier, a script repairs only what is in its bounded table, and taste stays the creator's. A clean battery means the file is worth a person's time; done is the person having watched it. See `content/reference/verify-loop.md`.

---

## Rendering

### 14. Long renders run detached, and every `-loop 1` input carries an explicit `-t`

- **Long renders run detached** (`scripts/render_detached.sh`) with a watcher beside them, never as a conversation background task. Several overnight go through `scripts/render_queue.sh`.
- **Any `-loop 1` image input carries an explicit `-t`**, or ffmpeg encodes duplicate frames until the disk or the kernel stops it, which looks exactly like running out of memory at "98%".
- Read `content/reference/render-reliability.md` when anything renders.

### 14b. Render limits differ by day and by night, and a low disk freezes a render instead of killing it

By day the creator is using the machine: allow 1 render and 2 heavy jobs, and hold a new render under 30 GB truly free or at real memory pressure. By night, idle: allow 3 renders and 4 heavy jobs. A running render is frozen (SIGSTOP) under 15 GB free and resumed (SIGCONT) at 25, never killed. Read the disk as the free blocks `df` reports, never the "available" number that counts purgeable space, which is what the file manager shows. Why: one machine panicked while the file manager showed 50 to 66 GB available and the kernel could not find room for a new swap file; and earlier, a gate on swap used alone held a render for hours on a machine with room to spare (2026-10-27). The numbers are one machine's starting defaults; set your own.

### 14c. A render watchdog watches the output size and the CPU together

A render that has stalled shows a file that stopped growing and an ffmpeg at 0 CPU. When both are flat for 20 s, kill that piece and retry it (4 tries for a piece, 3 for a finalize pass). Why: one machine hung pieces at their final flush only when they ran in their own session, which is how a detached runner starts a job; a watchdog on size alone or CPU alone either missed it or killed live work (2026-11-05). Detail: `content/reference/edit-lab/privacy-and-pipeline.md` B16.

### 15. Video pages are served over a Range server, never opened as files

A review board or handover page with `<video>` elements does not play its relative video files when opened as a file in an embedded browser pane, and a sandboxed snapshot of the page cannot reach them either. **Serve the folder over localhost with a server that answers HTTP Range requests** (206 Partial Content): `python3 scripts/serve_outputs.py` serves `outputs/` on port 4200 by default (pass another port as the first argument), then open `http://localhost:4200/<path under outputs/>`. A plain `python3 -m http.server` does not answer ranges, and Chromium's player needs them to start and seek an mp4. Opening the file in the user's own default browser also works for local files. Put the URL and the absolute file path in the hand-over line.

---

## The meta rule

### 16. A correction lands where the next session will see it, in the same session

When the creator corrects something, the fix goes into the skill, the taste file or a check script **in the same session**, and the work log names where it went. A fix that only touches today's episode says so out loud and says why. A caption floor once lived inside a single episode's build script; 3 days later the same fault shipped on 12 of 15 renders, because nothing outside that episode could see it. **A rule that keeps getting broken becomes a check, not a longer paragraph.**
