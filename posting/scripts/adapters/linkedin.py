"""LinkedIn: a personal profile post, video or written, through LinkedIn's official API.

Composio route (the easy option). The tool names and arguments are the ones the live system this was ported from used
in October and November 2026:
    LINKEDIN_WHO_AM_I                 your member id ("sub"), for the author and owner fields
    LinkedIn Videos API (proxy)       videos?action=initializeUpload with uploadThumbnail true when the leg has a thumb,
                                      the parts PUT to the signed upload URLs, the thumbnail PUT to its signed URL,
                                      videos?action=finalizeUpload, then the video read until AVAILABLE.
                                      This is the ONLY route found that carries a custom video thumbnail: Composio's own
                                      LINKEDIN_UPLOAD_VIDEO has no thumbnail field. It was proven on a real post in the
                                      live system (cover matched the picked thumbnail). The thumbnail cannot be changed
                                      after the post is live, so it goes up with the video or the post does not go.
    LINKEDIN_CREATE_VIDEO_POST        video_urn, commentary, visibility PUBLIC, title
    LINKEDIN_CREATE_LINKED_IN_POST    author, commentary, visibility, lifecycleState PUBLISHED, images (local paths)
    LINKEDIN_CREATE_COMMENT_ON_POST   target_urn, object, actor, message {text}
    LINKEDIN_GET_POST_CONTENT         the read-back; in the live system this read came back Forbidden for a personal
                                      post, so read_back then tries the public post page, and otherwise answers
                                      "unconfirmed": you look at the post and record it with `plan.py posted`.

Captions go out in LinkedIn's "little text format": reserved characters are escaped, and a person is tagged as
@[Name](urn:li:person:<id>) only when the leg's `mentions` carries their id. LinkedIn gives a member's id only inside
the app that person connected to, so in practice you can tag only people who connected their own LinkedIn to the same
app. Everyone else is named untagged, or tagged by your hand. Mentions are untested in this module.

LinkedIn messages and connection requests are never sent by this module, or by any machine.
"""
import html, json, re, time, urllib.parse, urllib.request
from datetime import date
from pathlib import Path

from .base import Adapter, Unsupported, composio_connection, composio_exec, composio_proxy

RESERVED = "\\|{}@[]()<>#*_~"


def ltf_escape(text):
    return "".join("\\" + ch if ch in RESERVED else ch for ch in text)


def commentary(caption, mentions):
    """The caption with the first occurrence of each mention's name as @[Name](urn), everything else escaped."""
    spans = []
    for m in mentions or []:
        name, urn = m.get("name", ""), m.get("urn", "")
        if not name or not urn.startswith("urn:li:"):
            continue
        hit = re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", caption)
        if hit and not any(a < hit.end() and hit.start() < b for a, b, _, _ in spans):
            spans.append((hit.start(), hit.end(), name, urn))
    out, pos = [], 0
    for a, b, name, urn in sorted(spans):
        out += [ltf_escape(caption[pos:a]), f"@[{name}]({urn})"]
        pos = b
    out.append(ltf_escape(caption[pos:]))
    return "".join(out)


def default_version():
    """LinkedIn's API wants a recent YYYYMM version header and refuses old ones. Default: 2 months back (untested
    as a rule; set linkedin_version in the config when LinkedIn refuses it)."""
    d = date.today()
    y, m = (d.year, d.month - 2) if d.month > 2 else (d.year - 1, d.month + 10)
    return f"{y}{m:02d}"


def _put(url, path, headers):
    data = Path(path).read_bytes() if not isinstance(path, bytes) else path
    req = urllib.request.Request(url, data=data, method="PUT", headers={"Content-Type": "application/octet-stream", **headers})
    with urllib.request.urlopen(req, timeout=900) as r:
        return r.status, dict(r.headers)


