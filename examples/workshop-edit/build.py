#!/usr/bin/env python3
"""Cut a recorded workshop (a video call with a shared deck and an attendee gallery) into finished videos.

  python3 build.py silences            # measure the room's silences once -> <out>/silences.json
  python3 build.py plan <cut>          # <out>/<cut>.segments.json: keep ranges, snapped to measured quiet,
                                       #   silences tightened, split at every layout hand-off
  python3 build.py probe               # one frame per layout through the SHIPPING segment path, before any long run
  python3 build.py render <cut>        # segments -> <out>/<cut>.joined.mp4 (1.0x, no captions, audio sample-exact)
  python3 build.py captions <cut>      # <out>/<cut>.captions.ass on the joined timeline (karaoke, one libass pass)
  python3 build.py finalize <cut>      # captions burned, THEN the speed pass, then loudnorm -> <out>/<cut>.mp4
  python3 build.py chapters <cut>      # chapter lines on the FINAL (sped) timeline
  python3 build.py selftest            # offline checks of the caption and config logic; no recording needed

All settings live in config.json (copy config.example.json). Paths in it are relative to the config file.

The rules this pipeline encodes, each paid for once:
  - Silences of 1.0 s or more tighten to about 0.6 s; never a kept sliver under 1.2 s; never merge across 2 keep
    ranges. A pause is cut only BETWEEN 2 transcript words, never through a quiet word.
  - Every cut boundary snaps to measured audio energy (boundary.py), not to the transcript's word spans.
  - Attendees: soft blur over the gallery (a person stays a person), hard blur on every name strip, presenters
    put back sharp. boxblur radius caps are validated before rendering because ffmpeg fails them silently.
  - Video segments render without audio; the audio is cut to each segment's REAL frame count, read back from the
    file, sample-exact, with 30 ms fades. Frame-quantised segments drift otherwise.
  - Every looped image input carries an explicit -t; every ffmpeg runs with -nostdin and a bounded wait.
  - Captions burn BEFORE the speed pass. Chapters are divided by the speed factor.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import hex_to_ass, load_config, resolve  # noqa: E402

CFG = None  # set in main()


# ---------------------------------------------------------------- helpers

def F():
    return CFG["frame"]


def run_bounded(cmd, dur):
    """A segment render at 0% CPU is a deadlock, not a slow render: bound the wait, retry once."""
    limit = 60 + 3 * max(dur, 1.0)
    for attempt in (1, 2):
        try:
            subprocess.run(cmd, check=True, timeout=limit)
            return
        except subprocess.TimeoutExpired:
            print(f"  segment stalled past {limit:.0f}s (attempt {attempt}), retrying" if attempt == 1
                  else "  segment stalled twice; stopping", flush=True)
    raise SystemExit("a segment render stalled twice: check the input window and the machine's memory")


def validate_blur(cfg):
    """ffmpeg's boxblur fails a render with no useful message when a radius is over its cap."""
    b = cfg.get("blur", {})
    problems = []
    for key in ("soft_radius", "label_luma_radius"):
        if b.get(key, 0) > 24:
            problems.append(f"blur.{key} = {b[key]} exceeds boxblur's luma cap of 24")
    for name, g in cfg.get("grids", {}).items():
        cap = g["label_h"] // 4  # chroma height of a 4:2:0 strip is label_h / 2; the radius cap is half that
        if b.get("label_chroma_radius", 0) > cap:
            problems.append(f"blur.label_chroma_radius = {b['label_chroma_radius']} exceeds {cap} "
                            f"(half the chroma height of grid {name}'s {g['label_h']}px label strip)")
    return problems


# ---------------------------------------------------------------- silences and plan

