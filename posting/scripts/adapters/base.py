"""The adapter interface every platform implements, plus the shared helpers for the Composio route.

An adapter has 5 jobs:
    whoami()                       the connected account's own id (channel id, member id, user id). The runner compares
                                   it with expected_account_id in the config before EVERY upload and refuses on a
                                   mismatch or an empty pin: a post on the wrong profile cannot be moved, only deleted.
    upload(leg)                    put the media up and create the post (on YouTube: a PRIVATE video). Returns
                                   {"post_id": ..., "post_url": ...}. Called once per leg, ever: the runner writes the
                                   post_id onto the leg before anything else, and never calls upload on a leg that has one.
    schedule(leg, post_id, utc)    set the publish time on the platform itself (YouTube publishAt). Raises Unsupported
                                   on a platform that cannot schedule through its API: the runner then posts at the slot.
    comment(leg, post_id, text)    the full-video link as a comment under the post. Returns the comment id.
    read_back(leg)                 read the post back from the platform. Returns (state, info):
                                   "live"       the post is up and public: this is the proof
                                   "scheduled"  it exists and is waiting for its publish time
                                   "processing" it exists and the platform is still working on it
                                   "missing"    the platform does not show it
                                   "unconfirmed" the read was refused or unreadable (not proof either way)

Routes: "composio" (Composio's CLI and your connected accounts, the easy option), "direct" (each platform's own API
with your own app; stubs here, untested), "fake" (the self-tests). A route is chosen per platform in the config.
"""
import json, os, subprocess, tempfile, time, urllib.request
from pathlib import Path


class Unsupported(Exception):
    """This route cannot do this job; the caller has a fallback (post at the slot, ask a person)."""


class Adapter:
    platform = ""
    supports_schedule = False

    def __init__(self, ctx, settings):
        self.ctx = ctx
        self.settings = settings or {}

    def check_connection(self):
        """Raise unless exactly one usable account is connected for this platform."""

    def whoami(self):
        raise Unsupported(f"no identity read for {self.platform} on this route")

    def upload(self, leg):
        raise NotImplementedError

    def schedule(self, leg, post_id, publish_at_utc):
        raise Unsupported(f"{self.platform} posts at the slot; it has no scheduling call on this route")

    def comment(self, leg, post_id, text):
        raise Unsupported(f"no comment route for {self.platform}")

    def read_back(self, leg):
        raise NotImplementedError


# ---------- the Composio route ----------
# These are the same CLI calls the live system this module was ported from makes: `composio execute <TOOL> -d @args.json`
# and `composio proxy <url> --toolkit <name>`. The CLI's output shape can change between versions; the reader below
# takes the first JSON object in the output and checks its "successful" flag.

def _first_json(raw):
    i = raw.find("{")
    if i < 0:
        return {}
    try:
        return json.loads(raw[i:])
    except json.JSONDecodeError:
        depth = 0
        for j, ch in enumerate(raw[i:], start=i):
            depth += ch == "{"
            depth -= ch == "}"
            if depth == 0:
                try:
                    return json.loads(raw[i:j + 1])
                except json.JSONDecodeError:
                    break
        return {"raw": raw[-800:]}


def composio_exec(tool, args, account="", timeout=1800):
    fd, req = tempfile.mkstemp(suffix=".json", prefix="composio-args-")
    with os.fdopen(fd, "w") as f:
        json.dump(args, f)
    cmd = ["composio", "execute", tool, "-d", f"@{req}"] + (["--account", account] if account else [])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    finally:
        os.unlink(req)
    res = _first_json(r.stdout + r.stderr)
    if not res.get("successful", False):
        raise RuntimeError(f"{tool}: {str(res.get('error') or res)[:600]}")
    return res.get("data") or {}


def composio_proxy(url, toolkit, method="GET", body=None, headers=(), account="", timeout=180):
    """A raw call to the platform's own API, signed with your connected account."""
    cmd = ["composio", "proxy", url, "--toolkit", toolkit, "-X", method, "-H", "content-type: application/json"]
    for h in headers:
        cmd += ["-H", h]
    if account:
        cmd += ["--account", account]
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    return _first_json(r.stdout + r.stderr)


def composio_connection(toolkit, pinned=""):
    """Exactly one ACTIVE connection for the toolkit (the pinned one when the config names it), or refuse.
    The JSON shape read here is the one our CLI version printed in late 2026; if it changes, this refuses, never guesses."""
    r = subprocess.run(["composio", "connections", "list", "--toolkit", toolkit], capture_output=True, text=True,
                       timeout=60, stdin=subprocess.DEVNULL)
    data = _first_json(r.stdout)
    items = data.get(toolkit) if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise RuntimeError(f"could not read {toolkit} connections; refusing to post: {(r.stdout + r.stderr)[-200:]}")
    active = [x for x in items if x.get("status") == "ACTIVE"]
    if pinned:
        active = [x for x in active if pinned in (x.get("word_id"), x.get("id"))]
    if len(active) != 1:
        raise RuntimeError(f"{toolkit}: {len(active)} ACTIVE connection(s)" + (f" matching {pinned}" if pinned else "")
                           + "; refusing to post (pin one in the config)")
    return active[0]


# ---------- hosting: a public URL for platforms that fetch the file themselves (Instagram) ----------

def public_url(ctx, leg, field="file"):
    """A public https URL for the leg's file or thumb: the leg's own `<field>_url` when set, else the config's hosting
    command. Untested in this module: it depends on the storage you choose."""
    own = leg.get(f"{field}_url", "")
    if own.startswith("https://"):
        return own
    host = ctx.cfg.get("hosting") or {}
    cmd, tmpl = host.get("upload_command"), host.get("public_url", "")
    if not cmd or not tmpl:
        raise Unsupported(f"{leg['platform']} needs a public URL for the {field}: set {field}_url on the leg, "
                          "or hosting.upload_command and hosting.public_url in the config")
    path = Path(leg[field])
    key = f"{leg['date']}/{path.name}"
    r = subprocess.run([c.replace("{file}", str(path)).replace("{key}", key) for c in cmd], capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        raise RuntimeError(f"hosting upload failed: {(r.stdout + r.stderr)[-300:]}")
    url = tmpl.replace("{key}", key)
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as resp:
        if resp.status != 200:
            raise RuntimeError(f"hosted file is not public: HTTP {resp.status}")
    return url


def wait(seconds):
    time.sleep(seconds)
