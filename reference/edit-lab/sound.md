# Edit lab: SOUND editing lessons

> Part of the edit lab book. Installed to `content/reference/edit-lab/sound.md`; the book's index is `README.md` in the same folder. The book records what was tried, what failed and how a pipeline got to the version that works. Each lesson: final method, what was tried and dropped, how it got there, the ruling, receipts, and where the rule also lives. A new lesson learned while editing is added here in the same session.

Built 2026-10-29 from one working content system (read only): its work logs, its taste files, its reference docs, the shorts-editor and cut-review skills, the content rules, the episode build folders and a user-level editing skill. Names are replaced by roles ("the host", "the co-host", "the editor", "the creator") and guests by letters (guest X, guest K, and so on); episode folders are shapes (`podcast-guest-x`, `tutorial-1`). Receipts are generic: a date, a measurement, "the build log, row N" (the lessons log of the podcast shorts build, kept in `examples/podcast-shorts-pipeline/README.md`).

Script names that are not in this pack are named so you can rebuild them from the method written beside them; where a script ships in the pack, its path is given.

How to read "Where it lives now":
- **Guidance** = a file your sessions read: `content/taste/`, `content/reference/`, `.claude/skills/` or your rules files.
- **Build only, not guidance** = under version control but in a build folder or a script comment; no session reads it unless pointed there.
- **Not tracked** = only on one machine (an untracked build folder or a `raw/` folder). Measured on 2026-10-29: 2 episode build folders (330 and 312 files) were entirely untracked, a third had 38 tracked and 246 untracked, a fourth 321 tracked and 0 untracked; every `raw/` folder sits outside version control. **[Fixed 2026-10-29: the build text files were committed; `raw/` stays out]**
- **Work log only** = a row in a work log; found only by searching the log.

---

### Loudness target (LUFS) and how the level is actually reached

- **Final method:**
  - Long form and podcast: -14 LUFS integrated, true peak ceiling -1.5 dBTP, LRA 11 (`loudnorm=I=-14:TP=-1.5:LRA=11`), applied once, at the very end, on PCM audio; then measured on the encoded mp4 with ebur128, never assumed from loudnorm.
  - Podcast shorts (the shorts pipeline, Oct 2026): `audio_take` in `examples/podcast-shorts-pipeline/pipeline.py`: pass 1 measure, pass 2 `loudnorm ... linear=true` with the measured values, after the 1.1x atempo; pass 3 in PCM: gain corrected on the wav and a limiter run on 4x oversampled audio (`aresample=192000,<limiter>,aresample=48000`) so it holds the TRUE peak; a second harder limiter pass if the first misses; then encode once with `aac_at` 192k.
  - Shorts-editor `compose.sh`: voice `loudnorm=I=-14:TP=-1.5:LRA=11` (it was -16 until 29 Oct; `.claude/skills/shorts-editor/scripts/compose.sh`). So until 29 Oct the shorts-editor lane targeted -16 while every podcast, wave-1 and podcast-shorts pipeline targeted -14. No ruling settled one number for all shorts.
- **Tried and dropped:**
  - Single-pass loudnorm: landed at -16.4 LUFS against -14 (`content/reference/verify-loop.md`); on 2026-10-22 a live training's shorts still had "single-pass loudnorm (now 2-pass)".
  - `linear=true` on a two-pass loudnorm on guest K's cut pushed true peak to +0.1 dBFS where the single pass sat at -1.1 (2026-09-09); flag removed there. Note the podcast shorts pipeline uses `linear=true` again and catches the peak with its pass-3 limiter instead.
  - Demanding -14 on a peak-limited tape (guest K, 2026-09-09): closing 2.4 dB would put true peak at +1.3 dBFS; "loudnorm is not missing the target, it is refusing to clip". The check now reports `loudness_peak_limited` as a note. Guest K shipped at -16.4.
  - Native ffmpeg `aac` at 192k: overshot a -1.5 dBTP wav by +4 to +5 dB on 4 transients (guest R, 2026-09-10) and up to +5.7 dBTP on guest O's M1 (the build log, row 2, 27 Oct). Fix: 256k `aac_low` (guest R's finalize step) or `aac_at` (shorts pipeline).
  - Fixing level on the finished AAC file (second AAC generation): dropped; level is corrected on the wav (a comment in `pipeline.py`).
  - Builder limiter with auto-level on: pushed one wave-1 clip to -12.5 LUFS; turned off (2026-09-25).
  - `loudnorm` in the final graph of a clip cut with `-t`: 25 clips of guest Z's episode lost about 3 s of sound mid-clip while ffprobe showed full length (2026-10-16).
  - Plain loudnorm on a testimonial speaker's shorts (sources at -34.8 and -34.5 LUFS) could not hold the peak; compressor plus limiter added (2026-10-06).
- **How it got there:** guest O v1 shipped "-14 LUFS" (2026-08-26); guest K taught that loudnorm refuses to clip (9 Sep); guest R taught the encoder overshoot and PCM intermediates (9 to 10 Sep); guest G run 6 taught that the true peak must be measured on the mp4 (limiter to 0.79, wav -1.7, AAC had read -0.7; 2026-10-20); the podcast shorts pipeline folded all of it into a 3-pass routine (27 Oct).
- **Ruling:** No creator quote set -14 at first. `content/taste/clip-bar.md` called "-14 LUFS" a carried-forward prior-SOP number that an editing skill automates, "NOT claimed as observed". The numbers were machine practice, not a ruling. **[Fixed 2026-10-29: the creator ruled -14 LUFS for shorts everywhere; compose.sh moved from -16]** A starting default for your taste file: -14 LUFS integrated, -1.5 dBTP, measured on the encoded file.
- **Receipts:** measurements on guest K (2026-09-09), a wave-1 clip (2026-09-25), guest Z (2026-10-16), guest G (2026-10-20), a live training (2026-10-22), guest R (2026-09-09 and 10); `content/reference/verify-loop.md`; the build log, row 2.
- **Where it lives now:** Guidance: `content/reference/podcast-edit.md` (-14 at the end; true peak measured on the encoded file; no loudnorm with `-t`); `content/reference/verify-loop.md`; `content/reference/podcast-edit-runbook.md`. NOT in guidance at the time: the encoder overshoot and the 256k or `aac_at` fix (only in build code), the `linear=true` clipping lesson, the peak-limited physics (`loudness_peak_limited`), the 4x-oversampled true-peak limiter, limiter auto-level off. The -16 against -14 split between shorts lanes was undocumented as a choice.

### Audio taming (compressor before loudnorm)

- **Final method:** `acompressor` then `loudnorm` on loud close-mic or saturating moments.
- **Tried and dropped:** none recorded.
- **Ruling:** the creator, from a verbatim log of his edit notes, 2026-08-14: "Now a standing rule for every edit." (`content/taste/editing-rules.md`). A starting default: compress before you normalise.
- **Receipts:** `content/taste/editing-rules.md`; cut-review checks it with `volumedetect` (`.claude/skills/cut-review/SKILL.md`).
- **Where it lives now:** Guidance (both paths above).

