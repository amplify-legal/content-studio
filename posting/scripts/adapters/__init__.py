"""Platform adapters. `get(ctx, platform)` returns the adapter the config names for that platform.

Only YouTube, LinkedIn and Instagram have machine routes here. TikTok and Substack (and any platform you list in
hand_platforms) are hand cards: the watcher writes the card, you post it, and nothing here ever posts them.
"""
from .base import Adapter, Unsupported
from .fake import FakeAdapter
from .instagram import ComposioInstagram, DirectInstagram
from .linkedin import ComposioLinkedIn, DirectLinkedIn
from .youtube import ComposioYouTube, DirectYouTube

ROUTES = {
    ("youtube", "composio"): ComposioYouTube, ("youtube", "direct"): DirectYouTube,
    ("linkedin", "composio"): ComposioLinkedIn, ("linkedin", "direct"): DirectLinkedIn,
    ("instagram", "composio"): ComposioInstagram, ("instagram", "direct"): DirectInstagram,
}


def get(ctx, platform):
    settings = (ctx.cfg.get("adapters") or {}).get(platform) or {}
    route = settings.get("route", "composio")
    if route == "fake":
        return FakeAdapter(ctx, settings, platform)
    cls = ROUTES.get((platform, route))
    if not cls:
        raise Unsupported(f"no {route} route for {platform}; it is a hand card platform or the config names an unknown route")
    return cls(ctx, settings)