def silences():
    s = CFG["silence"]
    log = subprocess.run(["ffmpeg", "-nostdin", "-v", "info", "-i", str(CFG["recording"]), "-vn", "-af",
                          f"silencedetect=n={s['threshold_db']}dB:d={s['min_s']}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    pairs = [[a, b] for a, b in zip(starts, ends) if b > a]
    Path(CFG["silences"]).write_text(json.dumps(pairs))
    print(f"{len(pairs)} silences of {s['min_s']}s or more at {s['threshold_db']} dB -> {CFG['silences']}")
    if not pairs:
        print("  none found: that means a noisy room, not a clean tape. Try a higher threshold_db (-35 or -30).")


def load_words():
    p = CFG.get("transcript")
    if not p or not Path(p).exists():
        return []
    return [{"t": w["text"].strip(), "s": w["start"], "e": w["end"], "spk": w.get("speaker_id")}
            for w in json.loads(Path(p).read_text())["words"]
            if w.get("type", "word") == "word" and w["text"].strip()]


def layout_bounds():
    b = set()
    for L in CFG.get("layouts", []):
        b.add(L["start"])
        b.add(L["end"])
    return sorted(b)


def plan(cut):
    from boundary import Snapper
    s = CFG["silence"]
    keeps, moved = Snapper(CFG).snap_units([tuple(x) for x in CFG["cuts"][cut]])
    for kind, t0, t1, w in moved:
        print(f"  snapped {kind} {t0:.2f} -> {t1:.2f} (was on \"{w}\")")
    sil = json.loads(Path(CFG["silences"]).read_text()) if Path(CFG["silences"]).exists() else []
    if not sil:
        print("  no silences.json: run `build.py silences` first, or the cut keeps every pause")
    starts = sorted(w["s"] for w in load_words())
    segs = []
    for a, b in keeps:
        frozen = any(abs(a - fa) < 0.5 and abs(b - fb) < 0.5 for fa, fb in CFG.get("no_tighten", {}).get(cut, []))
        cuts = []
        if not frozen:
            for s0, s1 in sil:
                if s0 < a or s1 > b or (s1 - s0) < s["min_s"]:
                    continue
                c0, c1 = s0 + s["leave_each_side_s"], s1 - s["leave_each_side_s"]
                # a pause is cut only BETWEEN 2 words: a word starting inside it is a quiet word, not silence
                if any(c0 - 0.05 <= st < c1 for st in starts):
                    continue
                cuts.append((c0, c1))
        t, local = a, []
        for c0, c1 in cuts:
            if c0 > t:
                local.append((t, c0))
            t = c1
        if b > t:
            local.append((t, b))
        merged = []  # machine-gun guard, never across 2 keep ranges
        for x, y in local:
            if merged and (y - x) < s["min_sliver_s"]:
                merged[-1] = (merged[-1][0], y)
            else:
                merged.append((x, y))
        segs += merged
    final = []
    for s0, s1 in segs:
        for bnd in sorted(set(layout_bounds() + list(CFG.get("splits", {}).get(cut, [])))):
            if s0 < bnd < s1:
                final.append((s0, bnd))
                s0 = bnd
        final.append((s0, s1))
    final = [(round(x, 3), round(y, 3)) for x, y in final if y - x > 0.2]
    tl, acc = [], 0.0
    for x, y in final:
        tl.append({"raw_in": x, "raw_out": y, "out_in": round(acc, 3)})
        acc += y - x
    out = CFG["out_dir"] / f"{cut}.segments.json"
    out.write_text(json.dumps({"segments": final, "duration": acc, "timeline": tl}, indent=1))
    sp = CFG["speed"]
    print(f"{cut}: {len(final)} segments, {acc / 60:.1f} min at 1.0x, {acc / sp / 60:.1f} min at {sp}x -> {out}")


# ---------------------------------------------------------------- layouts and segment filters

def mode(t):
    for L in CFG.get("layouts", []):
        if L["start"] <= t < L["end"]:
            return L["kind"], L.get("grid")
    return "grid", CFG["default_grid"]


def background():
    from PIL import Image, ImageDraw, ImageFont
    p = CFG["out_dir"] / "bg-gallery.png"
    if p.exists():
        return p
    im = Image.new("RGB", (F()["w"], F()["h"]), F()["background"])
    title = CFG.get("grid_title", "")
    if title:
        fonts = sorted(Path(CFG["fonts_dir"]).glob("*.ttf")) if CFG.get("fonts_dir") else []
        font = ImageFont.truetype(str(fonts[0]), 64) if fonts else ImageFont.load_default()
        ImageDraw.Draw(im).text((64, 84), title, font=font, fill="#111111")
    im.save(p)
    return p


def share_filter():
    sh = CFG["share"]
    dw, dh, dx, dy = sh["deck_crop"]
    fw, fh, fx, fy = sh["face_crop"]
    sw, shh, sx, sy = sh["deck_slot"]
    pw, ph, px, py = sh["face_slot"]
    return (f"[1:v]setpts=PTS-STARTPTS,split=2[r0][r1];"
            f"[r0]crop={dw}:{dh}:{dx}:{dy},scale={sw}:{shh}[d];"
            f"[r1]crop={fw}:{fh}:{fx}:{fy},scale={pw}:{ph},pad={pw + 8}:{ph + 8}:4:4:white[s];"
            f"[0:v][d]overlay={sx}:{sy}:shortest=1[b];[b][s]overlay={px - 4}:{py - 4}[v]")


def grid_filter(name):
    """Soft blur over the whole gallery (a person stays a person), a hard blur on every tile's name strip
    (no label survives), then the presenters' tiles put back sharp."""
    g, b = CFG["grids"][name], CFG["blur"]
    rows, cols, tw, th, gap, lh = g["rows"], g["cols"], g["tile_w"], g["tile_h"], g["row_gap"], g["label_h"]
    gw = cols * tw
    gh = rows * th + gap * (rows - 1)
    out_h = CFG["grid_out_h"]
    out_w = round(gw * out_h / gh / 2) * 2
    x0 = (F()["w"] - out_w) // 2
    keep = [tuple(k) for k in g.get("keep", [])]
    chain = (f"[1:v]setpts=PTS-STARTPTS,split={1 + len(keep)}[raw]" + "".join(f"[k{i}]" for i in range(len(keep))) + ";"
             f"[raw]boxblur={b['soft_radius']}:{b['soft_passes']},split={rows + 1}[bl]"
             + "".join(f"[st{r}]" for r in range(rows)) + ";")
    cur = "bl"
    for r in range(rows):
        y = g["y"] + r * (th + gap) + th - lh
        chain += (f"[st{r}]crop={gw}:{lh}:{g['x']}:{y},boxblur=luma_radius={b['label_luma_radius']}:luma_power=4:"
                  f"chroma_radius={b['label_chroma_radius']}:chroma_power=4[sb{r}];[{cur}][sb{r}]overlay={g['x']}:{y}[b{r}];")
        cur = f"b{r}"
    for i, (r, c) in enumerate(keep):
        tx, ty = g["x"] + c * tw, g["y"] + r * (th + gap)
        chain += f"[k{i}]crop={tw}:{th}:{tx}:{ty}[kt{i}];[{cur}][kt{i}]overlay={tx}:{ty}[c{i}];"
        cur = f"c{i}"
    chain += (f"[{cur}]crop={gw}:{gh}:{g['x']}:{g['y']},scale={out_w}:{out_h}[g];"
              f"[0:v][g]overlay={x0}:{CFG['grid_y']}:shortest=1[v]")
    return chain


def in_override(cut, a, b):
    ov = CFG.get("overrides", {}).get(cut)
    return bool(ov) and any(ra - 0.5 <= a and b <= rb + 0.5 for ra, rb in ov["ranges"])


def still_for(cut, a, b):
    for ra, rb, png in CFG.get("deck_stills", {}).get(cut, []):
        if ra - 0.01 <= a and b <= rb + 0.01:
            return resolve(CFG, png)
    return None


def seg_cmd(i, a, b, cut, ov_off=0.0):
    """The ONE function that builds a segment. `probe` uses it too, so a preview frame is the shipping frame."""
    W, H, FPS = F()["w"], F()["h"], F()["fps"]
    dur = b - a
    kind, grid = mode(a)
    out = CFG["out_dir"] / f"{cut}-seg" / f"{i:04d}.mp4"
    out.parent.mkdir(exist_ok=True)
    enc = ["-map", "[v]", "-an", "-t", f"{dur:.3f}", "-r", str(FPS)] + CFG["video_codec_args"] + ["-pix_fmt", "yuv420p", str(out)]
    colour = "0x" + F()["background"].lstrip("#")
    base = ["ffmpeg", "-nostdin", "-v", "error", "-y"]
    png = still_for(cut, a, b)
    if png and kind == "share":
        sh = CFG["share"]
        sw, shh, sx, sy = sh["deck_slot"]
        fw, fh, fx, fy = sh["face_crop"]
        pw, ph, px, py = sh["face_slot"]
        filt = (f"[2:v]scale={sw}:{shh},format=yuv420p[d];[1:v]setpts=PTS-STARTPTS,crop={fw}:{fh}:{fx}:{fy},scale={pw}:{ph},"
                f"pad={pw + 8}:{ph + 8}:4:4:white[s];[0:v][d]overlay={sx}:{sy}:shortest=1[b];[b][s]overlay={px - 4}:{py - 4}[v]")
        return base + ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", f"color=c={colour}:s={W}x{H}:r={FPS}",
                       "-ss", f"{a:.3f}", "-t", f"{dur:.3f}", "-i", str(CFG["recording"]),
                       "-loop", "1", "-t", f"{dur:.3f}", "-framerate", str(FPS), "-i", str(png),
                       "-filter_complex", filt] + enc, out
    if in_override(cut, a, b):
        mp4 = resolve(CFG, CFG["overrides"][cut]["video"])
        return base + ["-ss", f"{ov_off:.3f}", "-t", f"{dur:.3f}", "-i", str(mp4),
                       "-filter_complex", "[0:v]setpts=PTS-STARTPTS[v]"] + enc, out
    cmd = list(base)
    if kind == "share":
        cmd += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", f"color=c={colour}:s={W}x{H}:r={FPS}"]
        filt = share_filter()
    else:
        cmd += ["-loop", "1", "-t", f"{dur:.3f}", "-framerate", str(FPS), "-i", str(background())]
        filt = grid_filter(grid)
    cmd += ["-ss", f"{a:.3f}", "-t", f"{dur:.3f}", "-i", str(CFG["recording"]), "-filter_complex", filt] + enc
    return cmd, out


def check_blur_or_die():
    problems = validate_blur(CFG)
    if problems:
        raise SystemExit("blur settings would fail the render silently:\n  " + "\n  ".join(problems))


def probe():
    check_blur_or_die()
    for t in CFG.get("probe_times", []):
        kind, grid = mode(t)
        name = f"{kind}-{grid}" if grid else kind
        cmd, out = seg_cmd(0, t, t + 1.0, f"probe-{int(t)}")
        run_bounded(cmd, 1.0)
        png = CFG["out_dir"] / f"probe-{int(t)}-{name}.png"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(out), "-frames:v", "1", str(png)], check=True)
        print("probe", png)
    print("Look at every probe frame at full size before starting a long render.")