### Clean-up chain: booms, rumble, declip, broadband denoise

- **Final method (depends on the tape):**
  - Phone tape, one mic bus, booming (guest X): `adeclip,highpass=f=120:poles=2,lowshelf=f=220:g=-5,afftdn=nr=8:nf=-34,alimiter=limit=0.95` then `loudnorm=I=-14:TP=-1.5:LRA=11` (guest X's segment renderer, quoted in `content/reference/podcast-edit.md`). Measured low band -27.9 to -31.3 dB, peaks -10.5 to -14.5 dB.
  - Riverside per-person tracks with a hotter low end (guest K): ONLY `highpass=f=80:poles=2` (guest K's finalize step).
  - Podcast shorts (28 Oct, AUDIO_V=2): `aresample=48000,adeclip,highpass=f=120,lowshelf=f=220:g=-5,afftdn=nr=18:nf=-42:tn=1,deesser=i=0.25:m=0.5:f=0.5:s=o,agate=threshold=0.015:ratio=1.6:attack=8:release=160:knee=6` (`examples/podcast-shorts-pipeline/pipeline.py`). **[Fixed 2026-10-29: `pipeline.py` now carries `AUDIO_V = 7` (the 29 Oct harshness pass): this V2 string is the 28 Oct version, read the live chain there; it is written out with its measured numbers in "Harshness and sharp peaks" below]**
  - Guest U's episode: `audio_clean` = `highpass=f=80,afftdn=nr=6:nf=-40`, plus `adeclip` on the co-host's track only (the episode's config, keys `audio_clean`, `track_chain`).
- **Tried and dropped:**
  - afftdn denoise on the co-host's lav shorts (2026-09-01): "Audio chain reverted on the co-host's call (afftdn denoise muddled the voice) ... lav audio on this footage is good enough raw; denoise made it worse".
  - Broadband denoise on the host's feed in guest K's episode (2026-09-10): "afftdn at nr=10 moved every band above 80 Hz by under 0.35 dB, so it would have been artifact risk bought for show". Band measurement showed his feed hotter only below 300 Hz.
  - `adeclip` on Riverside flat tops (2026-09-10): the flat runs sit at exactly -1.0 dBFS, "Riverside's own limiter, not digital clipping", adeclip "did not reduce the flat runs either"; left off behind a `declip` flag in `overrides.json`.
  - Podcast shorts AUDIO_V=1 `afftdn nr=10 nf=-50`, no de-ess, nothing on the room tail: replaced by V2 above after the creator's notes on shorts E, H, J (the build log, row 170).
  - `arnndn`: never used, no `.rnnn` model on the machine (a comment in `pipeline.py`).
- **How it got there:** guest X's boom chain (2 Sep) became the shorts chain by ruling (4 Sep); guest K showed a measured highpass beats a guessed denoise (10 Sep); the co-host's ear rejected denoise on clean lav (1 Sep); the 28 Oct styles review asked for noise and echo clean-up on every short.
- **Ruling:**
  - The host, 2026-09-02, on guest X v1: *"The mic booms A LOT... is there a way to clean that up? especially from my end. If not, let's lower the volume a bit"*.
  - The host, 2026-09-04: *"The audio has to be the one that we used on the actual long-form video, or whatever fixes you did to that audio, because it removed the clipping and a lot of the loud booms ... and that's for all clips."* A starting default: a short takes the long form's cleaned audio.
  - The creator, 2026-10-28 styles review, on E, H and J: "remove the background noise", "clean up the background noise", "you should clean up the echo"; rule "every short gets a noise and echo clean-up pass" (`content/taste/shorts-formats.md`).
  - The co-host, 2026-09-01: denoise reverted on her call (work-log paraphrase, no verbatim found).
- **Receipts:** as above.
- **Where it lives now:** Guidance: `content/reference/podcast-edit.md`; `content/reference/podcast-edit-runbook.md`; `content/taste/shorts-formats.md` (the rule only, not the chain). NOT in guidance at the time: the 28 Oct shorts chain string (build only: `pipeline.py`), guest K's "highpass only, denoise earned nothing" (a finalize comment and the work log), "never adeclip a Riverside -1.0 dBFS limiter flat top" (same), the co-host's "denoise muddled clean lav" (work log only), guest U's chain (not tracked).

### Echo, de-reverb, and "Studio Sound" style enhancers

- **Final method:** Measure the host's reverb tail against the guests' on the same tape (a `measure.py` that reports `decay_ms` per track); if his rings longer, de-reverb his track with DeepFilterNet 3 (`deep-filter` 0.5.6 binary, `deep-filter -D -o full-out full-in/<host>.wav`), pad and level-match (`pass1_pad_level.py`), then crossfade the original back with 10 ms ramps wherever the output digs more than 20 dB under it (`pass2_mixback.py`), re-measure, a person listens. For a single short with room echo: per-source `audio_extra` `afftdn=nr=14:nf=-35:tn=1,deesser=i=0.35:m=0.5:f=0.5` (the build log, row 69, tutorial-2's tape).
- **Tried and dropped (all 2026-10-20, guest G):** ElevenLabs voice isolation ("barely touched the reverb"); Resemble Enhance ("resynthesises the voice, shifts it 13 to 17 ms, dents 3 kHz"); DeepFilterNet attenuation limits `-a 15` and `-a 20` ("did not close the holes"); the raw de-reverb output without the mix-back left "3 gate holes from the de-reverb" (an adversarial review, 2026-10-20). Caveat on file: between words the output is gated to digital silence, "the reason not to use it on a solo track without checking" (the de-reverb scripts' README).
- **Studio Sound and enhancers:** on the 22 Sep tutorial-1 take the creator tried a "studio voice" pass on one line: *"Oh, it actually worked."* The editor: *"Studio voice. Nice."* The creator: *"It's much better."* The tool is not named on tape; "Tella's own voice enhancement is the likely one and that is untested" (tutorial-1's edit notes). The co-host, 26 Oct: Voice Isolation in Mic Mode suggested as "a free try (untested in Chrome)". No Adobe Podcast or Descript Studio Sound use found anywhere.
- **Ruling:** the host, 2026-10-19: *"There's something off with my audio. It feels very echoy. Could you please fix that? It's mainly from my side. You do have the source files, so I know you can fix it Without hurting the audio quality ."* (`content/reference/podcast-edit.md`). The creator, 2026-09-22, on the far mic: *"As long as there's no booms, we can fix it."* (tutorial-1's edit notes).
- **Receipts:** work-log measurements 2026-10-20 and 2026-10-21 (guest Q: guard retuned to the host's floor plus 10 dB, tail median 250 to 212.5 ms); the build log, row 69.
- **Where it lives now:** Guidance: `content/reference/podcast-edit.md`; the de-reverb scripts' README (which itself says the scripts are "Untested in this folder"); `content/reference/podcast-edit-runbook.md` points to both. NOT tracked: the measurement reports for guest G and guest Q (in `raw/` folders). Guest Q's retuned guard ("floor+10") is work log only. The studio-voice line is build only (tutorial-1's edit notes). The mic-distance prevention is guidance: `content/taste/must-dos.md` rows 4 and 5.

### De-essing and sibilance at splices

- **Final method:** a gentle `deesser=i=0.25:m=0.5:f=0.5:s=o` after the denoise in the podcast shorts chain, because denoise leaves hiss on sibilants (`pipeline.py`); 0.35 for the echoey tutorial-2 tape. At a take-to-take splice, move the in-point past the other take's trailing sibilance. **[Fixed 2026-10-29: the chain moved to `AUDIO_V = 7` in `pipeline.py`]**
- **Tried and dropped:** 2026-09-02, a co-host short: splicing take 1 to take 2 at 85.10 left take 2's trailing sibilance under take 1 and both whisper models read "my response FONTS and"; moved to 85.19. 2026-10-21, the co-host's long form v18: "the 'so' after 'for you' out (sibilant at 2223.85)".
- **Ruling:** none specific; it rides on the 28 Oct noise and echo ruling.
- **Where it lives now:** Build only (`pipeline.py`); splice sibilance is work log only. No de-ess line in any taste file.

### Room tone (measuring around it, laying it under, gating it)

- **Final method:**
  - Measure a music bed by isolation, not in a speech gap: render with and without music, invert one (`volume=-1` + `amix`), the voice cancels and the bed remains (-32.1 dB at 6% against -41.1 dB at 2%, the predicted 9 dB).
  - Lay the creator's own room tone under a regenerated word (the word-repair script, below).
  - Lower the room tail between words with a mild downward expander `agate ratio 1.6 release 160 ms` (podcast shorts chain).
  - On Zoom 24 kHz mono, where `silencedetect` finds nothing, dump the seam to 16k mono and print per-10 ms RMS (onsets jump from 1 to 4 to 200+).
- **Tried and dropped:** measuring the bed in a speech gap (2026-08-21): "at 2% the gap read identically to no-music, which looks like the bed vanished. It had not." Lowering `silence_keep` to -30 or -32 dB in a noisy room eats word releases.
- **Receipts:** measurements 2026-08-21, 2026-09-01, 2026-09-25 (`word_clipped` flags that were room tone at -37 to -81 dB both sides).
- **Where it lives now:** Guidance: `.claude/skills/shorts-editor/SKILL.md` (isolation; RMS on Zoom; noisy room) and `.claude/skills/cut-review/SKILL.md` (noisy room). The agate tail is build only (`pipeline.py`).

### Music bed level: shorts

- **Final method:** bed at 2% (`MUSIC_VOL=0.02`, `compose.sh`), voice loudnorm -14, `amix normalize=0`, bed from 4 s into the track, 0.5 s fade in, 2 s fade out.
- **Tried and dropped:** 0.15 "covered the voice"; 0.06 (6%) "way too loud" (the creator, 2026-08-21); 12% under speech on guest X's shorts round 3, dropped to a duck to 2% under speech (2026-09-04). Guest G's shorts on 3 Oct had no bed; a 2% house bed was added on 6 Oct.
- **Ruling:** the creator, 2026-08-21: *"We will definitely go with the low music, whatever the first clip was, it was way too loud."* Resolved the same session: bed at 2%, not 6% and not zero. A starting default for your taste file: 2%.
- **Where it lives now:** Guidance: `content/taste/lessons.md`; `.claude/skills/shorts-editor/SKILL.md`. **Conflict:** `.claude/skills/shorts-editor/references/style.md` still said compose.sh keeps "the music LOW (volume 0.06 ...)", the retired default; a session reading style.md first got 6%. **[Fixed 2026-10-29: style.md now says 0.02]**

### Music bed level: podcast intro, teaser and trailer

- **Final method:** bed about 19 to 20 dB under the voices, measured against the voice in the same window before a render is shown, the number said. Guest P's `music_level` 0.0224 (voice -22.9, bed -42.9 LUFS); guest Q's trailer bed 0.0200 (19.5 dB under). One licensed music library only (Epidemic Sound in the tested setup, the creator's own account); 3 options per episode, the creator picks.
- **Tried and dropped:** 0.10 (guest X, 3 Sep, about 6 to 7 dB under), called "The music is way too loud" on guest P (2026-09-28); guest R 0.06 on the editor's ruling (9 Sep); guest R's trailer 0.11 (21 Sep); guest Q's W2 at 0.061 sat 9.8 dB under (fixed 2026-10-22). ElevenLabs-generated suspense beds were delivered for guest O (2026-08-27); the music source then became the licensed library only ("Music comes from the licensed library, the creator's account, never generated", the runbook).
- **Ruling:**
  - The host, 2026-09-03 (guest X): *"very low volume and... starts fading out about 7 seconds before the intro animation finishes."*
  - The editor, 2026-09-09 (guest R): *"really, really, really low volume in the background. And it shouldn't dominate the intro at all or the voice of [the host]."*
  - The host, 2026-09-28 (guest P): *"The music is way too loud."*
  - A starting default for your taste file: about 20 dB under the voices, measured.
- **Receipts:** measurements 2026-09-29 (0.10 to 0.0224, -13 dB; bed 18.8 dB under, was 5.9) and 2026-10-22.
- **Where it lives now:** Guidance: `content/reference/podcast-edit.md` (0.0224, about 19 to 20 dB under). **Conflict:** the runbook (`content/reference/podcast-edit-runbook.md`) still said "Bed at 0.10 under the teaser and intro animation" and listed "the bed level `0.10`", so the editor's runbook taught the level the host called way too loud. **[Fixed 2026-10-29: the runbook now says 0.0224]**

### Teaser bed length and fades

- **Final method:** a teaser bed is at least as long as the teaser plus the title card; a short track is extended musically (a crossfaded repeat of whole bars before the track's own ending), never looped hard or padded with silence; the build refuses a shorter bed (a `bed_guard` in the episode's picks step, plus a small extension script).
- **Tried and dropped:** 2026-10-20, M2 ended at 39.95 s against a 45.04 s bed window, "so the fade never played and the title card was digital silence".
- **Ruling:** machine finding from the third adversarial check (no creator quote).
- **Where it lives now:** Guidance: `content/reference/podcast-edit.md`. Code tracked (that build was fully tracked).

### Music bed level and ducking: the co-host's long form

- **Final method:** a `sound_mix.py` with beds by section, `sidechaincompress` keyed by the voice (`duck: threshold 0.02, ratio 6, attack 20, release 400`), every section fades at its borders "so a change of bed never clicks", optional ramp inside a section, loudnorm -14/-1.5/11, a `--range` listening sample before any full mix. Her numbers: open -30 riding to -40 over 2.5 s at 17 s, body -46 dB, close -30, ticks -8 dB. Her long-form open (17 Oct): level D, -12 to -18 with duck ratio 3.
- **Tried and dropped:** -20 dB "passed a one-minute sample and was too loud over nineteen minutes" (11 Sep); -26, -30, -40 for the body (11 to 14 Sep); open samples B and C "still too quiet in parts, the intro bed is there for energy ... the quiet parts were the ducking under her voice as much as the level" (17 Oct); E (-9 to -15, ratio 2) not picked.
- **Ruling:** the co-host, 2026-09-11: "music needs to be lower volume"; 2026-09-14 on v18: "lower the volume of the music after the intro"; 2026-09-17: "click sounds could be just a little bit louder"; 2026-10-17: D is the open's music level.
- **Receipts:** her mix rounds of 11, 14 and 17 Sep and 17 Oct.
- **Where it lives now:** Build only: the `sound_mix.py` header; the co-host's project README ("a level is judged on the whole video, never on a minute"). The general principle "judge a level on the whole video" was not in any taste file. The open's duck-ratio lesson (17 Oct) is work log only.

### Ducking other speakers and the bed in podcast cuts

- **Final method:** inside a trailer clip the 2 listeners' tracks duck to 0.1 unless the clip keeps them (a laugh, a "Whoa"), 40 ms pad either side (guest U's picks and render steps). On a one-mix tape (a Riverside composite) the duck-window skip is turned off (guest P, 2026-09-25). Mute a guest's track over echo of the host (co-host F1 and F2, 2026-10-07).
- **Ruling:** design, no creator quote; clip-bar Rule 5 ("ducks when you talk").
- **Where it lives now:** Guidance for the principle only: `content/taste/clip-bar.md`, `content/taste/kinds/short.md`. The listener duck to 0.1 was not tracked (guest U's build untracked). clip-bar's "~50%" duck number is labelled prior-SOP, not measured. **[Fixed 2026-10-29: guest U's build is tracked]**

### The host's loud laugh

- **Final method:** every laugh span on his track drops to gain 0.32 (pad 0.15 s), then his whole track runs `acompressor=threshold=0.08:ratio=5:attack=4:release=140:makeup=1.6,alimiter=limit=0.35:attack=3:release=60:level=false`; done before the bed is set. Guest U's shorts: "the host's laughs ducked 8 dB" (2026-10-27). Laughs are found by envelope modulation at 3.5 to 8 Hz (a `find_laughs.py` in guest Z's build), not by loudness.
- **Tried and dropped:** loudness-based laugh finding returned 198 "laughs", "nearly all crosstalk" (2026-09-21).
- **Ruling:** the host, 2026-10-27 (guest U's picks): *"my laugh is too loud, catch those moments and normalize ("overnormalize" my audio peaks)"*, *"make my laughs a bit quieter (i have a very loud laugh)."* (`content/reference/podcast-edit.md`). A starting default if your host laughs loud: treat the laugh spans before the bed.
- **Receipts:** guest U's episode config, key `host_laugh` ("Untested by ear until he hears it"); a measurement 2026-10-27 (his untagged laugh in M27 peaks at 0.0 dBFS, the co-host clips 250 samples; declipper on her track).
- **Where it lives now:** Guidance: `content/reference/podcast-edit.md` (rule, no numbers). The numbers and code were not tracked (guest U's build). `find_laughs.py` is build only; the modulation-not-loudness lesson is work log only. **[Fixed 2026-10-29: guest U's build is tracked]**

### Background noise check (honks, dogs, doors)

- **Final method:** Gemini Flash audio, one listen per sound category (6 per clip), not one open question; confirm every hit on the raw track because its timestamps drift by a second or more; a hit is cut, ducked or the moment dropped (a `noise_check.py` in guest U's shorts build).
- **Tried and dropped:** 2026-10-27, an open "anything that is not the voices" prompt answered "clean" 3 times on the M06 clip that has the honk.
- **Ruling:** the host, 2026-10-27: *"there's a honk noise in the back you should've caught (we could leverage audio models like gemini flash for this?)"* (`content/reference/podcast-edit.md`).
- **Where it lives now:** Guidance: `content/reference/podcast-edit.md`; build detail in guest U's shorts notes.

### Sound effects: swooshes, page flips, ticks

- **Final method:** a real sound the person picked (the co-host: a real recorded page turn from the licensed library) at -12 dB, placed on the cut measured on the picture, centred in a pause of 0.3 s or more; never on plan or section times; ticks at -8 dB. Worked example: the co-host's long form v20 rebuild script. **[Corrected 2026-10-29: what shipped (2026-10-22) is the 0.20 s landing only (0.42 to 0.62 s of the page-turn file) at -10 dB, in the quietest 0.2 s of her own voice track within 0.3 s of the cut measured on the picture, and only where that stretch is under -28 dBFS (the transcript's gaps lied: a voiced -12 dBFS sound read as a pause); 6 of 8 chapter cuts were too tight and got none. The 5-skills list ticks at -8 dB are synthesised (an `sfx_make.py`); whether a reveal tick counts as a transition sound under rule 10 was her call, asked 29 Oct.]**
- **Tried and dropped:** a synthesised `page-flip.wav` (19 Oct, 0.55 s) "reads as a pop to her" (2026-10-22); the pop the base render mixed on each chapter's first piece "landed up to 3 s into her speech", silenced at source (volume 0); section times "drifted up to 1.6 s from the picture"; ticks at -12 dB too quiet (17 Sep).
- **The creator's swoosh:** 2026-10-10 he allowed a background shift "as an effect that allows me to shift the background with a transition... a swoosh... while keeping my face intact". The background-shift tool (`footage_bg_shift.py`, not shipped in this pack) SYNTHESISED its whoosh (filtered noise sweep), `--sfx-under` default 10 dB under the loudest 30% of his samples (about 6 dB under his average speech).
- **Ruling:** the co-host, 2026-10-22: *"The chapter page flip sound should be in the transitional moments, in between me saying things when we're changing screens... it doesn't make any sense to have the sound right in the middle of me speaking."* (`content/taste/editing-rules.md`, rule 10). The creator, 2026-10-10 (the footage-edits rule in your content rules). A starting default: a transition sound lands in a measured pause, never on top of speech.
- **Where it lives now:** Guidance: `content/taste/editing-rules.md` (rule 10); your content rules (footage edits); `content/taste/clip-bar.md`. **Conflict, unresolved at the time:** rule 10 said "a real sound she picked, never a synthesised 'page flip' or pop", and `footage_bg_shift.py` synthesised its whoosh. Whether rule 10 bound the creator's footage was not ruled. **[Fixed 2026-10-29: ruled by the creator: real recordings only, on every machine; `footage_bg_shift.py` needs `--sfx`]**

### Sample rate: 96 kHz against 48 kHz

- **Final method:** hand any platform 48 kHz audio (`-c:v copy -c:a aac -ar 48000`), as a precaution. A LinkedIn file check requires AAC 48 kHz; Instagram allows 48 kHz at most. For cloud renders make every mix input explicitly 48 kHz stereo (Linux ffmpeg could not infer a channel layout, `content/reference/cloud-rendering.md`).
- **Tried and dropped:** 2026-09-22 a session blamed 96 kHz for LinkedIn's refusal; "the 48 kHz file then failed in exactly the same way" (the creator: *"still errored out"*). 96 kHz was not the cause; the claim is kept corrected in place.
- **Ruling:** measured, 2026-09-22. A starting default: 48 kHz at the hand-off, never claimed as a diagnosis.
- **Where it lives now:** Guidance: your content rules (the 48 kHz precaution); your posting notes. Note: several finals were still stereo 96 kHz (`content/reference/cloud-rendering.md`), so the pipeline itself was never moved to 48k; only the hand-off is.

### Regenerating a flubbed word in his own voice (ElevenLabs)

- **Final method:** a `footage_word_regen.py regen --video V --transcript T.json --window A,B --replace S,E --word "<meant word>" --picture keep --keep-from K --out DIR` (or `--picture cutaway --cutaway SCREEN.mp4`). Voice: an ElevenLabs Instant Voice Clone of the creator's own voice, labelled for word repair only, its id kept in your own config (133.4 s of his solo speech, 1 speaker across 420 words). Routine: snap both joins to the quietest 10 ms within 40 ms; ask the clone for his last 6 words plus the meant word, 3 seeds; pick the take whose melody follows his flubbed attempt; EQ match from the clone's lead to his real lead (3 bands, clamped 6 dB, half strength); pitch to his attempt's median (at most 2 semitones, formants kept); length to the slot; loudness from the lead words; his room tone under it; 15 ms crossfades; read back with Scribe. About 165 plan characters a word.
- **Tried and dropped (2026-10-10):** stock male voices (distance 28.2 and 41.6 dB against the clone's 19.9; his own 2 takes 18.7 apart); keeping the picture when he did not re-say the word (no lip-sync model on the machine or on any key; sync.so lipsync-2-pro priced "$0.067 -- $0.083/sec" needs a sign-up only the creator can do), so cutaway instead. "Keep" mode leaves a visible head jump.
- **Ruling:** the creator, 2026-10-10: *"Both, I'd love to integrate these!"*; only a word he meant to say, never a new word, each use noted in the edit notes so cut review sees it (the footage-edits rule in your content rules).
- **Receipts:** the script's docstring; the creator's video-lab page; 2 sessions on 2026-10-10.
- **Where it lives now:** Guidance: your content rules (the permission). The method is build only (the script docstring and the lab page). Not in any taste file or skill. No record of it used on a shipped cut.

### Anonymising a third party's voice

- **Final method:** none built. Practice so far: cut the third party's voice out entirely (a consult short: "Her voice was cut, not shifted: nothing of hers is in the file to shift", from that short's cut review).
- **Tried and dropped:** nothing run. Review note: "the route is untested here: a plain pitch shift (ffmpeg `rubberband`) is the minimum, ElevenLabs speech-to-speech is the alternative he named; whichever runs, somebody listens before it is called 'not creepy'"; and "A pitch change hides the voice and not the facts". Related, from the voice rules: pitch alone did not separate the creator (109 to 143 Hz) from the editor (152 to 165 Hz) on one tape; the lip check was decisive. On guest Z's episode, the co-host's and guest Z's pitch medians 15 Hz apart could not attribute speech (2026-09-18).
- **Ruling:** the creator, 2026-09-23: *"If someone is not seen, heard, or named, then what do they need to give consent about? If the short is better because of their speech and needs to be heard, then we can change the voice pitch to become anonymous (not creepy, just a voice change that maybe elevenlabs can do, and only on the other person's voice)."* (the third-party-consent rule in your content rules).
- **Where it lives now:** Guidance: your content rules; `content/taste/kinds/short.md`. The untested-route caution is build only (that short's cut review). UNTESTED as a technique.

### Riverside separate tracks: getting them and proving they are in sync

- **Final method:** download each person's Raw video from the project page (lands as `riverside_<participant>_raw-video-cfr_*.mp4`, aligned CFR); the Riverside MCP cannot download tracks. Since 2026-10-28 the studio records separate tracks up to 4K (was 720p). Stage: probe every track (CFR check), 10 ms RMS envelope per track, each speaker's own speech level and the gain that levels the voices, bleed words, and sync proved by cross-correlating the host's voice with its bleed in the guest track: "correctly aligned tracks show that bleed LATE by the call's audio latency ... a negative lag would mean misalignment" (guest G's stage step). Guest G: bleed +560 to +650 ms late at 4 points, no drift (2026-10-06). Mix with `amix normalize=0`.
- **Tried and dropped, and traps:**
  - 2026-09-18, guest Z: the co-host's isolated track ended at 691.0 s because her mic broke and Riverside opened a SECOND track; the "Aligned video" export of the second track is "DIGITALLY SILENT over the first 691 s", so swapping it in threw away her first 11:31; fixed by stitching the partial track to 691 s, then the aligned one.
  - Guest Z's track goes digitally silent at 1374.9 s (2026-10-03).
  - A Riverside composed export ("magic edit") is one mono bed (guest K at 69 kbps; guest R; guest D), not per-speaker tracks; per-person clean-up cannot run on it.
  - A notetaker bot staying on Zoom while the call moved to Riverside lost the guest's words (guest S, 2026-09-16).
  - 26 Oct, 9 episodes pulled in one night (each track's Download, then Raw video, in a signed-in browser): the file name carries the Riverside participant name, which is the account's, not always the person's (the host's track on guest C's episode carried the studio account's name). The ingest waits until no `.crdownload` is left, assigns each file to its episode by name fragment, duration (within 0.5 min) and width, and by birth order where 2 tracks are 1 s apart (the co-host's on guest E and guest Y), COPIES it (never moves, never deletes) to a media cache outside the synced project (`<media-cache>/podcasts/<slug>/<person>-cfr.mp4`), writes a manifest, then runs Scribe per track with the episode's keyterms (cached by file name, `--force` to redo). Its keyterm lists still carried the brand's old name: a copy of the script uses the current one (the build log, row 66). The Downloads copies went to the Trash only after `cmp` proved them identical (32 GB). Receipts: the ingest script's header and its log; the build hand-off notes ("Tape").
- **Ruling:** the creator's word switched the studio to Advanced, Up to 4K HD (2026-10-28).
- **Where it lives now:** Guidance: `content/reference/podcast-edit-runbook.md` (download route, MCP limit, 4K); `content/reference/podcast-edit.md` ("one shared timeline, Riverside CFR-aligned tracks"). NOT in guidance at the time: the bleed cross-correlation sync proof (build only: guest G's stage step), the second-track-when-the-mic-changes trap and the digitally silent aligned export (work log only), per-speaker leveling `gain_db` (the stage step only).

### Audio drift and A/V sync

- **Final method:**
  - Join with the concat FILTER, never `concat -c copy` of AAC pieces (`.claude/skills/shorts-editor/scripts/cutjoin.py`).
  - Every intermediate carries PCM audio (.mov), AAC made once at finalize (guest R).
  - Video segments render without audio; audio is cut sample-exact to each segment's real frame count at join time (`content/reference/workshop-edit.md`).
  - Parallel finalize chunk bounds on the frame grid and measured on the real master, never EDL arithmetic (`content/reference/podcast-edit.md`).
  - Audio pulled out of a cut is read by its timestamps (`aresample=async=1`), never sample by sample; sync proven against the original tape at every camera piece (a `tape_sync_check.py`).
  - Re-transcribe the finished file and compare anchor words (`verify.py --deep`, `content/reference/verify-loop.md`); `av_drift` gate at 0.10 s (the runbook).
  - Contiguous segments meet exactly on the frame grid; edge padding that overlaps 27 to 110 ms replays words (guest P, 2026-09-25).
- **Tried and dropped:** stream-copy concat (guest K: 0.114 s steps at joins, `verify-loop.md`; guest R: 0.42 s audio behind and captions 1.2 s late by minute 38, 2026-09-09; 0.366 s shipped once, the runbook); the co-host's v7 "cfr+async join measured worse (2059.9 s against a 2050 s plan; lips 1.5 s off at 1:00)", replaced by the concat filter with each piece's audio padded or trimmed to its frame count, then loudnorm (2026-10-15); reading joined audio straight through put the sound 0.77 s late by 3:49 (2026-10-22).
- **Ruling:** the co-host, 2026-10-22: "im at 3:49 and the video is not synced with the audio" (`content/taste/editing-rules.md`). A starting default: sync is proven against the original tape, not assumed.
- **Where it lives now:** Guidance: `content/taste/editing-rules.md`; `content/reference/podcast-edit.md`; `content/reference/workshop-edit.md`; `.claude/skills/shorts-editor/SKILL.md`; `content/reference/verify-loop.md`; the runbook. Gap: the "PCM intermediates, AAC once" rule was not written in guidance (only in 2 episodes' build comments and the work log); the overlap-replay lesson is work log only.

### Clicks at cut points, crossfades, fades

- **Final method:** 30 ms fades at every segment edge (podcast, `content/reference/podcast-edit.md`; the video-use skill's Hard Rule 3: `afade=t=in:st=0:d=0.03,afade=t=out:st={dur-0.03}:d=0.03`); podcast shorts pipeline 8 ms raised-cosine ramps per piece plus a 0.25 s fade on the last breath (`pipeline.py`); word regen snaps joins to the quietest 10 ms within 40 ms and splices with 15 ms crossfades; de-reverb mix-back 10 ms ramps; bed sections fade at their borders (`sound_mix.py` header). A second fast limiter pass caught a mic pop at 34:15 on the 23 Sep live session (2026-09-25). Cut-review flags "Waveform spike at the boundary" (the video-use skill).
- **Tried and dropped:** hard audio cuts ("Audible pops", the video-use skill); a pop baked into each chapter's start (the co-host's long form, silenced 2026-10-22).
- **Ruling:** none by the creator; technical rule.
- **Where it lives now:** Guidance: `content/reference/podcast-edit.md`; `content/reference/podcast-edit-runbook.md`. The 8 ms ramp, 15 ms crossfade and quietest-10 ms snap are build only. video-use is a user-level skill (see below).

### Silence removal

- **Final method:**
  - Shorts: `silence_keep.py` with silencedetect -40 dB, MIN 0.35 s (0.30 for very punchy), PAD_AFTER 0.12, PAD_BEFORE 0.06, PAD_LAST 0.45 (`.claude/skills/shorts-editor/scripts/silence_keep.py`); then check gaps over 0.30 s in the re-transcribed cut.
  - Podcast: joint-silence gaps of 1.0 s or more tighten to about 0.6; never a kept sliver under 1.2 s (machine-gun guard) (`content/reference/podcast-edit.md`, `content/taste/kinds/podcast.md`, `content/reference/workshop-edit.md`).
  - Livestream cuts keep 1 to 3 s natural silences (`content/taste/editing-rules.md`).
  - A masterclass (the editor's pick, 2026-10-12): every pause over 1.5 s inside a take trimmed to 0.8 s (78 trims, 5.6 min).
  - On the delivered file run silencedetect and flag any silence over 1 s (`content/reference/workshop-edit.md`); read the first `silence_end` as the true voice onset at the head.
- **Tried and dropped:** old MIN 0.5 and PAD 0.16 left 0.3 to 0.5 s pauses, "too much pause" (`SKILL.md`); a -30 dB trimmer ate soft tails ("output" to "out", 3 rounds); word-gap trimming alone left 0.6 to 1.1 s silences; a 0.75 s silent lead shipped a hairflip on a co-host short (2026-08-19).
- **Ruling:** the creator, livestream: "Clearly still a livestream but more watchable." (`content/taste/editing-rules.md`). The editor, 2026-10-12 masterclass pick (work-log paraphrase).
- **Where it lives now:** Guidance for all but the masterclass 1.5 to 0.8 s rule, which is work log only (not in `content/taste/kinds/masterclass.md`).

### Filler removal

- **Final method:** podcasts keep fillers in the audio, captions drop standalone uh and um; shorts drop fillers, the other speaker's lone "Yeah", false starts and repeats from the CAPTIONS only, and cut a stumble from the tape only when the cut is clean. A retake detector separates STUTTERS (same word twice in a breath, kept) from RESTARTS (a 3+ word phrase said twice by the same mic within 30 s, cut) (a `find_retakes.py` in guest Z's build, 2026-09-18). The co-host's shorts bar: the machine marks fillers red, she approves (her shorts-bar taste file). The in-point after a dropped stutter sits at the dip right before the kept word (`.claude/skills/shorts-editor/SKILL.md`).
- **Tried and dropped:** chasing every "um" in a two-shot "makes visible jump cuts" (`content/reference/podcast-edit.md`); 3 rounds widening a cut around a 10 ms Scribe "Hmm." that was the creator's own filler mislabelled (a tutorial, 2026-09-11).
- **Ruling:** the host, on guest Z's tape (17 Sep): *"keep, you know, keep the "ums," keep the f- keep the, um, the, um, uh, um, the clunky, sometimes awkward parts, but obviously really delete the double takes."* The co-host, 2026-10-15: "highlight areas where we could trim and the retakes, not the ums and likes". `content/taste/editing-rules.md` says filler handling is decided per video. A starting default for a podcast: keep the ums, delete the double takes.
- **Where it lives now:** Guidance: `content/reference/podcast-edit.md`; `content/reference/podcast-edit-runbook.md`; `content/taste/kinds/podcast.md`; `content/taste/shorts-formats.md`; the co-host's shorts-bar file. The host's verbatim "keep the ums ... delete the double takes" is build only (guest Z's options brief); the stutter against restart split is work log plus build code (`find_retakes.py`).

### Livestream and mixed-source levels; speed

- **Final method:** livestream phone audio sits about 12 dB under the lav mix (mean -25.4 against -12.8 dB), lifted to about 6 dB under, "err for lower volume" (`content/reference/podcast-edit.md`, the runbook). Full episode at 1.1x with pitch preserved (atempo); captions burn before the speed pass (`content/reference/podcast-edit.md`); shorts default 1.1x (`pipeline.py` `spec_speed`).
- **Where it lives now:** Guidance (paths above). The shorts 1.1x default is build only (the build log, row 67).

### The user-level video-use skill (local edits)

- A local diff of this third-party skill showed 6 added lines and 1 changed, none about sound technique: hard rules 13 to 15 (detached renders, `-loop 1` needs `-t`, never kill during a render), a pointer to `content/reference/podcast-edit.md` and the runbook, and a rewritten Whisper line saying the machine had no `ELEVENLABS_API_KEY`. That last line went stale: the editor's machine got the key on 2026-09-09 and Scribe is the route (`.claude/skills/shorts-editor/SKILL.md`). **[Fixed 2026-10-29: that line was rewritten the same day: the key is there and Scribe is the route]** Lesson: a user-level skill you edited locally drifts from your project's facts; re-read it when a key or a route changes.
- Upstream sound rules in that skill: 30 ms fades at every boundary, pad every cut 30 to 200 ms because Scribe drifts 50 to 100 ms, silences of 400 ms or more as the cleanest cut targets. An editor has these only if they installed video-use themselves.

---

### Removing a sound baked into a mix (from the co-host's channel, added 2026-10-29)
- **Final method:** subtract the known waveform of the baked sound from the in-sync voice; 8 pops removed, 0 matches above 0.7 left, lag 0.0 ms at 9 points.
- **Receipts:** the co-host's long form v20 rebuild, 2026-10-22.

### A reveal and its tick land on the measured voice onset (from the co-host's channel)
- **Final method:** the onset is the first 10 ms frame above -40 dB, not the transcript's word start; Scribe starts ran 0.1 to 0.3 s ahead of the audible word on every reveal word.
- **Receipts:** the co-host's project README (a 5-skills list reveal).

### Outdoor takes and the cough (from the co-host's channel)
- **Final method:** `silencedetect` finds nothing outdoors; an RMS scan at -29 dB separates speech (-17 to -25) from ambient (-32 to -37), but the same threshold eats word tails, so tails are extended by ear; a whisper word over about 1 s is a stumble it papered over; a cough is a picture before it is a sound (the gesture starts first), so its span goes whole.
- **Receipts:** the take notes of a walking recording, 2026-09-01.

---

From the 27 to 29 Oct podcast shorts build (added 2026-10-29 evening; "row N" is a row of the build log, kept in `examples/podcast-shorts-pipeline/README.md`):

### Harshness and sharp peaks: the shorts chain V3 to V7, and how to measure it
- **Final method (`examples/podcast-shorts-pipeline/pipeline.py`, `AUDIO_V = 7`):**
  - Every piece: `aresample=48000,adeclip,highpass=f=120,lowshelf=f=220:g=-5,afftdn=nr=18:nf=-42:tn=1,deesser=i=0.4:m=0.5:f=0.45:s=o,adynamicequalizer=dfrequency=5500:dqfactor=1.2:tfrequency=5500:tqfactor=1.2:attack=1:release=80:ratio=2.5:range=8:mode=cutabove:auto=adaptive,agate=threshold=0.015:ratio=1.6:attack=8:release=160:knee=6`, then read back: a piece that is not finite or peaks over +6 dBFS is rebuilt down `AUDIO_FALLBACKS` and the chain that held is logged. Fallback 1 drops the de-esser and the 5.5 kHz dynamic cut; fallback 2 also drops `adeclip`, afftdn's `tn=1` and the gate; both end in `alimiter=limit=0.95:level=false`. A 25 ms fade in at every join.
  - The joined take, pass 3: `SHAPE`, a soft fast compressor (-18 dB, 3:1, 0.5 ms attack, 60 ms release, knee 8), then the 3 to 8 kHz band alone through a fast compressor (`acrossover=split=3000 8000:order=8th`, -16 dB, 4:1, 0.1 ms attack, recombined with `amix normalize=0`); its gain is found through the shape so the take still lands at -14 LUFS; then the 4x-oversampled true-peak limiter.
  - `AUDIO_V` is in every piece's cache key: bump it with any chain change, or old pieces are reused silently (V2 row 170, V3 row 190, V4 row 207, V7 row 218).
- **How to measure it:** a band meter read through the AAC encode: decode to 48 kHz stereo and average the 2 channels, filter 3 to 8 kHz with a 6th-order Butterworth band-pass run forward and back (`butter(6, [3000, 8000])`, `sosfiltfilt`), take the peak of each 50 ms window. Report before and after: 50 ms broadband windows over -3 dBFS; band windows over -12 dBFS; the band peak and where it sits; 2 balances, the band's energy against the whole signal on the loudest 2 s (`loudest2s_band_balance_dB`) and on every sample over -30 dBFS (`speech_band_balance_dB`, the "not dulled" number). Guest C, old chain (M2): 231 of 1064 windows over -3 dBFS, 102 band windows over -12, band peak -3.0 dBFS. New chain: F2 6 of 572, 9, -9.6 dBFS, speech balance -16.0 dB; M1 45 of 1029, 8, -11.0, -18.1; loudness -14.0 LUFS, true peak -2.2 and -2.0 dBTP (row 218). The meter is about 20 lines and lived in a session scratchpad, which the system clears: the description above is enough to rebuild it.
- **Tried and dropped:**
  - Row 207's first numbers: they read the limiter's ceiling as spikes, so "215 of 572 windows over -3 dBFS" described the limiter, not the voice. Row 218 blames "a whole-signal FFT band cut and a mono downmix", but the replacement meter averages the 2 channels too, so the band filter is the change that is proven; the downmix part is not.
  - V4 (de-esser 0.4 plus the 5.5 kHz dynamic cut, no band compressor): it missed a sharp onset the de-esser cannot catch, guest C's F2 'Just' at 8.75 s, a 60 ms all-treble burst at -3.8 dBFS (row 218).
  - A stronger chain (2 dynamic cuts, de-esser 0.5): it took the speech's 3 to 8 kHz balance from -14.9 to -20.7 dB. Dull, rejected (row 218).
  - The V2 chain on guest X's clipped single-camera phone file: it ran away to +12.2 LUFS before loudnorm (adeclip rebuilds clipped peaks above 1.0) and 3 renders died on loudnorm's 'measured_I out of range'. Which filter ran away is untested; the read-back and fallbacks are the fix (row 190).
- **Open:** one chain does not fit every tape. Guest O's quiet, hissy 360p Zoom track came out dulled: balance -23.4 dB on the loudest 2 s against her source's -14.0 under the same meter, from afftdn nr 18 plus the de-esser (guest O's M1 round-3 verdict, fix 0). Guest X's tape is dull at the source, 3 to 8 kHz about 40 dB under the mids; a gentle treble lift would help every guest X short (guest X's F2 round-3 verdict, taste 3). `people.<role>.audio_extra` only adds to the chain, so a lighter per-source chain is not built yet.
- **Ruling:** the host, 2026-10-29, on guest C's clips: *"there are high peaks in [the guest's] voice, and it's a little sharp on the ear. Clean up the audio in any sharp places, and then they'll be ready to go."* (`content/taste/shorts-formats.md`, the last Round-3 line). A starting default: run the band meter on every short before it is shown, and judge "not dulled" by the speech balance number.
- **Receipts:** rows 190, 207, 218; the `pipeline.py` comments around `AUDIO_V` carry the numbers; guest E's M2 round-3 verdict, taste 4 (band peak -9.5 dBFS, -13.98 LUFS, -3.58 dBTP on the new chain).
- **Where it lives now:** this entry and `pipeline.py`. The rule is in `content/taste/shorts-formats.md`; the chain and the meter are not.

### A spec timed on one export while the tracks run on another: retime and offsets
- **Final method (`needs_retime: true` on the spec):** a person with a null offset gets it measured at build time. The span's own text (the hook `text`, or a piece's 4th element) is matched in order against that person's word file, fillers skipped. With no text, the search takes the offset within 45 s of the known one that puts the spans' edges on word edges (0.04 s), or the known same-session offset when 60% of the edges sit on word edges there. Then every piece of every person must have words under it (30%). A miss writes a `retime-failed` row and exits 2, never a crash; a found offset is written back into the spec's `retime` and `people.<role>.offset`. `words_offset` shifts a word file cut from an extract (guest Z's co-host word file starts at track second 693).
- **Tried and dropped:** specs timed on a composed Riverside export that is gone (guest D +387.98 s and guest R +374.65 s on the guest tracks; guest P's tracks landed late); an aha hook piece that carries its speaker as a 3rd element broke the retime path, because `_pieces_of` unpacked 2 (row 78); a role name ('agent') that is no person in the spec stopped `plan()` with a KeyError (row 128).
- **Receipts:** the example's README, method notes item 10; rows 8, 78, 128; the build hand-off notes ("Gotchas").

## Where these lived before this book (29 Oct 2026), and what still waited on a ruling

Not tracked at all (one machine only):
1. The host's laugh treatment numbers and code (gain 0.32, pad 0.15 s, compressor and limiter strings), the listener duck to 0.1 in trailers, the co-host's adeclip, guest U's `audio_clean` chain: guest U's build folder was wholly untracked (330 files). The rule was in `podcast-edit.md` but the working values were not. **[Fixed 2026-10-29: committed]**
2. Guest Q's de-reverb run with the retuned guard ("floor+10") and its report: build and `raw/` untracked. **[Fixed 2026-10-29: the build folder committed; `raw/` stays out]**
3. Guest G's de-reverb measurements report (`raw/` is never committed; the README says so).
4. Most of guest P's build (246 untracked files); its bed level 0.0224 survives in `podcast-edit.md`. **[Fixed 2026-10-29: guest P's text files are tracked]**

Tracked but only in work logs, build code or outputs (no editor session reads them unless pointed):
5. AAC encoder overshoot: native `aac` at 192k overshoots true peak by +4 to +5.7 dB; use 256k `aac_low` or `aac_at`, encode once, from PCM. (2 episodes' finalize comments, the shorts `pipeline.py`, the build log row 2; 2026-09-10.)
6. PCM intermediates, AAC once at finalize (2026-09-09; build code).
7. `linear=true` two-pass loudnorm can clip, and the "peak-limited, not missing target" physics (2026-09-09).
8. The 3-pass loudness routine with a 4x-oversampled true-peak limiter (`pipeline.py`).
9. Denoise decisions: guest K "highpass 80 Hz only, afftdn earned nothing"; never adeclip Riverside's -1.0 dBFS limiter flat tops (2026-09-10); the co-host "afftdn muddled clean lav" (2026-09-01).
10. The 28 Oct shorts clean-up chain string (afftdn tn=1 nr 18, deesser 0.25, agate 1.6) and the per-source echo `audio_extra`: in `pipeline.py` and the build log rows 69 and 170 only; `shorts-formats.md` carried the rule without the chain.
11. Riverside sync proof by bleed cross-correlation (guest G's stage step) and the second-track trap (a mic switch opens a new track; its Aligned export is digitally silent before the switch; stitch them) (2026-09-18).
12. Laughs are found by 3.5 to 8 Hz envelope modulation, not loudness (2026-09-21; `find_laughs.py`).
13. Splice sibilance can manufacture a word in the captions ("FONTS") (2026-09-02).
14. The co-host's long-form mixing lessons: judge a level on the whole video, never a one-minute sample; the open's bed is "there for energy" and over-ducking made it quiet (2026-10-17; her project README; `sound_mix.py`).
15. The editor's own masterclass silence rule (pauses over 1.5 s inside a take to 0.8 s) and the editor's guest R bed ruling (2026-10-12 and 2026-09-09), not in `kinds/masterclass.md` or `podcast-edit.md`.
16. Overlapping segment padding (27 to 110 ms) replays words at joins (2026-09-25).
17. The host's verbatim "keep the ums ... delete the double takes" (guest Z's options brief, not taste) and the stutter against restart split (2026-09-18).
18. The flubbed-word regeneration method (the script docstring and the lab page only).
19. The studio-voice enhancement the creator liked on 22 Sep: tool unnamed on tape, untested (tutorial-1's edit notes).

Contradictions inside guidance the editor does read (would actively mislead them):
20. The runbook said the intro bed is 0.10; `content/reference/podcast-edit.md` says 0.0224 (about 20 dB under) after the host called the louder bed "way too loud" (2026-09-28). **[Fixed 2026-10-29: the runbook now says 0.0224]**
21. `.claude/skills/shorts-editor/references/style.md` said compose.sh music is 0.06; the skill, `compose.sh` and `lessons.md` say 0.02 and name 0.06 as retired. **[Fixed 2026-10-29: style.md now says 0.02]**
22. Shorts loudness: shorts-editor compose.sh normalised the voice to -16 LUFS; the podcast, wave-1 and podcast shorts pipelines targeted -14. No ruling picked one. **[Fixed 2026-10-29: -14 everywhere, the creator's ruling]**
23. `editing-rules.md` rule 10 forbids synthesised transition sounds (the co-host, 22 Oct); `footage_bg_shift.py` synthesised its whoosh (10 Oct). The scope of rule 10 for the creator's footage was unruled. **[Fixed 2026-10-29: ruled: real only, every machine]**
24. The user-level video-use skill (outside the project) told sessions there was no ElevenLabs key; stale since 2026-09-09. **[Fixed 2026-10-29: rewritten the same day]**

Untested, stated as such: voice anonymisation (rubberband or ElevenLabs speech-to-speech) has never been run; tutorial-2's `audio_extra` echo pass was "not rendered"; the host's laugh treatment is "Untested by ear until he hears it"; the de-reverb scripts are "Untested in this folder".

Could not reach: the full set of sound-matching work-log rows (about 578K characters) was filtered by keyword, not read row by row, so a lesson worded without any of the swept terms may be missing. Session transcripts were not read. The co-host's denoise build files were not found under version control, so that lesson rests on the work-log row alone.
