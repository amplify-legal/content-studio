"""YouTube: upload PRIVATE, then set publishAt so YouTube itself publishes at the slot.

Composio route (the easy option): the tool names and arguments below are the ones the live system this was ported from
used in October and November 2026. If Composio renames one, `composio search youtube upload` finds the new name.
    YOUTUBE_MULTIPART_UPLOAD_VIDEO   title, description, categoryId, privacyStatus "private", videoFile (a local path), tags
    videos.list (through the proxy)  the ghost check right after the upload, and the read-back
    videos.update status (proxy)     privacyStatus "private" plus publishAt, read back until it sticks
    YOUTUBE_UPDATE_THUMBNAIL         videoId, thumbnailUrl (long form only; a Short's cover is picked in the YouTube app)
    YOUTUBE_POST_COMMENT             videoId, channelId, textOriginal (the full-video link, once the video is public)

Read-back proof: processingStatus "succeeded", a duration above 0 and privacy "public". A row in a listing is not proof.

Quota: Composio's default YouTube connection runs on Composio's own Google Cloud project, shared by every Composio
customer. The live system hit that pool's daily limit with 0 uploads of its own that day, and moved to its own Google
Cloud project behind a Composio custom auth config. Your own project gets its own quota: see posting/README.md.
"""
import json, re, time

from .base import Adapter, Unsupported, composio_connection, composio_exec, composio_proxy, public_url

API = "https://www.googleapis.com/youtube/v3"


def duration_seconds(iso):
    m = re.fullmatch(r"P(?:(\d+)D)?(?:T(?=\d)(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?", str(iso or ""))
    return sum(float(x or 0) * s for x, s in zip(m.groups(), (86400, 3600, 60, 1))) if m else 0.0


def state_of(item):
    """(state, info) from one videos.list item."""
    if not item:
        return "missing", "videos.list returned nothing"
    proc = (item.get("processingDetails") or {}).get("processingStatus")
    secs = duration_seconds((item.get("contentDetails") or {}).get("duration"))
    st = item.get("status") or {}
    info = f"processing {proc}, duration {secs:.0f} s, privacy {st.get('privacyStatus')}, publishAt {st.get('publishAt')}"
    if proc != "succeeded" or secs <= 0:
        return "processing", info
    if st.get("privacyStatus") == "public":
        return "live", info
    return "scheduled", info


class ComposioYouTube(Adapter):
    platform = "youtube"
    supports_schedule = True

    @property
    def account(self):
        return self.settings.get("composio_account", "")

    def check_connection(self):
        composio_connection("youtube", self.account)

    def _proxy(self, url, method="GET", body=None):
        return composio_proxy(url, "youtube", method, body, account=self.account)

    def _video(self, vid):
        r = self._proxy(f"{API}/videos?part=snippet,status,contentDetails,processingDetails&id={vid}")
        items = r.get("items") or []
        return items[0] if items else None

    def whoami(self):
        r = self._proxy(f"{API}/channels?part=id&mine=true")
        items = r.get("items") or []
        if len(items) != 1:
            raise RuntimeError(f"channel read returned {len(items)} channels: {str(r)[:200]}")
        return items[0]["id"]

    def upload(self, leg):
        desc = leg.get("description") or leg.get("caption") or ""
        req = {"title": leg["title"][:100], "description": desc[:4900], "privacyStatus": "private",
               "categoryId": str(self.settings.get("category_id", "22")), "videoFile": leg["file"],
               "tags": list(leg.get("tags") or [])}
        res = composio_exec("YOUTUBE_MULTIPART_UPLOAD_VIDEO", req, self.account, timeout=3600)
        found = re.search(r'"id":\s*"([A-Za-z0-9_-]{11})"', json.dumps(res))
        if not found:
            raise RuntimeError(f"YouTube upload returned no video id: {str(res)[:300]}")
        vid = found.group(1)
        time.sleep(5)
        if not self._video(vid):
            raise RuntimeError(f"YouTube upload {vid} is a ghost: videos.list returned nothing")
        return {"post_id": vid, "post_url": f"https://youtu.be/{vid}"}

    def schedule(self, leg, post_id, publish_at_utc):
        body = {"id": post_id, "status": {"privacyStatus": "private", "publishAt": publish_at_utc,
                                          "selfDeclaredMadeForKids": bool(self.settings.get("made_for_kids", False))}}
        for _ in range(6):
            self._proxy(f"{API}/videos?part=status", "PUT", body)
            time.sleep(4)
            st = (self._video(post_id) or {}).get("status") or {}
            if str(st.get("publishAt", "")).startswith(publish_at_utc[:16]):
                break
            time.sleep(10)
        else:
            raise RuntimeError(f"publishAt did not stick on {post_id}")
        if leg["kind"] == "youtube_long" and leg.get("thumb"):
            try:   # a failed thumbnail never fails the upload; the runner logs it
                composio_exec("YOUTUBE_UPDATE_THUMBNAIL", {"videoId": post_id, "thumbnailUrl": public_url(self.ctx, leg, "thumb")}, self.account)
            except (Unsupported, RuntimeError) as ex:
                raise RuntimeError(f"scheduled, but the thumbnail did not go on: {ex}") from ex

    def comment(self, leg, post_id, text):
        ch = ((self._video(post_id) or {}).get("snippet") or {}).get("channelId")
        if not ch:
            raise RuntimeError("no channelId on the video read")
        r = composio_exec("YOUTUBE_POST_COMMENT", {"videoId": post_id, "channelId": ch, "textOriginal": text}, self.account)
        cid = str(r.get("id") or ((r.get("snippet") or {}).get("topLevelComment") or {}).get("id") or "")
        if not cid:
            raise RuntimeError(f"comment returned no id: {str(r)[:200]}")
        return cid

    def read_back(self, leg):
        return state_of(self._video(leg["post_id"]))


class DirectYouTube(Adapter):
    """UNTESTED STUB. YouTube Data API v3 with your own OAuth client:
    videos.insert (resumable upload, part=snippet,status, privacyStatus private), videos.update part=status with
    publishAt, thumbnails.set, commentThreads.insert, videos.list part=status,contentDetails,processingDetails.
    Scopes: youtube.upload and youtube.force-ssl. You hold the refresh token yourself here, so keep it out of the repo."""
    platform = "youtube"
    supports_schedule = True

    def _no(self, *a, **k):
        raise Unsupported("the direct YouTube route is a stub in this module (untested); use the composio route, or build it on the calls in this docstring")

    upload = schedule = comment = read_back = _no