# ---------------------------------------------------------------- render and join

SR = 48000


def source_wav():
    p = CFG["out_dir"] / "source.wav"
    if not p.exists():
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(CFG["recording"]), "-vn", "-ac", "2",
                        "-ar", str(SR), "-c:a", "pcm_s16le", str(p)], check=True)
    return p


def render(cut):
    check_blur_or_die()
    segs = json.loads((CFG["out_dir"] / f"{cut}.segments.json").read_text())["segments"]
    lines, ov_off = [], 0.0
    for i, (a, b) in enumerate(segs):
        cmd, out = seg_cmd(i, a, b, cut, ov_off)
        if in_override(cut, a, b):
            ov_off += b - a
        if not (out.exists() and out.stat().st_size > 1000):  # content cache: a retry only redoes what is missing
            run_bounded(cmd, b - a)
        lines.append(f"file '{out}'")
        if i % 10 == 0:
            print(f"{cut} seg {i}/{len(segs)} done", flush=True)
    (CFG["out_dir"] / f"{cut}.concat.txt").write_text("\n".join(lines) + "\n")
    join(cut)


def join(cut):
    """Concat the video segments, then cut the audio to the REAL frame count of each segment (sample-exact,
    30 ms fades at every edge) so video, audio and captions share one timeline."""
    import wave
    import numpy as np
    FPS = F()["fps"]
    if SR % FPS:
        raise SystemExit(f"fps {FPS} does not divide {SR}: pick a frame rate that does (24, 25, 30, 48, 50, 60)")
    out_dir = CFG["out_dir"]
    d = json.loads((out_dir / f"{cut}.segments.json").read_text())
    tl, acc = [], 0
    for i, (a, b) in enumerate(d["segments"]):
        seg = out_dir / f"{cut}-seg" / f"{i:04d}.mp4"
        n = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                                "stream=nb_read_frames", "-of", "csv=p=0", str(seg)],
                               capture_output=True, text=True).stdout.strip())
        tl.append({"raw_in": a, "raw_out": b, "out_in": round(acc / FPS, 4), "frames": n})
        acc += n
    d["timeline"], d["duration"] = tl, acc / FPS
    (out_dir / f"{cut}.segments.json").write_text(json.dumps(d, indent=1))
    src = wave.open(str(source_wav()), "rb")
    fade = int(0.03 * SR)
    ramp = np.linspace(0, 1, fade, dtype=np.float32)
    wav_path = out_dir / f"{cut}.audio.wav"
    dst = wave.open(str(wav_path), "wb")
    dst.setnchannels(2)
    dst.setsampwidth(2)
    dst.setframerate(SR)
    for seg in tl:
        ns = seg["frames"] * (SR // FPS)
        src.setpos(min(int(round(seg["raw_in"] * SR)), src.getnframes()))
        x = np.frombuffer(src.readframes(ns), dtype=np.int16).reshape(-1, 2).astype(np.float32)
        if len(x) < ns:
            x = np.vstack([x, np.zeros((ns - len(x), 2), np.float32)])
        x[:fade] *= ramp[:, None]
        x[-fade:] *= ramp[::-1, None]
        dst.writeframes(x.astype(np.int16).tobytes())
    dst.close()
    src.close()
    vid = out_dir / f"{cut}.video.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i",
                    str(out_dir / f"{cut}.concat.txt"), "-c", "copy", str(vid)], check=True)
    joined = out_dir / f"{cut}.joined.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(vid), "-i", str(wav_path), "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", str(joined)], check=True)
    from common import probe_duration
    print(f"JOINED {joined} video {probe_duration(joined, 'v:0'):.3f}s audio {probe_duration(joined, 'a:0'):.3f}s "
          f"frames {acc} (the 2 durations should agree within a frame)", flush=True)


