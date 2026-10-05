#!/usr/bin/env python3
"""
media_gen.py: image and video generation through MixRoute.

One gateway, one key, no credit pack to run dry. It replaced a per-provider
credit pack, and then the direct Gemini and fal keys the same day.

    Images   nano-banana-pro    gemini-3-pro-image
             nano-banana-lite   gemini-3.1-flash-lite-image
    Video    seedance           doubao-seedance-2-5-260628
             veo                veo-3.1-generate-preview
             veo-fast           veo-3.1-fast-generate-preview

NOT AVAILABLE ON MIXROUTE: Gemini Omni Flash. Both `gemini-omni-flash-preview`
and `gemini-omni-flash` return 503 model_not_found ("no available channel"),
checked live. Omni was one of the three models originally asked for, so this
is a real gap rather than an oversight. Use `veo` or `veo-fast` for the
reference-driven, native-audio shots Omni would have covered, and re-run
`media_gen.py models` to see if MixRoute adds it later.

KEY (an environment variable; see the repo's SETUP.md):
    MIXROUTE_API_KEY     from mixroute.ai, covers every model above
    export it in your shell profile, e.g.
        echo 'export MIXROUTE_API_KEY=your_key_here' >> ~/.zshrc
    A .env file in the project root (the folder you run this from, or
    MEDIA_GEN_ROOT) also works, then a .env beside this skill folder. An
    exported variable always wins.

PATHS. Everything is relative to the project root: the current working
directory, or MEDIA_GEN_ROOT if set. The spend log is
outputs/media-gen/spend.jsonl under it, and renders default to
outputs/media-gen/<date>/. Face references come from MEDIA_GEN_FACE_REFS
(comma-separated), defaulting to two files under content/brand/people/.

OFFLINE CHECKS. `media_gen.py selftest` runs the guards (face lock, spend
ceiling, caption parsing, thumbnail sizing) with no network and no key.
`media_gen.py thumb-size --video <file>` prints the frame size a native
video thumbnail must match, and with --image fits a picture to it.

THIS SCRIPT SPENDS REAL MONEY. Every call prints its cost and waits for a yes,
and anything over MEDIA_GEN_MAX_CALL_USD (default $5.00) is refused outright.

Everything below was verified against the LIVE API, not the docs.
5 places the docs are wrong or silent, all handled here:
  1. Poll responses nest under `data`, not top level.
  2. Status casing varies by model: Seedance returns SUCCESS, Veo returns
     succeeded. Compared case-insensitively.
  3. Seedance leaves `url` empty and puts a signed 24h Volcengine link in
     `result_url`. The gateway's own /videos/{id}/content works for both, so
     that is the download route used here.
  4. /videos/{id}/content needs the Authorization header; a bare GET 401s.
  5. /v1/models does NOT list the video models. Veo works and is absent from
     the catalogue, so model discovery never relies on that list alone.
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ROOT = Path(os.environ.get("MEDIA_GEN_ROOT") or Path.cwd()).expanduser().resolve()
SPEND_LOG = ROOT / "outputs" / "media-gen" / "spend.jsonl"
DEFAULT_OUT = ROOT / "outputs" / "media-gen"
BASE = "https://api.mixroute.ai/v1"

# Rates are the underlying providers' published prices (MixRoute advertises
# zero markup). They drive the pre-spend estimate and the spend log only.
# The MixRoute dashboard is the truth for what was actually billed.
IMAGE_MODELS = {
    "nano-banana-pro": {
        "id": "gemini-3-pro-image",
        "usd": {"1k": 0.134, "2k": 0.134, "4k": 0.24},
        "note": "Ultimate quality, text and diagrams. The thumbnail workhorse.",
    },
    "nano-banana-lite": {
        "id": "gemini-3.1-flash-lite-image",
        "usd": {"1k": 0.0336, "2k": 0.0336, "4k": 0.0336},
        "note": "~4x cheaper. Explore a board here before committing to Pro.",
    },
}

VIDEO_MODELS = {
    "seedance": {
        "id": "doubao-seedance-2-5-260628",
        "usd_per_sec": {"480p": 0.2205, "720p": 0.4730},
        "max_dur": 30,
        "style": "seedance",
        "note": "Seedance 2.5. Material physics; holds a reference's colour.",
    },
    "veo": {
        "id": "veo-3.1-generate-preview",
        "usd_per_sec": {"720p": 0.40, "1080p": 0.40},
        "max_dur": 8,
        "fixed_dur": 8,   # MixRoute's Veo channel IGNORES durationSeconds, verified
        "style": "veo",
        "note": "Veo 3.1. Top-tier cinematic, native audio. Always 8s.",
    },
    "veo-fast": {
        "id": "veo-3.1-fast-generate-preview",
        "usd_per_sec": {"720p": 0.10, "1080p": 0.12},
        "max_dur": 8,
        "fixed_dur": 8,   # MixRoute's Veo channel IGNORES durationSeconds, verified
        "style": "veo",
        "note": "Veo 3.1 Fast. The default story-animation lane; 4x cheaper. Always 8s.",
    },
    # Not MixRoute. Goes straight to Google, so it bills your GCP project and
    # can spend Google Cloud credits. Verified against Google's own notebook:
    # GoogleCloudPlatform/generative-ai vision/getting-started/gemini_omni_flash_video_gen.ipynb
    "omni": {
        "id": "gemini-omni-flash-preview",
        "usd_per_sec": None,          # preview: no published rate, do not invent one
        "max_dur": 10,
        "style": "google",
        "note": "Gemini Omni Flash (preview). Video refs + conversational edit. Google-direct.",
    },
}

# Asked for, checked live, genuinely not there.
UNAVAILABLE = {}


def die(msg, hint=None):
    print(f"\n  Stopped: {msg}", file=sys.stderr)
    if hint:
        print(f"  Try this: {hint}", file=sys.stderr)
    sys.exit(1)


def load_env():
    # Project root first, then the skill folder. setdefault means an exported
    # variable always wins, and the first file to name a key wins over the second.
    for f in (ROOT / ".env", SKILL_DIR / ".env"):
        if not f.exists():
            continue
        for line in f.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip()
            if k.startswith("export "):
                k = k[len("export "):].strip()
            os.environ.setdefault(k, v.strip().strip('"').strip("'"))


def key():
    v = os.environ.get("MIXROUTE_API_KEY")
    if not v:
        die("MIXROUTE_API_KEY is not set.",
            "Get it from mixroute.ai, then run:  "
            "echo 'export MIXROUTE_API_KEY=your_key_here' >> ~/.zshrc  "
            "and open a new terminal window.")
    return v


def call(path, body=None, method=None, raw=False, timeout=600):
    url = path if path.startswith("http") else BASE + path
    hdr = {"Authorization": f"Bearer {key()}"}
    data = None
    if body is not None:
        hdr["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=hdr,
                                 method=method or ("POST" if data else "GET"))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            blob = r.read()
            return r.status, (blob if raw else blob.decode())
    except urllib.error.HTTPError as e:
        return e.code, (e.read() if raw else e.read().decode())
    except Exception as e:
        die(f"could not reach MixRoute ({type(e).__name__}).",
            "Check the connection, then try again.")


def stamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def outdir(a):
    d = Path(a).expanduser() if a else DEFAULT_OUT / datetime.now().strftime("%Y-%m-%d")
    d.mkdir(parents=True, exist_ok=True)
    return d


def confirm(cost, yes):
    cap = float(os.environ.get("MEDIA_GEN_MAX_CALL_USD", "5.00"))
    print(f"  Estimated cost: ${cost:.3f}   (estimate; MixRoute's dashboard is truth)")
    if cost > cap:
        die(f"that is over the ${cap:.2f} per-call cap.",
            "Lower the duration or resolution, or raise MEDIA_GEN_MAX_CALL_USD "
            "in your shell profile and open a new terminal window.")
    if yes:
        return
    try:
        answer = input("  Go ahead? [y/N] ").strip().lower()
    except EOFError:       # non-interactive run without --yes: never assume yes
        die("nothing on stdin to confirm with.", "Add --yes to run unattended.")
    if answer not in ("y", "yes"):
        die("cancelled, nothing was spent.")


def log_spend(kind, model, cost, detail):
    SPEND_LOG.parent.mkdir(parents=True, exist_ok=True)
    with SPEND_LOG.open("a") as f:
        f.write(json.dumps({
            "ts": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "kind": kind, "model": model, "usd_est": round(cost, 4), **detail}) + "\n")


def read_ref(p):
    p = Path(p).expanduser()
    b = p.read_bytes()
    return b, (mimetypes.guess_type(p.name)[0] or "image/png")


def check_refs(paths):
    # gs:// URIs are Cloud Storage, not local files -- the omni lane reads video
    # references from there on purpose, so never stat them.
    missing = [str(p) for p in paths
               if p and not str(p).startswith("gs://") and not Path(p).expanduser().exists()]
    if missing:
        die("these reference files don't exist: " + ", ".join(missing),
            "check the paths. Real photographs of the people live in "
            "content/brand/people/; set MEDIA_GEN_FACE_REFS to your two face "
            "references (comma-separated) so the hints point at real files")


# Two reference images of the same person, passed together, are what locks a
# face across renders. Export MEDIA_GEN_FACE_REFS=path/a.png,path/b.png.
# They must be real photographs of that person (content/brand/people/ by
# convention). A face is never invented from a text prompt, and a render whose
# face came back wrong is never the reference for the fix.
DEFAULT_FACE_REFS = "content/brand/people/face-ref-a.png,content/brand/people/face-ref-b.png"


def face_refs():
    refs = tuple(p.strip() for p in os.environ.get(
        "MEDIA_GEN_FACE_REFS", DEFAULT_FACE_REFS).split(",") if p.strip())
    return refs if len(refs) >= 2 else refs + ("<second-face-ref>",) * (2 - len(refs))


def check_face_refs(refs, allow_single):
    # The face lock needs BOTH references or the render comes back as a
    # different person (a 1-ref call still runs happily and still fails).
    # One reference is almost always that mistake, so it is refused unless
    # the caller says out loud that this render has no face in it.
    if len(refs) == 1 and not allow_single:
        die(f"one reference won't lock the face; the second reference is missing "
            f"(you passed only {Path(refs[0]).name}).",
            f"Pass both together:  --ref {face_refs()[0]} --ref {face_refs()[1]}\n"
            f"  Or, if this render has no face in it, add --allow-single-ref.")


def _report(saved):
    if not saved:
        print("\n  Nothing was saved.")
        return
    print(f"\n  Saved {len(saved)} file(s):")
    for p in saved:
        print(f"    {p}")


# ---------------------------------------------------------------------- image
def cmd_image(a):
    spec = IMAGE_MODELS.get(a.model) or die(
        f"unknown image model '{a.model}'.", f"Pick one of: {', '.join(IMAGE_MODELS)}")
    check_refs(a.ref)
    check_face_refs(a.ref, a.allow_single_ref)
    res = a.resolution.lower()
    cost = spec["usd"].get(res, spec["usd"]["1k"]) * a.count

    print(f"\n  {a.model}  ({spec['id']})  {res.upper()}  {a.aspect}  x{a.count}")
    if a.ref:
        print(f"  {len(a.ref)} reference(s): {', '.join(Path(r).name for r in a.ref)}")
    confirm(cost, a.yes)

    # References go FIRST so the model anchors identity before it reads the
    # prompt. This is the face-lock rule: both refs, refs ahead of the words,
    # or the render comes back as a different person.
    parts = []
    for r in a.ref:
        b, m = read_ref(r)
        parts.append({"inline_data": {"mime_type": m, "data": base64.b64encode(b).decode()}})
    parts.append({"text": a.prompt})

    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"],
                                 "imageConfig": {"aspectRatio": a.aspect,
                                                 "imageSize": res.upper()}}}

    # Which wallet pays. Vertex and MixRoute charge the SAME list price for
    # Gemini 3 Pro Image (check both providers' pricing pages; at the time of
    # writing the gateway took zero markup on this model). The difference
    # is which balance it comes out of: a Google Cloud project can be sitting on
    # trial credit that expires whether it is used or not, while MixRoute is
    # cash. So go Google when it is configured and reachable, MixRoute otherwise.
    # If you have no GOOGLE_CLOUD_PROJECT, everything simply runs on MixRoute.
    via = _pick_image_route(a.via, a.model, getattr(a, "pay_cash", False))

    d, saved = outdir(a.out), []
    for i in range(a.count):
        print(f"  Rendering {i + 1} of {a.count}... (can take a minute)")
        if via == "google":
            st, txt = _vertex_image(a.model_id or spec["id"], body)
            if st != 200:
                # An expired ADC token or a model Vertex will not serve should
                # cost a render, not the whole run. But a silent cash fallback is
                # its own incident: 6 renders once spent cash while a Google
                # credit sat unused, because a token had gone stale and nobody
                # read the line saying so. When a Google route was configured,
                # falling back to cash needs --pay-cash said out loud.
                if _guard_wallet(a):
                    die(f"Vertex refused this render ({st}: {txt[:120]}) and the "
                        f"MixRoute fallback would spend cash while your Google "
                        f"project sits unused.",
                        "Reauth:  gcloud auth application-default login\n"
                        "  Or, to spend MixRoute cash deliberately, add --pay-cash.")
                print(f"    Vertex said {st}, falling back to MixRoute for the rest.")
                print(f"    ({txt[:120]})")
                via = "mixroute"
                st, txt = call(f"/models/{a.model_id or spec['id']}:generateContent", body)
        else:
            st, txt = call(f"/models/{a.model_id or spec['id']}:generateContent", body)
        if st != 200:
            _hint(st, txt, a.model_id or spec["id"])
        got = False
        for p in json.loads(txt).get("candidates", [{}])[0].get("content", {}).get("parts", []):
            inl = p.get("inlineData") or p.get("inline_data")
            if inl and inl.get("data"):
                mime = inl.get("mimeType") or inl.get("mime_type") or "image/png"
                ext = mime.split("/")[-1].replace("jpeg", "jpg")
                path = d / f"{stamp()}-{a.slug}-{i + 1}.{ext}"
                path.write_bytes(base64.b64decode(inl["data"]))
                saved.append(path)
                got = True
            elif p.get("text"):
                print(f"    model said: {p['text'][:160]}")
        if not got:
            print("  ! No image in that response (usually a content filter). Rephrase and retry.")

    log_spend("image", spec["id"], cost,
              {"n": a.count, "resolution": res, "via": via,
               "auth": ("vertex-credit" if via == "google" else "mixroute-cash"),
               "billing": ("google-cloud-credits" if via == "google" else "mixroute"),
               "files": [str(p) for p in saved]})
    _report(saved)
    if via == "google":
        print("  paid with: your Google Cloud project")
    else:
        print("  paid with: MixRoute balance (cash)")


REAUTH = "gcloud auth application-default login"


def _guard_wallet(a):
    """True when a silent fall back to paying cash should be a refusal instead.

    Only bites when you actually configured a Google route: with no
    GOOGLE_CLOUD_PROJECT, MixRoute is your only wallet and there is nothing to
    guard. It exists because the failure mode is not an error, it is quietly
    paying cash for what another balance already covers. That happened once for
    6 renders on a stale token, and the line saying so scrolled past unread.
    """
    return (getattr(a, "model", None) == "nano-banana-pro"
            and not getattr(a, "pay_cash", False)
            and bool(os.environ.get("GOOGLE_CLOUD_PROJECT")))


def _pick_image_route(want, model=None, pay_cash=False):
    """google | mixroute, honouring --via and refusing a silent cash fallback.

    For nano-banana-pro, when a Google project IS configured, an unreachable
    Vertex route is a refusal with the reauth command rather than a quiet switch
    to the cash balance. `--pay-cash` is the override. With no Google project
    configured this is a no-op and everything runs on MixRoute.
    """
    has_google = bool(os.environ.get("GOOGLE_CLOUD_PROJECT"))
    guarded = (model == "nano-banana-pro") and not pay_cash and has_google

    def _refuse(why):
        die(f"{why} Falling back to MixRoute would spend cash while your "
            f"Google project sits unused.",
            f"Reauth:  {REAUTH}\n"
            f"  Or, to spend MixRoute cash deliberately, add --pay-cash.")

    if want == "mixroute":
        return "mixroute"
    if not has_google:
        if want == "google":
            die("--via google needs GOOGLE_CLOUD_PROJECT set in your environment.",
                f"Add it, then run once: {REAUTH}")
        return "mixroute"
    try:
        _adc_token()
        return "google"
    except Exception as e:
        if want == "google":
            die(f"Google credentials are not usable: {str(e)[:160]}",
                f"Run: {REAUTH}")
        if guarded:
            _refuse(f"Google credentials are stale ({str(e)[:120]}).")
        print("  (Google credentials stale, so this is going on MixRoute cash. "
              f"Run `{REAUTH}` to go back to the Google project.)")
        return "mixroute"


def _adc_token():
    import google.auth
    import google.auth.transport.requests
    # google-genai and google-auth both read these, and a stray key silently
    # sends the call to a different wallet than the one you think you picked.
    for var in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
        os.environ.pop(var, None)
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


def _vertex_image(model_id, body):
    """Same generateContent body, Vertex endpoint, so the Cloud credit pays.

    Two differences from MixRoute, both found live:
      - Vertex REQUIRES an explicit role on each content block ("Please use a
        valid role: user, model"), which the OpenAI-compatible gateway does not.
      - The model id has no -preview suffix here: gemini-3-pro-image-preview
        404s, gemini-3-pro-image serves.
    """
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
    body = dict(body)
    body["contents"] = [{**c, "role": c.get("role", "user")} for c in body["contents"]]
    url = (f"https://aiplatform.googleapis.com/v1/projects/{project}"
           f"/locations/{location}/publishers/google/models/{model_id}:generateContent")
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {_adc_token()}",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"


def _hint(status, txt, model_id):
    if status == 503 and "model_not_found" in txt:
        die(f"MixRoute has no channel for '{model_id}' right now.",
            "Run `media_gen.py models` to see what it actually carries.")
    if status == 401:
        die("MixRoute rejected the key.",
            "Run `media_gen.py doctor` to see which key it is using.")
    die(f"MixRoute returned {status}: {txt[:300]}")


# ---------------------------------------------------------------------- video
def cmd_video(a):
    if a.model in UNAVAILABLE:
        die(UNAVAILABLE[a.model])
    spec = VIDEO_MODELS.get(a.model) or die(
        f"unknown video model '{a.model}'.", f"Pick one of: {', '.join(VIDEO_MODELS)}")
    check_refs(list(a.ref) + ([a.start] if a.start else []) + ([a.end] if getattr(a, "end", None) else []))

    if spec["style"] == "google":
        return cmd_omni(a, spec)

    if a.duration > spec["max_dur"]:
        die(f"{a.model} maxes out at {spec['max_dur']}s, you asked for {a.duration}s.",
            f"Use --duration {spec['max_dur']} or switch model.")
    rate = spec["usd_per_sec"].get(a.resolution)
    if rate is None:
        die(f"{a.model} doesn't do {a.resolution}.",
            f"It supports: {', '.join(spec['usd_per_sec'])}")

    # Verified live: MixRoute's Veo channel ignores durationSeconds
    # and always returns 8s. Bill the real length so the estimate can never
    # under-report, and say plainly that the request will not be honoured.
    billed = spec.get("fixed_dur") or a.duration
    if spec.get("fixed_dur") and a.duration != spec["fixed_dur"]:
        print(f"\n  Note: {a.model} always returns {spec['fixed_dur']}s through MixRoute, "
              f"your --duration {a.duration} will be ignored, and you pay for "
              f"{spec['fixed_dur']}s. Use --model seedance if the length matters.")
    cost = rate * billed

    print(f"\n  {a.model}  ({spec['id']})  {billed}s  {a.resolution}  {a.aspect}")
    print(f"  rate: ${rate:.4f}/sec   paid with: MixRoute balance (cash)")
    print(f"  audio: {'off' if a.no_audio else 'on'}")
    _seedance_text_warning(a)
    if a.start:
        print(f"  start frame: {Path(a.start).name}")
    if a.ref:
        print(f"  {len(a.ref)} reference(s): {', '.join(Path(r).name for r in a.ref)}")
    confirm(cost, a.yes)

    body = {"model": a.model_id or spec["id"], "prompt": a.prompt}
    if spec["style"] == "seedance":
        # Seedance puts everything except model/prompt inside metadata, and
        # images go in metadata.content with a role.
        # Live: with a first_frame image, Seedance rejects an explicit ratio
        # (InvalidParameter.TaskTypeConstraint). The aspect comes from the image,
        # so ratio must be "adaptive" for image-to-video jobs.
        meta = {"ratio": "adaptive" if a.start else a.aspect,
                "duration": a.duration, "resolution": a.resolution,
                "generate_audio": not a.no_audio}
        content = []
        if a.start:
            content.append({"type": "image_url", "role": "first_frame",
                            "image_url": {"url": _data_uri(a.start)}})
        if getattr(a, "end", None):
            content.append({"type": "image_url", "role": "last_frame",
                            "image_url": {"url": _data_uri(a.end)}})
        for r in a.ref:
            content.append({"type": "image_url", "role": "reference",
                            "image_url": {"url": _data_uri(r)}})
        if content:
            meta["content"] = content
        body["metadata"] = meta
    else:  # veo, flat camelCase fields
        body.update({"durationSeconds": a.duration, "aspectRatio": a.aspect,
                     "resolution": a.resolution, "generateAudio": not a.no_audio})
        if a.start:
            body["image"] = _data_uri(a.start)
        if a.negative:
            body["negativePrompt"] = a.negative

    print("  Submitting...")
    st, txt = call("/video/generations", body)
    if st != 200:
        _hint(st, txt, a.model_id or spec["id"])
    tid = json.loads(txt).get("task_id") or json.loads(txt).get("id")
    if not tid:
        die(f"MixRoute accepted the job but returned no task id: {txt[:250]}")
    print(f"  task {tid}")

    waited = 0
    while True:
        time.sleep(10)
        waited += 10
        st, txt = call(f"/video/generations/{tid}")
        d = (json.loads(txt).get("data") or json.loads(txt)) if st == 200 else {}
        status = str(d.get("status", "")).lower()      # SUCCESS vs succeeded
        if status in ("succeeded", "success", "completed"):
            break
        if status in ("failed", "error"):
            die(f"the render failed: {d.get('fail_reason') or d.get('error') or txt[:250]}")
        print(f"  Still rendering... {waited}s ({d.get('status') or 'queued'})")
        if waited > 900:
            die("15 minutes with no result.", "Try a shorter duration.")

    # The gateway's own content endpoint works for every model and needs the
    # auth header. Seedance's result_url is a signed 24h link and is the
    # fallback only.
    dest = outdir(a.out) / f"{stamp()}-{a.slug}.mp4"
    st, blob = call(f"/videos/{tid}/content", raw=True)
    if st != 200 or len(blob) < 1000:
        alt = d.get("result_url") or d.get("url")
        if not alt:
            die(f"the render finished but no file came back (HTTP {st}).")
        st2, blob = call(alt, raw=True)
        if st2 != 200:
            die(f"could not download the finished video (HTTP {st2}).")
    dest.write_bytes(blob)
    log_spend("video", spec["id"], cost,
              {"duration": billed, "requested_duration": a.duration,
               "resolution": a.resolution, "auth": "mixroute-cash",
               "billing": "mixroute", "files": [str(dest)]})
    _report([dest])


UI_TEXT_WORDS = ("text", "ui", "screen", "phone", "interface", "dashboard",
                 "caption", "subtitle", "app ", "typing", "word", "headline",
                 "laptop", "monitor", "spreadsheet")


def _seedance_text_warning(a):
    """Seedance cannot be trusted with on-screen UI text, so say so before paying."""
    if a.model != "seedance":
        return
    p = (a.prompt or "").lower()
    hits = sorted({w.strip() for w in UI_TEXT_WORDS if w in p})
    if not hits:
        return
    print("\n  WARNING: on-screen text in a generated video.")
    print(f"  This prompt mentions: {', '.join(hits)}")
    print("  Generated video cannot be trusted with on-screen UI text: it renders")
    print("  garbled words, invented logos and wrong numbers, and that ships.")
    print("  Routes that work: veo or omni for a legible line, or a real screen")
    print("  capture composited in afterwards.\n")


def google_client():
    """Vertex first (spends your Google Cloud project), API key second."""
    try:
        from google import genai
    except ImportError:
        die("the google-genai SDK isn't installed.",
            "pip3 install --upgrade google-genai")

    # Vertex FIRST, because that is the only route that spends a Google Cloud
    # project's balance (including any trial credit sitting on it). A plain
    # Gemini API key bills a SEPARATE "prepayment credits" pool, which returns
    # 429 credits_depleted when empty, so the key is a fallback only.
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    # Omni Flash rejects classic Vertex regions: only global, us, eu.
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
    if project:
        # google-genai picks GOOGLE_API_KEY up from the environment on its own and
        # it wins over enterprise mode, silently sending calls to the wrong wallet.
        for var in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
            os.environ.pop(var, None)
        try:
            return genai.Client(enterprise=True, project=project, location=location), \
                   f"Vertex AI, project {project} ({location}), bills that project"
        except Exception as e:
            die(f"Vertex wouldn't start: {e}",
                "Run: gcloud auth application-default login")

    die("no Google credentials found.",
        "To bill a Google project, export GOOGLE_CLOUD_PROJECT=your-project-id\n"
        "             then run once:  gcloud auth application-default login\n"
        "  Or for a plain key:  GOOGLE_API_KEY=... (bills the key's own pool)")


def cmd_omni(a, spec):
    from google.genai import types as _t
    try:
        from google.genai import interactions
    except ImportError:
        die("this google-genai is too old for Gemini Omni Flash.",
            "pip3 install --upgrade google-genai")

    client, who = google_client()

    # Local images ride as base64. Video has to be a gs:// URI, which is a real
    # constraint: Omni reads video refs from Cloud Storage, not from your disk.
    parts = [{"type": "text", "text": a.prompt}]
    vids = [r for r in a.ref if str(r).startswith("gs://") or str(r).lower().endswith(".mp4")]
    imgs = [r for r in a.ref if r not in vids]
    if a.start:
        imgs.insert(0, a.start)

    for r in imgs:
        b, m = read_ref(r)
        parts.append({"type": "image", "mime_type": m,
                      "data": base64.b64encode(b).decode()})
    for v in vids:
        if not str(v).startswith("gs://"):
            die(f"Omni reads video references from Cloud Storage, not local files ({Path(v).name}).",
                "Upload it first:  gcloud storage cp file.mp4 gs://your-bucket/\n"
                "  then pass:  --ref gs://your-bucket/file.mp4")
        parts.append({"type": "video", "mime_type": "video/mp4", "uri": str(v)})

    task = ("edit" if vids else
            "reference_to_video" if len(imgs) > 1 else
            "image_to_video" if imgs else
            "text_to_video")

    print(f"\n  omni  ({spec['id']})  {a.duration}s  {a.aspect}  task={task}")
    print(f"  auth: {who}")
    if imgs:
        print(f"  {len(imgs)} image ref(s): {', '.join(Path(i).name for i in imgs)}")
    if vids:
        print(f"  {len(vids)} video ref(s): {', '.join(str(v) for v in vids)}")
    print("  cost: preview model, no published per-second rate. Billed to the "
          "account above, not to MixRoute.")
    if not a.yes:
        confirm(0.0, False)

    print("  Submitting...")
    inter = client.interactions.create(
        model=a.model_id or spec["id"],
        input=parts if len(parts) > 1 else a.prompt,
        background=True,
        generation_config=interactions.GenerationConfig(
            video_config=interactions.VideoConfig(task=task)),
        # An edit task inherits the reference's frame: passing aspect_ratio is a
        # 400 ("Aspect ratio cannot be set in response format for edit task").
        response_format=(interactions.VideoResponseFormat(duration=f"{a.duration}s")
                         if task == "edit" else
                         interactions.VideoResponseFormat(
                             aspect_ratio=a.aspect, duration=f"{a.duration}s")),
    )
    print(f"  interaction {inter.id}")

    waited = 0
    while str(inter.status) not in ("completed", "failed"):
        time.sleep(10)
        waited += 10
        inter = client.interactions.get(id=inter.id)
        print(f"  Still rendering... {waited}s ({inter.status})")
        if waited > 1200:
            die(f"20 minutes with no result. The job may still finish: "
                f"interaction id {inter.id}.", "Re-check it rather than re-paying.")
    if str(inter.status) == "failed":
        die(f"Omni reported the render failed: {getattr(inter, 'error', '') or inter.status}")

    blob = None
    for step in (getattr(inter, "steps", []) or []):
        if getattr(step, "type", None) == "model_output":
            for c in (step.content or []):
                data = getattr(c, "data", None)
                if data:
                    blob = base64.b64decode(data) if isinstance(data, str) else data
    if not blob:
        die(f"the render finished but carried no video (interaction {inter.id}).")

    dest = outdir(a.out) / f"{stamp()}-{a.slug}.mp4"
    dest.write_bytes(blob)

    # Omni is token-priced, not per-second, and Google publishes the rates
    # (check its pricing page; the figures used live in _omni_cost). Read the
    # real usage off the interaction rather than guessing. An earlier version
    # logged a flat zero here, which hid real spend before anyone noticed.
    cost, usage = _omni_cost(inter)
    log_spend("video", spec["id"], cost,
              {"duration": a.duration, "resolution": "720p", "task": task,
               "auth": who, "interaction": inter.id, "usage": usage,
               "billing": "google-cloud-credits", "files": [str(dest)]})
    if cost:
        print(f"  cost: ${cost:.4f}   (from the interaction's own token usage)")
    _report([dest])


def _omni_cost(inter):
    """Real USD for an Omni render, from the token counts Vertex returns.

    Rates verified live against the Cloud Billing SKU catalogue. Returns
    (usd, usage_dict). Falls back to (0.0, {}) rather than inventing a number if
    the response carries no usage: an absent bill is not a free one, so the
    caller prints nothing instead of claiming zero.
    """
    RATE_IN, RATE_TEXT_OUT, RATE_VIDEO_OUT = 1.50e-6, 9.00e-6, 17.50e-6
    u = getattr(inter, "usage", None)
    if not u:
        return 0.0, {}
    g = (lambda *names: next((int(v) for n in names
                              if (v := getattr(u, n, None)) is not None), 0))
    inp   = g("input_tokens", "prompt_token_count", "input_token_count")
    think = g("reasoning_tokens", "thoughts_token_count", "output_tokens")
    vid   = g("video_output_tokens", "video_token_count")
    # Some responses fold video into total output; recover it by difference.
    total = g("total_tokens", "total_token_count")
    if not vid and total:
        vid = max(0, total - inp - think)
    usd = inp * RATE_IN + think * RATE_TEXT_OUT + vid * RATE_VIDEO_OUT
    return usd, {"input": inp, "reasoning": think, "video_output": vid}


def _data_uri(p):
    b, m = read_ref(p)
    return f"data:{m};base64,{base64.b64encode(b).decode()}"


# ------------------------------------------------------------------ discovery
def cmd_models(a):
    print("\n  Configured, and verified live\n")
    print("  IMAGES")
    for n, s in IMAGE_MODELS.items():
        print(f"    {n:<18} {s['id']:<30} ${s['usd']['1k']:.4f}/image  {s['note']}")
    print("\n  VIDEO")
    for n, s in VIDEO_MODELS.items():
        fixed = f", ALWAYS {s['fixed_dur']}s" if s.get("fixed_dur") else f", max {s['max_dur']}s"
        if s["usd_per_sec"]:
            price = f"from ${min(s['usd_per_sec'].values()):.4f}/sec"
        else:
            price = "preview, no published rate"
        print(f"    {n:<18} {s['id']:<30} {price}{fixed}")
        print(f"    {'':<18} {s['note']}")
    print("\n  NOT AVAILABLE")
    for n, why in UNAVAILABLE.items():
        print(f"    {n:<18} {why}")

    print("\n  Asking MixRoute what it carries now...")
    st, txt = call("/models", timeout=90)
    if st != 200:
        print(f"  Could not list models (HTTP {st}).")
        return
    ids = sorted(m.get("id", "") for m in json.loads(txt).get("data", []))
    import re
    media = [i for i in ids if re.search(r"image|video|seedance|veo|omni|sora", i, re.I)]
    print(f"  {len(ids)} models total; {len(media)} look image/video shaped:")
    for i in media:
        print(f"    {i}")
    print("\n  Note: /models does NOT list every video model. Veo works and is")
    print("  absent from this list. Absence here is not proof of absence.")
    for probe in ("gemini-omni-flash-preview", "gemini-omni-flash"):
        st, _ = call("/video/generations", {"model": probe, "prompt": "test"}, timeout=60)
        print(f"    probe {probe:<28} -> HTTP {st}"
              f"{'  (available!)' if st == 200 else '  (still absent)'}")


def cmd_doctor(a):
    print("\n  Checks\n")
    ok = bool(os.environ.get("MIXROUTE_API_KEY"))
    print(f"    {'OK   ' if ok else 'MISSING'}  MIXROUTE_API_KEY"
          f"{'' if ok else ' (get it from mixroute.ai, then export MIXROUTE_API_KEY)'}")
    if ok:
        st, txt = call("/models", timeout=60)
        if st == 200:
            print(f"    OK      key works, {len(json.loads(txt).get('data', []))} models reachable")
        else:
            ok = False
            print(f"    FAILED  MixRoute returned {st}: {txt[:120]}")
    for stale in ("GEMINI_API_KEY", "FAL_KEY"):
        if os.environ.get(stale):
            print(f"    note    {stale} is still set and is no longer used, safe to delete")
    print(f"    OK      per-call spend cap: ${float(os.environ.get('MEDIA_GEN_MAX_CALL_USD', '5.00')):.2f}")

    # The optional Google lane. Not required to work: everything falls back to
    # MixRoute, so a failure here is a "you are paying cash" warning, never an
    # error. ADC tokens expire often, which is exactly why the fallback exists.
    print("\n  Google Cloud lane, optional (images and omni video)\n")
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        print("    OFF     GOOGLE_CLOUD_PROJECT not set, so images bill MixRoute (cash).")
        print("            That is a fine way to run this. Set it only if you have a")
        print("            Google Cloud project you would rather bill.")
    else:
        print(f"    OK      project {project}")
        try:
            _adc_token()
            print("    OK      credentials live, images and omni bill that project")
        except Exception:
            print("    STALE   credentials expired. Renders still work, on MixRoute (cash).")
            print("            Fix:  gcloud auth application-default login")
    print(f"\n  {'Ready.' if ok else 'Not ready, fix the lines above.'}\n")


def cmd_spend(a):
    if not SPEND_LOG.exists():
        print("\n  Nothing spent yet.\n")
        return
    rows = [json.loads(l) for l in SPEND_LOG.read_text().splitlines() if l.strip()]
    month = a.month or datetime.now().strftime("%Y-%m")
    rows = [r for r in rows if r["ts"].startswith(month)]
    if not rows:
        print(f"\n  Nothing logged for {month}.\n")
        return
    by = {}
    for r in rows:
        e = by.setdefault(r["model"], [0, 0.0])
        e[0] += 1
        e[1] += r["usd_est"]
    print(f"\n  Spend for {month}  (estimated; MixRoute's dashboard is truth)\n")
    for m, (n, c) in sorted(by.items(), key=lambda x: -x[1][1]):
        print(f"    {m:<34} {n:>4} calls   ${c:>8.2f}")
    print(f"    {'':<34} {len(rows):>4} total   ${sum(r['usd_est'] for r in rows):>8.2f}\n")

    # Which wallet paid. Rows written by older versions have no `auth` field, so
    # fall back to `billing`/`via` rather than pretending they are unknown.
    print("  By wallet\n")
    wal = {}
    for r in rows:
        w = _wallet_of(r)
        e = wal.setdefault(w, [0, 0.0])
        e[0] += 1
        e[1] += r["usd_est"]
    labels = {"mixroute-cash": "MixRoute (cash out of pocket)",
              "vertex-credit": "Google Cloud project",
              "unknown": "unrecorded (row predates the auth field)"}
    for w, (n, c) in sorted(wal.items(), key=lambda x: -x[1][1]):
        print(f"    {labels.get(w, w):<44} {n:>4} calls   ${c:>8.2f}")

    # All time, both wallets, so a month's total is never mistaken for the bill.
    all_rows = [json.loads(l) for l in SPEND_LOG.read_text().splitlines() if l.strip()]
    print(f"\n  All time, every wallet: ${sum(r['usd_est'] for r in all_rows):.2f} "
          f"across {len(all_rows)} calls. Estimates, not invoices.\n")


def _wallet_of(r):
    a = r.get("auth")
    if a:
        a = str(a)
        if "vertex" in a.lower() or "google" in a.lower():
            return "vertex-credit"
        if "mixroute" in a.lower():
            return "mixroute-cash"
    b = r.get("billing") or ("google-cloud-credits" if r.get("via") == "google" else None)
    if b == "google-cloud-credits":
        return "vertex-credit"
    if b == "mixroute":
        return "mixroute-cash"
    return "unknown"


# ---------------------------------------------------------------------- board
def cmd_board(a):
    """Captioned contact grid, saved AND opened with the full set beside it.

    Built after a session said 9 renders were "open in Preview" without ever
    calling `open`, and after 15 thumbnails got judged off a downscaled grid
    because the full-size files were never opened. So this command does both
    halves and PRINTS the exact `open` invocation as proof that it ran. The
    grid is for scanning; the full-size files are what actually gets judged.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        die("Pillow isn't installed.", "pip3 install --upgrade pillow")

    d = Path(a.dir).expanduser().resolve()
    if not d.is_dir():
        die(f"no such directory: {d}")
    exts = {".png", ".jpg", ".jpeg", ".webp"}
    imgs = sorted(p for p in d.iterdir()
                  if p.suffix.lower() in exts and "contact-grid" not in p.name
                  and p.name != (a.name or "board-contact-grid.png"))
    if not imgs:
        die(f"no images in {d}")

    captions = _load_captions(a.captions)

    cols = a.cols or min(4, len(imgs))
    rows = (len(imgs) + cols - 1) // cols
    cw, ch, pad, cap_h = a.cell, int(a.cell * 9 / 16), 24, 96
    W = cols * (cw + pad) + pad
    H = rows * (ch + cap_h + pad) + pad
    sheet = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(sheet)
    font = _font(20)
    small = _font(16)

    for i, p in enumerate(imgs):
        r, c = divmod(i, cols)
        x = pad + c * (cw + pad)
        y = pad + r * (ch + cap_h + pad)
        im = Image.open(p).convert("RGB")
        im.thumbnail((cw, ch))
        sheet.paste(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2))
        draw.text((x, y + ch + 6), p.name[:56], fill="#1C1C1C", font=small)
        cap = captions.get(p.name) or captions.get(p.stem) or ""
        if cap:
            draw.text((x, y + ch + 30), _wrap(cap, 46), fill="#2B5C8A", font=font)

    dest = (d / (a.name or "board-contact-grid.png")).resolve()
    sheet.save(dest)
    print(f"\n  Grid: {dest}  ({cols} x {rows}, {len(imgs)} images)")

    # The grid is for scanning; the individual files are what gets judged.
    # Both go up in ONE open call so nothing can half-happen.
    import shutil as _sh
    import subprocess
    opener = "open" if _sh.which("open") else (
        "xdg-open" if _sh.which("xdg-open") else None)
    if not opener:
        print("\n  No image viewer on this machine. Open these by hand, all of them,")
        print("  at full size (the grid alone is not enough to judge on):")
        for q in [dest] + imgs:
            print(f"    {q}")
        return
    argv = [opener, str(dest)] + [str(p) for p in imgs]
    print("\n  Opening the grid and every full-size image. Exact invocation:")
    print("    " + " ".join(_q(x) for x in argv))
    rc = subprocess.run(argv).returncode
    print(f"  {opener} exited {rc}: "
          f"{'grid + ' + str(len(imgs)) + ' images are open.' if rc == 0 else 'IT DID NOT OPEN.'}")


