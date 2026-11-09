"""Instagram: a Reel on a professional (Business or Creator) account, through Meta's Instagram Graph API.

Instagram fetches the video from a public URL itself, so the file needs hosting first (posting/README.md, "Hosting").

Composio route (the easy option). The tool names and arguments are the ones the live system this was ported from used
in October and November 2026:
    INSTAGRAM_GET_USER_INFO              your Instagram user id
    INSTAGRAM_POST_IG_USER_MEDIA         ig_user_id, media_type REELS, video_url (public), caption, share_to_feed, cover_url
    INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH ig_user_id, creation_id, max_wait_seconds
    INSTAGRAM_GET_IG_MEDIA               ig_media_id, fields permalink
    INSTAGRAM_GET_IG_USER_MEDIA          the read-back: is the media id among your recent posts
    INSTAGRAM_POST_IG_MEDIA_COMMENTS     ig_media_id, message (the full-video link)

Limits the live system worked to (from its research, not re-checked here): Reels 3 s to 15 min, audio at 48 kHz at
most, caption 2,200 characters, a Reel over 3 minutes is not shown to non-followers.
"""
import json, re

from .base import Adapter, Unsupported, composio_connection, composio_exec, public_url


class ComposioInstagram(Adapter):
    platform = "instagram"

    @property
    def account(self):
        return self.settings.get("composio_account", "")

    def check_connection(self):
        composio_connection("instagram", self.account)

    def _uid(self):
        info = composio_exec("INSTAGRAM_GET_USER_INFO", {}, self.account)
        return str(info.get("id") or (info.get("user") or {}).get("id") or "me")

    def whoami(self):
        uid = self._uid()
        if uid == "me":
            raise RuntimeError("INSTAGRAM_GET_USER_INFO returned no user id")
        return uid

    def upload(self, leg):
        uid = self._uid()
        args = {"ig_user_id": uid, "media_type": "REELS", "video_url": public_url(self.ctx, leg, "file"),
                "caption": leg["caption"], "share_to_feed": True}
        if leg.get("thumb"):
            args["cover_url"] = public_url(self.ctx, leg, "thumb")
        cont = composio_exec("INSTAGRAM_POST_IG_USER_MEDIA", args, self.account)
        cid = str(cont.get("id") or cont.get("creation_id") or "")
        if not cid:
            raise RuntimeError(f"Instagram container returned no id: {str(cont)[:300]}")
        pub = composio_exec("INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH", {"ig_user_id": uid, "creation_id": cid, "max_wait_seconds": 300},
                            self.account, timeout=900)
        mid = str(pub.get("id") or (pub.get("response") or {}).get("id") or "")
        if not mid:
            raise RuntimeError(f"Instagram publish returned no media id: {str(pub)[:300]}")
        link = ""
        try:
            link = composio_exec("INSTAGRAM_GET_IG_MEDIA", {"ig_media_id": mid, "fields": "permalink"}, self.account).get("permalink", "")
        except RuntimeError:
            pass
        return {"post_id": mid, "post_url": link}

    def comment(self, leg, post_id, text):
        r = composio_exec("INSTAGRAM_POST_IG_MEDIA_COMMENTS", {"ig_media_id": post_id, "message": text[:300]}, self.account)
        cid = str(r.get("id") or "")
        if not cid:
            raise RuntimeError(f"comment returned no id: {str(r)[:200]}")
        return cid

    def read_back(self, leg):
        r = composio_exec("INSTAGRAM_GET_IG_USER_MEDIA", {"ig_user_id": self._uid(), "limit": 10}, self.account)
        ids = re.findall(r'"id":\s*"(\d+)"', json.dumps(r))
        if leg["post_id"] in ids:
            return "live", f"the media id is among the {len(ids)} most recent posts"
        return "missing", f"not among the {len(ids)} most recent posts"


class DirectInstagram(Adapter):
    """UNTESTED STUB. Instagram Graph API with your own Meta app: POST /<ig-user-id>/media (media_type REELS,
    video_url, caption), poll the container's status_code until FINISHED, POST /<ig-user-id>/media_publish
    (creation_id), POST /<media-id>/comments. Needs instagram_content_publish and a professional account linked to a
    Facebook Page."""
    platform = "instagram"

    def _no(self, *a, **k):
        raise Unsupported("the direct Instagram route is a stub in this module (untested); use the composio route")

    upload = comment = read_back = _no