# ---------------------------------------------------------------- captions

BACK = re.compile(r"^(hmm+|mm+-?hmm*|mm+|uh-?huh|yeah|yes|okay|right|wow|oh|uh|um|huh|great|exactly|absolutely|"
                  r"sure|perfect|got it|cool|lovely)[.,!?]*$", re.I)
UNITS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                    "fourteen fifteen sixteen seventeen eighteen nineteen".split())}
TENS = {w: 10 * (i + 2) for i, w in enumerate("twenty thirty forty fifty sixty seventy eighty ninety".split())}
NUMWORD = re.compile(r"^(a|an|zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|"
                     r"fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|"
                     r"ninety|hundred|thousand|million|point)(-[a-z]+)?$", re.I)


def small(tok):
    t = tok.lower()
    if t in UNITS:
        return UNITS[t]
    if t in TENS:
        return TENS[t]
    if "-" in t:
        a, b = t.split("-", 1)
        if a in TENS and b in UNITS:
            return TENS[a] + UNITS[b]
    return None


def numeralize(words):
    """Spoken number runs become numerals: 'sixty-five percent' -> 65%, 'nine thousand dollars' -> $9,000,
    'two point five million' -> 2.5 million. A standalone 'one' or 'a' stays a word: 'one' is a pronoun
    ("see them one by one"), and converting it shipped "1 by 1" 15 times in one cut."""
    out, i = [], 0
    while i < len(words):
        j, run = i, []
        while j < len(words) and NUMWORD.match(words[j]["t"].rstrip(".,!?")):
            run.append(words[j])
            j += 1
        toks = [w["t"].rstrip(".,!?").lower() for w in run]
        value, frac = None, None
        if run and any(t not in ("a", "an", "one", "point") for t in toks):
            try:
                total, cur, k = 0, 0, 0
                while k < len(toks):
                    t = toks[k]
                    if t in ("a", "an"):
                        cur = 1
                    elif t == "hundred":
                        cur = (cur or 1) * 100
                    elif t == "thousand":
                        total += (cur or 1) * 1000
                        cur = 0
                    elif t == "million":
                        total += (cur or 1)
                        frac = "million"
                        cur = 0
                    elif t == "point":
                        dec = toks[k + 1] if k + 1 < len(toks) else None
                        dd = small(dec) if dec else None
                        if dd is None:
                            raise ValueError
                        cur = float(f"{cur}.{dd}")
                        k += 1
                    else:
                        sv = small(t)
                        if sv is None:
                            raise ValueError
                        cur += sv
                    k += 1
                value = total + cur
                if (len(toks) == 2 and all(small(t) is not None for t in toks) and small(toks[0]) >= 20
                        and small(toks[1]) >= 10):
                    value = small(toks[0]) * 100 + small(toks[1])  # 'twenty twenty-six' style years
            except ValueError:
                value = None
        if value is None or not run or (len(run) == 1 and toks[0] in ("a", "an", "one", "point")):
            out.append(words[i])
            i += 1
            continue
        punct = (re.findall(r"[.,!?]+$", run[-1]["t"]) or [""])[0]
        nxt = words[j]["t"].rstrip(".,!?").lower() if j < len(words) else ""
        year = len(toks) == 2 and 1900 <= value <= 2099 and "hundred" not in toks and "thousand" not in toks
        if frac == "million":
            txt = (f"{value:g}" if value != int(value) else f"{int(value)}") + " million"
        elif year:
            txt = str(int(value))
        else:
            txt = f"{value:,.1f}".rstrip("0").rstrip(".") if value != int(value) else f"{int(value):,}"
        end = run[-1]["e"]
        if nxt in ("percent", "dollars"):
            txt = txt + "%" if nxt == "percent" else "$" + txt
            punct = (re.findall(r"[.,!?]+$", words[j]["t"]) or [""])[0]
            end = words[j]["e"]
            j += 1
        out.append({"t": txt + punct, "s": run[0]["s"], "e": end, "spk": run[0].get("spk")})
        i = j
    return out