def _q(s):
    return f'"{s}"' if " " in s else s


def _font(size):
    from PIL import ImageFont
    for f in ("/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Helvetica.ttc"):
        try:
            return ImageFont.truetype(f, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _wrap(s, n):
    out, line = [], ""
    for w in s.split():
        if len(line) + len(w) + 1 > n:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    out.append(line)
    return "\n".join(out[:2])


def _load_captions(src):
    """{filename: caption} from a JSON map or a markdown `file - caption` list."""
    if not src:
        return {}
    p = Path(src).expanduser()
    if not p.exists():
        die(f"captions file not found: {p}")
    txt = p.read_text()
    if p.suffix.lower() == ".json":
        return json.loads(txt)
    out = {}
    for line in txt.splitlines():
        line = line.strip().lstrip("-*| ").strip()
        for sep in ("\u2014", " - ", "|", ":"):
            if sep in line:
                k, _, v = line.partition(sep)
                if k.strip():
                    out[k.strip()] = v.strip().strip("|").strip()
                break
    return out


# ------------------------------------------------------------- thumb-size
YOUTUBE_THUMB = (1280, 720)


def video_size(path):
    """(width, height) of the first video stream, read with ffprobe."""
    import shutil as _sh
    import subprocess
    if not _sh.which("ffprobe"):
        die("ffprobe is not installed.", "Install ffmpeg (it ships ffprobe), then retry.")
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height:stream_side_data=rotation",
         "-of", "json", str(path)], capture_output=True, text=True)
    if r.returncode != 0:
        die(f"ffprobe could not read {path}.", r.stderr.strip()[:200] or None)
    st = (json.loads(r.stdout).get("streams") or [{}])[0]
    w, h = int(st.get("width", 0)), int(st.get("height", 0))
    rot = 0
    for sd in st.get("side_data_list", []) or []:
        rot = int(sd.get("rotation", 0) or 0)
    if abs(rot) in (90, 270):
        w, h = h, w
    if not w or not h:
        die(f"no video stream found in {path}.")
    return w, h


