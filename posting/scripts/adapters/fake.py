"""A pretend platform for the self-tests and for a first dry week. It keeps its posts in
content/posting/fake-platform.json in the project, so a read-back works across ticks. It never touches a network.

Settings (in the config's adapters.<platform>, or set by a self-test):
    "fail_uploads": 2          the first 2 uploads raise an error
    "read_back": "unconfirmed" read_back answers this state until the post is read with "confirm_after" reads done
    "confirm_after": 1         how many read-backs answer `read_back` before the truth comes back
"""
import json
from datetime import datetime

from .base import Adapter


class FakeAdapter(Adapter):
    supports_schedule = False

    def __init__(self, ctx, settings, platform):
        super().__init__(ctx, settings)
        self.platform = platform
        self.supports_schedule = platform == "youtube"
        self.path = ctx.project / "content" / "posting" / "fake-platform.json"

    def _load(self):
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {"posts": {}, "uploads": 0, "upload_errors": 0, "reads": {}}

    def _save(self, st):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(st, indent=1))

    def whoami(self):
        return self.settings.get("account_id", "fake-creator")

    def upload(self, leg):
        st = self._load()
        if st["upload_errors"] < int(self.settings.get("fail_uploads", 0)):
            st["upload_errors"] += 1
            self._save(st)
            raise RuntimeError("fake platform: upload refused (a generic error)")
        st["uploads"] += 1
        pid = f"{self.platform}-{st['uploads']}"
        st["posts"][pid] = {"leg": leg["id"], "platform": self.platform, "caption": leg.get("caption", ""),
                            "public": self.platform != "youtube", "publish_at": "", "comments": []}
        self._save(st)
        return {"post_id": pid, "post_url": f"https://fake.example/{pid}"}

    def schedule(self, leg, post_id, publish_at_utc):
        st = self._load()
        st["posts"][post_id]["publish_at"] = publish_at_utc
        self._save(st)

    def comment(self, leg, post_id, text):
        st = self._load()
        post = st["posts"][post_id]
        post["comments"].append(text)
        self._save(st)
        return f"{post_id}-c{len(post['comments'])}"

    def read_back(self, leg):
        st = self._load()
        post = st["posts"].get(leg.get("post_id", ""))
        n = st["reads"].get(leg["id"], 0)
        st["reads"][leg["id"]] = n + 1
        self._save(st)
        if self.settings.get("read_back") and n < int(self.settings.get("confirm_after", 1)):
            return self.settings["read_back"], "fake platform: answered as told"
        if not post:
            return "missing", "fake platform: no such post"
        if self.platform == "youtube" and not post["public"]:
            if post["publish_at"] and datetime.fromisoformat(post["publish_at"].replace("Z", "+00:00")) <= self.ctx.now():
                post["public"] = True
                self._save(st)
            else:
                return "scheduled", f"private, publishAt {post['publish_at'] or 'none'}"
        return "live", f"fake platform: {post['leg']} is public"


def posts(ctx):
    """Every fake post, for the self-tests to count."""
    p = ctx.project / "content" / "posting" / "fake-platform.json"
    return json.loads(p.read_text())["posts"] if p.exists() else {}