def phrases(words, gap=0.6):
    ph, cur = [], []
    for w in words:
        if cur and w["s"] - cur[-1]["e"] > gap:
            ph.append(cur)
            cur = []
        cur.append(w)
    if cur:
        ph.append(cur)
    return ph


def break_cost(ws, i):
    """Cost of ending a caption group after word i. Language decides, not a word count."""
    t = ws[i]["t"].rstrip('"”')
    if t.endswith((".", "?", "!")):
        return 0.0
    if i + 1 < len(ws) and ws[i + 1].get("spk") != ws[i].get("spk"):
        return 0.0
    if t.endswith((",", ";", ":")):
        return 1.0
    if i + 1 < len(ws) and ws[i + 1]["s"] - ws[i]["s"] > 0.9:
        return 1.5  # a real pause (measured on starts, because word ends carry the trailing pause)
    return 4.0


def break_groups(ws, width, max_words, max_px, gap):
    """Shortest-path line breaking over the whole phrase. Greedy breaking leaves 3 word fragments after every
    forced break; a hard word cap put 524 of 705 lines at exactly 4 words on one cut."""
    n = len(ws)
    INF = float("inf")
    best = [0.0] + [INF] * n
    back = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(max(0, j - max_words - 1), j):
            k = j - i
            px = sum(width(w["t"]) for w in ws[i:j]) + gap * (k - 1)
            if k > max_words + 1 or (px > max_px and k > 1):
                continue
            size = 3.0 if (k == 1 and n > 1) else (2.0 if k == max_words + 1 else 0.0)
            cost = best[i] + size + (break_cost(ws, j - 1) if j < n else 0.0)
            if cost < best[j]:
                best[j], back[j] = cost, i
    groups, j = [], n
    while j > 0:
        groups.append(ws[back[j]:j])
        j = back[j]
    return groups[::-1]