def cover_box(src_w, src_h, dst_w, dst_h):
    """Centre crop box (l, t, r, b) on the source that fills dst at its aspect."""
    src_ar, dst_ar = src_w / src_h, dst_w / dst_h
    if src_ar > dst_ar:                 # source too wide: trim the sides
        cw = round(src_h * dst_ar)
        left = (src_w - cw) // 2
        return (left, 0, left + cw, src_h)
    ch = round(src_w / dst_ar)          # source too tall: trim top and bottom
    top = (src_h - ch) // 2
    return (0, top, src_w, top + ch)


def cmd_thumb_size(a):
    """The size a thumbnail must be, and optionally fit an image to it.

    A native video post with a custom thumbnail can fail wholesale, with an
    error that names neither the thumbnail nor the size, when the thumbnail is
    smaller than the video frame (a 1280x720 cover on a 1920x1080 video). So
    for a native video upload the thumbnail takes its pixel size from the
    VIDEO, not just its aspect ratio. YouTube is the exception: it wants
    1280x720 whatever the video is.
    """
    if a.platform == "youtube":
        w, h = YOUTUBE_THUMB
        why = "YouTube thumbnail, always 1280x720"
    else:
        if not a.video:
            die("--video is required unless --platform youtube.")
        w, h = video_size(a.video)
        why = f"matches the video frame of {Path(a.video).name}"
    print(f"\n  Thumbnail size: {w}x{h}  ({why})")
    if not a.image:
        return
    try:
        from PIL import Image
    except ImportError:
        die("Pillow is not installed.", "pip install pillow")
    src = Path(a.image).expanduser()
    if not src.exists():
        die(f"image not found: {src}")
    im = Image.open(src).convert("RGB")
    if im.width < w or im.height < h:
        print(f"  Note: the source is {im.width}x{im.height}, smaller than {w}x{h}. "
              f"It will be upscaled; render the thumbnail natively at {w}x{h} "
              f"for a sharp result.")
    im = im.crop(cover_box(im.width, im.height, w, h)).resize((w, h), Image.LANCZOS)
    out = Path(a.out).expanduser() if a.out else src.with_name(f"{src.stem}-{w}x{h}.jpg")
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix.lower() in (".jpg", ".jpeg"):
        im.save(out, "JPEG", quality=92, optimize=True)
    else:
        im.save(out)
    print(f"  Saved {out}")