class ComposioLinkedIn(Adapter):
    platform = "linkedin"

    @property
    def account(self):
        return self.settings.get("composio_account", "")

    def check_connection(self):
        composio_connection("linkedin", self.account)

    def _proxy(self, url, method="POST", body=None):
        ver = self.settings.get("linkedin_version") or default_version()
        return composio_proxy(url, "linkedin", method, body, account=self.account,
                              headers=(f"LinkedIn-Version: {ver}", "X-Restli-Protocol-Version: 2.0.0"))

    def _me(self):
        me = composio_exec("LINKEDIN_WHO_AM_I", {}, self.account)
        sub = me.get("sub") or (me.get("data") or {}).get("sub") or me.get("id") or (me.get("response_data") or {}).get("sub")
        if not sub:
            raise RuntimeError(f"LINKEDIN_WHO_AM_I gave no member id: {str(me)[:200]}")
        return f"urn:li:person:{sub}"

    def whoami(self):
        return self._me().rsplit(":", 1)[-1]

    def _video_asset(self, leg, owner):
        video = Path(leg["file"])
        thumb = leg.get("thumb") or ""
        init = self._proxy("https://api.linkedin.com/rest/videos?action=initializeUpload", "POST",
                           {"initializeUploadRequest": {"owner": owner, "fileSizeBytes": video.stat().st_size,
                                                        "uploadCaptions": False, "uploadThumbnail": bool(thumb)}})
        v = init.get("value") or {}
        urn, token, parts, turl = v.get("video"), v.get("uploadToken", ""), v.get("uploadInstructions") or [], v.get("thumbnailUploadUrl")
        if not urn or not parts or (thumb and not turl):
            raise RuntimeError(f"initializeUpload failed: {str(init)[:300]}")
        etags = []
        raw = video.read_bytes()
        for p in parts:
            first, last = int(p["firstByte"]), int(p["lastByte"])
            _, headers = _put(p["uploadUrl"], raw[first:last + 1], {})
            etag = {k.lower(): val for k, val in headers.items()}.get("etag")
            if not etag:
                raise RuntimeError(f"part {first}-{last} returned no ETag")
            etags.append(etag.strip('"'))
        if thumb:
            status, _ = _put(turl, thumb, {"media-type-family": "STILLIMAGE"})
            if status not in (200, 201, 204):
                raise RuntimeError(f"thumbnail upload returned {status}; the post does not go without it")
        self._proxy("https://api.linkedin.com/rest/videos?action=finalizeUpload", "POST",
                    {"finalizeUploadRequest": {"video": urn, "uploadToken": token, "uploadedPartIds": etags}})
        for _ in range(40):
            st = self._proxy(f"https://api.linkedin.com/rest/videos/{urllib.parse.quote(urn, safe='')}", "GET")
            if st.get("status") == "AVAILABLE":
                return urn
            if st.get("status") == "PROCESSING_FAILED":
                raise RuntimeError(f"LinkedIn video processing failed: {st}")
            time.sleep(15)
        raise RuntimeError(f"LinkedIn video {urn} not AVAILABLE after 10 minutes")

    def upload(self, leg):
        owner = self._me()
        text = commentary(leg["caption"], leg.get("mentions"))
        if leg["kind"] == "linkedin_video":
            urn = self._video_asset(leg, owner)
            args = {"video_urn": urn, "commentary": text, "visibility": "PUBLIC"}
            if leg.get("title"):
                args["title"] = leg["title"][:400]
            res = composio_exec("LINKEDIN_CREATE_VIDEO_POST", args, self.account)
        else:
            args = {"author": owner, "commentary": text, "visibility": "PUBLIC", "lifecycleState": "PUBLISHED"}
            if leg.get("thumb"):
                args["images"] = [leg["thumb"]]
            res = composio_exec("LINKEDIN_CREATE_LINKED_IN_POST", args, self.account)
        pid = res.get("post_id") or res.get("id") or res.get("urn") or ""
        if not pid:
            found = re.search(r"urn:li:(ugcPost|share|activity):\d+", json.dumps(res))
            pid = found.group(0) if found else ""
        if not pid:
            raise RuntimeError(f"LinkedIn post returned no id: {str(res)[:300]}")
        return {"post_id": pid, "post_url": f"https://www.linkedin.com/feed/update/{pid}/"}

    def comment(self, leg, post_id, text):
        r = composio_exec("LINKEDIN_CREATE_COMMENT_ON_POST", {"target_urn": post_id, "object": post_id, "actor": self._me(),
                                                              "message": {"text": text}}, self.account)
        cid = str(r.get("id") or r.get("comment_urn") or "")
        if not cid:
            raise RuntimeError(f"comment returned no id: {str(r)[:200]}")
        return cid

    def read_back(self, leg):
        want = leg["caption"][:60]
        try:
            r = composio_exec("LINKEDIN_GET_POST_CONTENT", {"post_id": leg["post_id"]}, self.account)
            if want and want in json.dumps(r, ensure_ascii=False).replace("\\", ""):
                return "live", "API read: the caption is on the post"
        except RuntimeError:
            pass
        try:   # the public post page (untested in this module)
            req = urllib.request.Request(leg["post_url"], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                page = resp.read(3_000_000).decode("utf-8", "replace")
            if want and want[:40] in html.unescape(page):
                return "live", "the public post page carries the caption"
        except Exception as ex:
            return "unconfirmed", f"API read refused and the public page did not load ({str(ex)[:80]}); open {leg['post_url']} and record it with plan.py posted"
        return "unconfirmed", f"could not find the caption on the post; open {leg['post_url']} and look"


class DirectLinkedIn(Adapter):
    """UNTESTED STUB. LinkedIn's own API with your own developer app: the "Share on LinkedIn" product gives the
    w_member_social scope; posts go to /rest/posts with author urn:li:person:<id>, videos through /rest/videos as above.
    Reading a personal post back may need a scope that product does not give."""
    platform = "linkedin"

    def _no(self, *a, **k):
        raise Unsupported("the direct LinkedIn route is a stub in this module (untested); use the composio route")

    upload = comment = read_back = _no