def fmt_t(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def ass_header(c, W, H):
    white = hex_to_ass(c["text_colour"])
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,{c['font_name']},{round(c['size_px'] / c['calib'])},{white},{white},&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,{c['outline']},2,2,60,60,{H - c['y_base']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def word_override(cx, y, on_ms, off_ms, base, hi):
    """The base colour is pinned FIRST. Without it libass resolves the first \\t target for any time before its
    start, every word arrives highlighted, and the highlight drains backwards as the words are spoken."""
    return (f"{{\\an2\\pos({cx:.0f},{y})\\1c{base}\\t({on_ms},{on_ms + 40},\\1c{hi})"
            f"\\t({off_ms},{off_ms + 60},\\1c{base})\\fad(50,30)}}")


def measurer(c):
    from PIL import Image, ImageDraw, ImageFont
    fp = Path(CFG["fonts_dir"]) / c["font_file"] if CFG.get("fonts_dir") else None
    if fp and fp.exists():
        font = ImageFont.truetype(str(fp), c["size_px"])
    else:
        print(f"  caption font file not found ({fp}); measuring with PIL's default font, widths are approximate")
        font = ImageFont.load_default()
    dr = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    # the visible width as libass draws it: the advance plus both outlines (style Spacing is 0 here)
    return lambda t: dr.textlength(t, font=font) + 2 * c["outline"]


def captions(cut):
    c = CFG["captions"]
    W, H = F()["w"], F()["h"]
    width = measurer(c)
    base, hi = hex_to_ass(c["text_colour"]), hex_to_ass(c["highlight_colour"])
    tl = json.loads((CFG["out_dir"] / f"{cut}.segments.json").read_text())["timeline"]
    raw = load_words()
    if not raw:
        raise SystemExit("no transcript words: set \"transcript\" in the config")
    raw = [w for w in raw if not re.match(r"^[Uu][hm]+[.,]?$", w["t"])]       # captions drop standalone uh/um
    raw = [w for w in raw if not re.match(r"^\w{1,4}-$", w["t"])]            # a false start is dropped, never de-dashed
    for w in raw:
        m = re.match(r"^(\$?)(\d{4,})([.,!?%]*)$", w["t"])
        if m and not (m.group(1) == "" and 1900 <= int(m.group(2)) <= 2099):
            w["t"] = m.group(1) + f"{int(m.group(2)):,}" + m.group(3)
    by_spk = {}
    for w in raw:
        by_spk.setdefault(w["spk"], []).append(w)
    phr = {k: [numeralize(p) for p in phrases(v)] for k, v in by_spk.items()}

    def overlaps_other(s, e, spk):
        return any(op[0]["s"] < e and op[-1]["e"] > s and not (len(op) <= 3 and all(BACK.match(w["t"]) for w in op))
                   for k, v in phr.items() if k != spk for op in v)

    events = []
    # A word belongs to the segment its START falls in. Its end may run into the next segment when the 2 are
    # contiguous on the raw timeline, and is clamped otherwise. Transcribers attach the pause after a word to the
    # word, so an end-based filter drops words that are fully audible before a cut placed on measured quiet.
    for i, seg in enumerate(tl):
        s0, e0, o0 = seg["raw_in"], seg["raw_out"], seg["out_in"]
        ext = e0
        for nxt in tl[i + 1:]:
            if abs(nxt["raw_in"] - ext) > 0.002:
                break
            ext = nxt["raw_out"]
        for spk, plist in phr.items():
            for ph in plist:
                inw = [dict(w, e=min(w["e"], ext)) for w in ph if s0 - 0.05 <= w["s"] < e0]
                if not inw:
                    continue
                if len(inw) <= 3 and all(BACK.match(w["t"]) for w in inw) and overlaps_other(inw[0]["s"], inw[-1]["e"], spk):
                    continue  # a backchannel under the other speaker's sentence
                for ch in break_groups(inw, width, c["max_words"], c["max_px"], c["gap_px"]):
                    texts = [w["t"].replace("{", "").replace("}", "") for w in ch]
                    widths = [width(t) for t in texts]
                    x = (W - (sum(widths) + c["gap_px"] * (len(texts) - 1))) / 2
                    g_s = max(0.0, ch[0]["s"] - s0 - 0.06) + o0
                    g_e = min(ext - s0, ch[-1]["e"] - s0 + 0.16) + o0
                    if g_e <= g_s:
                        continue
                    wl = []
                    for wd, txt, wpx in zip(ch, texts, widths):
                        wl.append((x + wpx / 2, txt, max(wd["s"] - s0, 0) + o0, min(wd["e"] - s0, ext - s0) + o0))
                        x += wpx + c["gap_px"]
                    events.append({"s": g_s, "e": g_e, "w": wl})
    events.sort(key=lambda g: g["s"])
    for i in range(len(events) - 1):  # one group on screen at a time
        if events[i + 1]["s"] < events[i]["e"]:
            events[i]["e"] = max(events[i]["s"] + 0.12, events[i + 1]["s"] - 0.01)
    n = 0
    with open(CFG["out_dir"] / f"{cut}.captions.ass", "w") as fo:
        fo.write(ass_header(c, W, H))
        for g in events:
            for cx, txt, ws, we in g["w"]:
                on = max(0, int((ws - g["s"]) * 1000))
                off = max(1, int((we - g["s"]) * 1000))
                fo.write(f"Dialogue: 0,{fmt_t(g['s'])},{fmt_t(g['e'])},Main,,0,0,0,,"
                         f"{word_override(cx, c['y_base'], on, off, base, hi)}{txt}\n")
                n += 1
    print(f"{cut}: {len(events)} caption groups, {n} word events. Read them back across every join before finalizing.")


# ---------------------------------------------------------------- finalize and chapters

def finalize(cut):
    out_dir, sp = CFG["out_dir"], CFG["speed"]
    joined, ass, final = out_dir / f"{cut}.joined.mp4", out_dir / f"{cut}.captions.ass", out_dir / f"{cut}.mp4"
    fonts = f":fontsdir={CFG['fonts_dir']}" if CFG.get("fonts_dir") else ""
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(joined),
                    "-vf", f"ass={ass}{fonts},setpts=PTS/{sp}",
                    "-af", f"atempo={sp},loudnorm=I=-14:TP=-1.5:LRA=11",
                    *CFG["video_codec_args"], "-pix_fmt", "yuv420p", "-r", str(F()["fps"]),
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(final)], check=True)
    print("FINAL", final, final.stat().st_size, flush=True)