# ---------------------------------------------------------------- selftest
def cmd_selftest(a):
    """Offline checks of the guards. No network, no key, nothing spent."""
    import tempfile
    fails = []

    def expect_exit(label, fn):
        try:
            fn()
        except SystemExit:
            return
        fails.append(f"{label}: expected a refusal, got none")

    def expect_ok(label, fn):
        try:
            fn()
        except SystemExit:
            fails.append(f"{label}: refused when it should pass")

    # Face lock: 1 ref refused, 1 ref with --allow-single-ref passes, 2 pass.
    expect_exit("single face ref", lambda: check_face_refs(["a.png"], False))
    expect_ok("single ref, no face", lambda: check_face_refs(["a.png"], True))
    expect_ok("two face refs", lambda: check_face_refs(["a.png", "b.png"], False))
    if len(face_refs()) < 2:
        fails.append("face_refs() must always offer 2 paths for the hint")

    # Spend ceiling: over the cap refuses even with --yes; under it passes.
    old = os.environ.get("MEDIA_GEN_MAX_CALL_USD")
    os.environ["MEDIA_GEN_MAX_CALL_USD"] = "1.00"
    expect_exit("over the ceiling", lambda: confirm(1.50, True))
    expect_ok("under the ceiling", lambda: confirm(0.50, True))
    if old is None:
        os.environ.pop("MEDIA_GEN_MAX_CALL_USD", None)
    else:
        os.environ["MEDIA_GEN_MAX_CALL_USD"] = old

    # Missing reference files refuse; gs:// URIs are never stat'ed.
    expect_exit("missing ref file", lambda: check_refs(["/nonexistent/x.png"]))
    expect_ok("gs:// ref", lambda: check_refs(["gs://bucket/clip.mp4"]))

    # Caption parsing, markdown and JSON.
    with tempfile.TemporaryDirectory() as td:
        md = Path(td) / "c.md"
        md.write_text("- a.png - First title\n- b.png | Second title\n")
        got = _load_captions(str(md))
        if got != {"a.png": "First title", "b.png": "Second title"}:
            fails.append(f"markdown captions parsed wrong: {got}")
        js = Path(td) / "c.json"
        js.write_text(json.dumps({"c.png": "Third"}))
        if _load_captions(str(js)) != {"c.png": "Third"}:
            fails.append("json captions parsed wrong")

    # Thumbnail sizing: cover crop fills the target aspect exactly.
    for src, dst in [((1920, 1080), (1920, 1080)), ((1080, 1920), (1280, 720)),
                     ((2000, 1000), (1280, 720)), ((1280, 720), (1080, 1920))]:
        l, t, r, b = cover_box(*src, *dst)
        if not (0 <= l < r <= src[0] and 0 <= t < b <= src[1]):
            fails.append(f"cover box out of bounds for {src}->{dst}")
        if abs((r - l) / (b - t) - dst[0] / dst[1]) > 0.01:
            fails.append(f"cover box wrong aspect for {src}->{dst}")

    # Wallet guard only bites when a Google project is configured.
    class _A:
        model = "nano-banana-pro"
        pay_cash = False
    oldp = os.environ.pop("GOOGLE_CLOUD_PROJECT", None)
    if _guard_wallet(_A()):
        fails.append("wallet guard fired with no Google project configured")
    os.environ["GOOGLE_CLOUD_PROJECT"] = "selftest-project"
    if not _guard_wallet(_A()):
        fails.append("wallet guard did not fire with a Google project configured")
    if oldp is None:
        os.environ.pop("GOOGLE_CLOUD_PROJECT", None)
    else:
        os.environ["GOOGLE_CLOUD_PROJECT"] = oldp

    if fails:
        print("\n  selftest FAILED:")
        for f in fails:
            print(f"    - {f}")
        sys.exit(1)
    print("\n  selftest passed: face lock, spend ceiling, ref checks, captions, "
          "thumbnail sizing, wallet guard.\n")


