# Content lessons that cross every lane

> Installed to `content/reference/lessons.md`. The durable rules a working content system paid for, written as generic rules. Each one exists because something went wrong once. They apply to every format: long form, shorts, posts and pages. Lane-specific craft lives in `content/reference/podcast-edit.md`, `content/reference/workshop-edit.md` and `content/reference/long-form-lessons.md`. Your own taste lives in `content/taste/` and `content/taste/lessons.md` is where your own lessons go.

---

## Publishing

### 1. A native LinkedIn video's custom thumbnail matches the video's pixel dimensions, and goes on after the upload reaches 100%

- **Match the video's own pixel dimensions, not just its aspect ratio.** A 1280x720 thumbnail on a 1920x1080 video failed the whole post with a generic error that named neither. Re-rendering the same thumbnail at 1920x1080 posted first try. A thumbnail builder takes its size from the video rather than defaulting to 720p. (YouTube thumbnails stay 1280x720, which is what YouTube wants.)
- **Order matters.** Add the video, wait until its upload bar reaches 100%, and only then add the thumbnail. With the thumbnail added early, 2 uploads sat at 0% and posted nothing even with a thumbnail that already matched the frame; without it, the upload ran. Why is untested. If it still stalls, try the same picture as PNG, then as a lighter JPEG, before anything else changes.
- **Never "post first, add the thumbnail later".** A LinkedIn video's thumbnail cannot be changed once the post is live.
- **The fallback when every custom thumbnail stalls** is a render with the thumbnail as the video's first second. LinkedIn showed that frame as the cover on the post where it was measured.
- If you post through an official API rather than the composer, check whether that route can carry a custom video thumbnail at all. If it cannot, refuse the leg rather than drop the thumbnail.

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

### 15. Video pages are served over a Range server, never opened as files

A review board or handover page with `<video>` elements does not play its relative video files when opened as a file in an embedded browser pane, and a sandboxed snapshot of the page cannot reach them either. **Serve the folder over localhost with a server that answers HTTP Range requests** (206 Partial Content): `python3 scripts/serve_outputs.py` serves `outputs/` on port 4200 by default (pass another port as the first argument), then open `http://localhost:4200/<path under outputs/>`. A plain `python3 -m http.server` does not answer ranges, and Chromium's player needs them to start and seek an mp4. Opening the file in the user's own default browser also works for local files. Put the URL and the absolute file path in the hand-over line.

---

## The meta rule

### 16. A correction lands where the next session will see it, in the same session

When the creator corrects something, the fix goes into the skill, the taste file or a check script **in the same session**, and the work log names where it went. A fix that only touches today's episode says so out loud and says why. A caption floor once lived inside a single episode's build script; 3 days later the same fault shipped on 12 of 15 renders, because nothing outside that episode could see it. **A rule that keeps getting broken becomes a check, not a longer paragraph.**