def chapters(cut):
    tl = json.loads((CFG["out_dir"] / f"{cut}.segments.json").read_text())["timeline"]

    def to_out(t):
        for seg in tl:
            if seg["raw_in"] <= t < seg["raw_out"]:
                return seg["out_in"] + (t - seg["raw_in"])
            if t < seg["raw_in"]:
                return seg["out_in"] if seg["raw_in"] - t < 30.0 else None
        return None

    lines = []
    for t, title in CFG.get("chapters", []):
        o = to_out(t)
        if o is None:
            continue
        o /= CFG["speed"]  # timestamps handed to a human come off the DELIVERED (sped) timeline
        lines.append(f"{int(o // 60):02d}:{int(o % 60):02d} {title}")
    (CFG["out_dir"] / f"{cut}.chapters.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("Check these against the delivered file before they go in a description.")


# ---------------------------------------------------------------- selftest

def selftest():
    fails = 0

    def ok(cond, msg):
        nonlocal fails
        print(("PASS " if cond else "FAIL ") + msg)
        fails += 0 if cond else 1

    def w(*toks):
        return [{"t": t, "s": i * 0.3, "e": i * 0.3 + 0.25, "spk": 0} for i, t in enumerate(toks)]

    txt = lambda ws: " ".join(x["t"] for x in numeralize(ws))
    ok(txt(w("sixty-five", "percent")) == "65%", "sixty-five percent -> 65%")
    ok(txt(w("nine", "thousand", "dollars")) == "$9,000", "nine thousand dollars -> $9,000")
    ok(txt(w("two", "point", "five", "million")) == "2.5 million", "two point five million -> 2.5 million")
    ok(txt(w("see", "them", "one", "by", "one")) == "see them one by one", "'one' stays a pronoun")
    ok(txt(w("the", "big", "one,")) == "the big one,", "'the big one,' is left alone")
    ok(txt(w("twenty", "twenty-six")) == "2026", "twenty twenty-six -> 2026")

    words = w("So", "I", "was", "in", "an", "instance", "where,", "a", "firm", "was", "trying", "to", "decide.")
    groups = break_groups(words, lambda t: 20.0 * len(t), 4, 900, 22)
    joined = [" ".join(x["t"] for x in g) for g in groups]
    ok(any(j.endswith("where,") for j in joined), f"breaks at the clause, not at a word count: {joined}")
    ok(all(len(g) <= 5 for g in groups), "no group over max_words + 1")

    ov = word_override(960, 1030, 100, 400, "&H00FFFFFF", "&H0000D4FF")
    ok(ov.index("\\1c&H00FFFFFF") < ov.index("\\t("), "karaoke base colour pinned before the transitions")
    ok(hex_to_ass("#FFD400") == "&H0000D4FF", "hex_to_ass converts RGB to ASS BGR")

    bad = {"blur": {"soft_radius": 30, "label_luma_radius": 20, "label_chroma_radius": 20},
           "grids": {"g": {"label_h": 48}}}
    probs = validate_blur(bad)
    ok(len(probs) == 2, f"blur caps caught before render ({len(probs)} problems)")
    good = {"blur": {"soft_radius": 16, "label_luma_radius": 20, "label_chroma_radius": 10},
            "grids": {"g": {"label_h": 48}}}
    ok(validate_blur(good) == [], "the example blur settings pass")

    hdr = ass_header({"font_name": "X", "size_px": 56, "calib": 0.63, "outline": 4, "y_base": 1030,
                      "text_colour": "#FFFFFF"}, 1920, 1080)
    fmt = [l for l in hdr.splitlines() if l.startswith("Format:") and "Text" in l][0]
    ok(len(fmt.split(":", 1)[1].split(",")) == 10, "ASS Dialogue Format line declares all 10 fields")
    print(f"\n{'all passed' if not fails else f'{fails} failed'}")
    return 1 if fails else 0


# ---------------------------------------------------------------- main

def main():
    global CFG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("op", choices=["silences", "plan", "probe", "render", "captions", "finalize", "chapters", "selftest"])
    ap.add_argument("cut", nargs="?", help="a cut name from config.json \"cuts\"")
    ap.add_argument("--config", default=None, help="path to config.json (default: $WORKSHOP_CONFIG or ./config.json)")
    args = ap.parse_args()
    if args.op == "selftest":
        sys.exit(selftest())
    CFG = load_config(args.config, need_recording=args.op not in ("captions", "chapters"))
    if args.op in ("plan", "render", "captions", "finalize", "chapters") and not args.cut:
        ap.error(f"{args.op} needs a cut name: one of {', '.join(CFG.get('cuts', {}))}")
    if args.cut and args.cut not in CFG.get("cuts", {}) and args.op == "plan":
        ap.error(f"unknown cut {args.cut!r}: one of {', '.join(CFG.get('cuts', {}))}")
    fn = {"silences": silences, "plan": plan, "probe": probe, "render": render, "captions": captions,
          "finalize": finalize, "chapters": chapters}[args.op]
    fn(args.cut) if args.op in ("plan", "render", "captions", "finalize", "chapters") else fn()


if __name__ == "__main__":
    main()