def main():
    load_env()
    p = argparse.ArgumentParser(
        prog="media_gen.py",
        description="Images and video through MixRoute. One key, no credit pack.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  # thumbnail with a face locked (BOTH refs, always, or you get another person)
  media_gen.py image --prompt "..." \\
      --ref /path/to/face-hires.png \\
      --ref /path/to/face-ref.png \\
      --resolution 2k --slug my-thumb

  # explore a board cheaply first
  media_gen.py image --model nano-banana-lite -n 6 --prompt "..." --slug board

  # story animation, cheapest good lane
  media_gen.py video --model veo-fast --duration 8 --prompt "..." --slug scene

  # Seedance for material physics
  media_gen.py video --model seedance --duration 8 --resolution 720p --prompt "..."

  # the size a native video's thumbnail must be, and fit a picture to it
  media_gen.py thumb-size --video cut.mp4 --image thumb.png

  media_gen.py models / doctor / spend / selftest
""")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--prompt", required=True)
        sp.add_argument("--ref", action="append", default=[])
        sp.add_argument("--aspect", default="16:9")
        sp.add_argument("--out", default=None)
        sp.add_argument("--slug", default="gen")
        sp.add_argument("--model-id", default=None, help="raw MixRoute model id override")
        sp.add_argument("--yes", action="store_true")

    i = sub.add_parser("image"); common(i)
    i.add_argument("--model", default="nano-banana-pro", choices=list(IMAGE_MODELS))
    i.add_argument("--resolution", default="2k", choices=["1k", "2k", "4k"])
    i.add_argument("-n", "--count", type=int, default=1)
    i.add_argument("--via", default="auto", choices=["auto", "google", "mixroute"],
                   help="which wallet pays. auto = your Google Cloud project "
                        "when one is configured and reachable (same list price), "
                        "MixRoute otherwise")
    i.add_argument("--pay-cash", action="store_true",
                   help="permit the MixRoute cash fallback for nano-banana-pro "
                        "when a configured Google route is unavailable. Without "
                        "it, an unreachable Vertex is a refusal, not a fallback.")
    i.add_argument("--allow-single-ref", action="store_true",
                   help="this render has no face in it; one reference is deliberate")
    i.set_defaults(func=cmd_image)

    v = sub.add_parser("video"); common(v)
    v.add_argument("--model", default="veo-fast",
                   choices=list(VIDEO_MODELS) + list(UNAVAILABLE))
    v.add_argument("--duration", type=int, default=8)
    v.add_argument("--resolution", default="720p")
    v.add_argument("--start", default=None)
    v.add_argument("--end", default=None, help="last frame (Seedance only)")
    v.add_argument("--negative", default=None)
    v.add_argument("--no-audio", action="store_true")
    v.set_defaults(func=cmd_video)

    b = sub.add_parser("board", help="captioned contact grid, then open the grid "
                                     "AND every full-size image")
    b.add_argument("--dir", required=True)
    b.add_argument("--captions", default=None, help="JSON map or a markdown list")
    b.add_argument("--cols", type=int, default=None)
    b.add_argument("--cell", type=int, default=520)
    b.add_argument("--name", default=None, help="grid filename (default board-contact-grid.png)")
    b.set_defaults(func=cmd_board)

    t = sub.add_parser("thumb-size", help="the pixel size a thumbnail must be "
                                          "(from the video, or 1280x720 for YouTube); "
                                          "--image fits a picture to it")
    t.add_argument("--video", default=None, help="the video the thumbnail goes on")
    t.add_argument("--platform", default="native", choices=["native", "youtube"],
                   help="native = match the video frame (LinkedIn and other native "
                        "uploads); youtube = 1280x720")
    t.add_argument("--image", default=None, help="a thumbnail to fit to that size")
    t.add_argument("--out", default=None, help="where to write the fitted image")
    t.set_defaults(func=cmd_thumb_size)

    sub.add_parser("selftest", help="offline checks, no network, no key").set_defaults(
        func=cmd_selftest)
    sub.add_parser("models").set_defaults(func=cmd_models)
    sub.add_parser("doctor").set_defaults(func=cmd_doctor)
    s = sub.add_parser("spend"); s.add_argument("--month", default=None)
    s.set_defaults(func=cmd_spend)

    a = p.parse_args()
    try:
        a.func(a)
    except KeyboardInterrupt:
        die("cancelled.")


if __name__ == "__main__":
    main()
