#!/usr/bin/env python3
"""
copy_check.py, the guard that reads your copy before anybody else does.

WHAT THIS IS FOR

Every business has a handful of claims it must never make and a handful of
phrases somebody has already struck by hand more than once. Writing the rule
down somewhere the machine reads does not hold, and here is the honest reason:
a rule broken while it sits in context is a rule that needs a checker. The same
forbidden idea shows up in 3 template variants with 3 wordings that share no
searchable string. You find out when the copy is already out.

So the rule gets a script. The script runs on the copy, not on the intention,
and it runs every time. If a rule keeps getting broken, the answer is a
checker, never a longer paragraph in an instructions file.

WHAT IT CHECKS

Three tiers, and the difference matters.

  ALWAYS          mechanical rules about form. Always on. A hit fails the run.
                    em-dash     no em dashes (and no spaced en dash used as one)
                    bare-link   a link meant to be clicked carries https://
  BANNED_CLAIMS   phrases and claims that must never ship. A hit fails the run.
                  Ships with generic rules that hold for most people. Edit it.
  VOICE_PATTERNS  constructions that usually mean the copy reads written rather
                  than said. A hit warns and never changes the exit code. Your
                  own ear beats the pattern every time.

Plus OPTIONAL_CLAIMS, off by default, on with --strict. They are rules that are
right for many businesses and wrong for some, so you opt in.

WHAT THIS SCRIPT DOES NOT DO, ON PURPOSE

It cannot recognise a construction. The antithesis, the connoisseur's rating,
the aphorism closer and the essay verb are shapes, not phrases, and a regex
that tried to catch them all would fire on good sentences and miss the ones a
person would strike. Those belong to a reader (a person, or a voice-check agent
that reads your writing rules at run time). This script owns the phrases
somebody wrote down word for word. The VOICE_PATTERNS tier is a narrow,
advisory exception for the few constructions that recur with a fixed wording.

It also reads 1 file at a time, so it can never see a batch. A phrase that is
fine once and tiring in 36 letters out of 97 is a frequency problem, and the
fix is a batch check, not a ban here. Banning it here would push everybody to
one replacement phrase, which then carries 36 of 97 letters instead.

TWO RULES ABOUT THIS SCRIPT

1. A rules file will flag itself, because it quotes the banned phrases in order
   to ban them. That is correct. Run the checker on the copy that ships, never
   rewrite a rule so the report goes green.

2. A template you have approved and frozen must exit 0. A checker that refuses
   your own approved copy either stops the run or gets the template rewritten
   by the next session. When that happens, narrow the pattern to the direction
   and the shape you actually struck, and add the approved line to SELF_TEST as
   a case that must come back clean.

USAGE

    python3 scripts/copy_check.py <file> [<file> ...]
    python3 scripts/copy_check.py --strict <file>     also run OPTIONAL_CLAIMS
    cat draft.txt | python3 scripts/copy_check.py -
    python3 scripts/copy_check.py --self-test

Exit 0 when clean, 1 when something is flagged. Standard library only.

ESCAPE HATCH

Put `copy-check: allow` anywhere on a line and that line is skipped. Use it on
real copy that is right and trips a pattern, never to silence a finding you
have not read.
"""

import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# bare-link. A link in a message carries https:// on the front or it is not
# reliably a link.
#
# Why this is a rule: messaging clients decide for themselves whether a bare
# "host/path" becomes a link, and they decide differently by top-level domain.
# In one measured case the same client linkified a bare address on one TLD and
# left a bare address on another TLD as plain text, same message shape, same
# day. Dozens of people got a correct address that did nothing when tapped.
# The scheme is the only form that linkifies whatever the TLD.
#
# Why it only fires on host + path: a bare domain with no path is how most
# signatures read, and most clients linkify it. Firing on it would make the
# checker noisy, and a noisy checker is one people stop running.
#
# How discussing an address is told from sending one: an address you are
# talking ABOUT goes in backticks or <code>; an address you SEND goes bare on
# its own line. Also exempt: href/src values, markdown link targets, anything
# already carrying a scheme, and file paths whose "TLD" is a file extension.
# ---------------------------------------------------------------------------

BARE_LINK = re.compile(
    r"(?<![\w@./-])((?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,24})(/[^\s<>\"'`)\]]+)",
    re.I,
)

# Extensions that look like a TLD followed by a path but are file paths.
_NOT_A_TLD = {
    "py", "md", "html", "htm", "json", "jsonl", "csv", "tsv", "sh", "txt", "js",
    "mjs", "css", "yaml", "yml", "xml", "sql", "ini", "toml", "env", "log",
    "lock", "cfg", "conf", "mp4", "mov", "webm", "mp3", "wav", "m4a", "jpg",
    "jpeg", "png", "gif", "webp", "svg", "pdf", "zip", "gz", "tar", "ts", "tsx",
    "jsx", "rb", "go", "rs", "java", "c", "cpp", "h", "ass", "srt", "vtt",
}

# A block of text that is explicitly ABOUT a bare or retired address (a note
# retiring it, a rules file describing it) is not sending it. The marker must
# be in the same paragraph, so a note 400 lines away cannot excuse a live paste.
BARE_LINK_ALLOW = re.compile(
    r"retired|redirect|stub|no longer|superseded|stale|do not paste|"
    r"don't paste|unclickable|not a link|without the https|bare link|scheme",
    re.I,
)

# Places on a line where an address is shown rather than sent.
_SHOWN_PATTERNS = (
    r"`[^`]*`",                                  # backticks: discussing an address
    r"<code[^>]*>.*?</code>",                    # <code>: same, in HTML
    r"(?:href|src)\s*=\s*[\"'][^\"']*[\"']",     # inside an attribute
    r"\]\([^)]*\)",                              # a markdown link target
)
_HAS_SCHEME = (r"https?://\S+",)


def _protected_spans(line, include_scheme=True):
    """Character ranges on a line where an address is shown rather than sent."""
    spans = []
    pats = _SHOWN_PATTERNS + (_HAS_SCHEME if include_scheme else ())
    for pat in pats:
        for m in re.finditer(pat, line, re.I):
            spans.append((m.start(), m.end()))
    return spans


def bare_link_hits(line, block):
    """Yield match objects for scheme-less links that are meant to be clicked."""
    if BARE_LINK_ALLOW.search(block):
        return
    spans = _protected_spans(line)
    for m in BARE_LINK.finditer(line):
        tld = m.group(1).rsplit(".", 1)[-1].lower()
        if tld in _NOT_A_TLD:
            continue
        if any(a <= m.start() < b for a, b in spans):
            continue
        yield m


# ---------------------------------------------------------------------------
# ALWAYS ON. Not part of the editable table, on purpose.
#
# The em dash is written as an escape rather than typed, so this source file
# does not flag itself. Also caught: an en dash used as a punctuation dash
# (spaced, " - " shape). A ranged en dash between digits is left alone.
#
# bare-link is listed here so its id prints with the others; the matching is
# done by bare_link_hits(), which needs the line's context.
# ---------------------------------------------------------------------------

ALWAYS = [
    (
        "em-dash",
        re.compile("\u2014|(?<=\\s)\u2013(?=\\s)"),
        "em dash in copy, the loudest machine tell there is",
        "a comma, a period, or two sentences",
    ),
    (
        "bare-link",
        BARE_LINK,
        "a link with no https:// on the front, which a messaging client may not turn into a link",
        "put https:// on the front of the address",
    ),
]


# ---------------------------------------------------------------------------
# EDIT THIS TABLE. This is your file, not ours.
#
# One row per phrase or claim your copy must never carry. Four fields:
#
#   id       a short name you will see in the report
#   pattern  a compiled regex. re.I ignores case, re.X lets you write the
#            pattern over several lines
#   message  what is wrong with it, in the words you would use out loud
#   instead  what to write in its place. This is the field people actually
#            read at 11pm, so make it a real instruction
#
# The rows below are generic: each is a phrase or shape that has been struck
# by hand, by name, more than once, in real drafts. Keep the ones you agree
# with. Then add the 2 or 3 things somebody in YOUR business has already
# corrected more than once. That is where the script earns its place.
#
# Only exact phrases go here. A rule written as a construction ("any clause
# explaining why the message exists") is a reader's job, not a regex's.
# ---------------------------------------------------------------------------

BANNED_CLAIMS = [
    (
        # Labelling a message's own intent. "Quick question rather than a
        # pitch" makes the reader look for the pitch. If a message is not a
        # pitch, it shows, and saying so is the only thing that makes it read
        # like one. Deliberately NOT caught: "not quite a cold note", which
        # describes the relationship, not the message (see ALLOW).
        "label-intent",
        re.compile(
            r"""(
              (no|not\s+a|rather\s+than\s+a|isn't\s+a|is\s+not\s+a)\s+(pitch|sales\s+email|hard\s+sell)
            | not\s+(trying\s+to\s+)?sell(ing)?\s+you
            | this\s+(is\s+not|isn't)\s+a\s+(pitch|sale|sales)
            | no\s+hard\s+sell
            | just\s+a\s+quick\s+note,?\s+(not|no)\b
            )""",
            re.I | re.X,
        ),
        "labels the message's own intent, which makes it read like the thing it denies",
        "delete the label and let the message be what it is",
    ),
    (
        # A human question reduced to a keyword the reader is told to type
        # back. A machine asking for structured input in a person's voice.
        "keyword-reply",
        re.compile(
            r"""(
              (just\s+)?reply\s+(back\s+)?(with\s+)?["']?(yes|no|yep|interested|more)["']?\b
            | reply\s+with\s+the\s+word
            | just\s+say\s+the\s+word
            | hit\s+reply\s+with
            | (comment|type|drop)\s+["']?\w+["']?\s+(below|in\s+the\s+comments)
            | let\s+me\s+know\s+which\s+(one|option)\b
            )""",
            re.I | re.X,
        ),
        "turns a question into a menu of keywords, which nobody says out loud",
        "ask the real question and let them answer in their own words",
    ),
    (
        # Chatbot artifacts pasted out of a chat window with the assistant's
        # throat-clearing still attached.
        "chatbot-artifact",
        re.compile(
            r"""(
              I\s+hope\s+this\s+helps
            | great\s+question
            | I'?d\s+be\s+happy\s+to
            | feel\s+free\s+to\s+reach\s+out
            | (certainly|absolutely|of\s+course)\s*!
            | is\s+there\s+anything\s+else\s+(I\s+can|you'?d)
            | let\s+me\s+know\s+if\s+you\s+have\s+any\s+(other\s+)?questions
            )""",
            re.I | re.X,
        ),
        "an assistant artifact in copy a person is supposed to have written",
        "cut the sentence; it carries no information",
    ),
    (
        # The hedge in front of a question, in the post-connect message shape:
        # thanks for connecting, an observation, "Curious what X actually...",
        # then a trailing "because" claim. The hedge does the asking for the
        # question, and the "because" answers it before the reader can.
        #
        # NARROWED on purpose. The bare phrase also appears in good copy that
        # was approved and frozen: a connection-request note sent BEFORE
        # anybody has connected ("Curious what you hope to achieve with that
        # role"). So this fires only where one of the 2 markers of the struck
        # shape sits nearby: a thanks-for-connecting opener in the same
        # paragraph, or a trailing ", because" in the same sentence. A hedge
        # with neither marker is a construction, and constructions belong to
        # a reader. See POST_ACCEPT_OPENER and HEDGE_BECAUSE below.
        "hedged-question",
        re.compile(r"\bcurious\s+(what|whether)\b", re.I),
        "a hedge in front of the question, in the post-connect shape",
        "ask the question itself, and stop at the question mark",
    ),
    (
        # A clause explaining why the message exists or what it prevents.
        # Only the exact clauses that kept recurring are caught here; a purpose
        # clause in new words is a reader's job.
        "purpose-clause",
        re.compile(
            r"""(
              so\s+nothing\s+lands\s+cold
            | so\s+nothing\s+gets\s+lost\s+between
            | so\s+you\s+have\s+something\s+to\s+post\s+on\s+its\s+own
            | so\s+it'?s\s+zero\s+work\s+for\s+you
            )""",
            re.I | re.X,
        ),
        "a clause explaining why the message exists or what it prevents",
        "delete the clause; the sentence before it already carries the content",
    ),
    (
        # Asking to be kept in mind or kept first. It positions you as the one
        # who needs them. NARROWED so it fires only when WE are the one being
        # placed (me, us, I, we): "you're first on the list for the next one"
        # is you offering them something, the opposite direction, and stays
        # legal.
        "supplicant-close",
        re.compile(
            r"""(
              keep\s+(me|us)\s+first
            | keep\s+(me|us)\s+in\s+mind
            | put\s+(me|us)\s+first
            | (me|us)\s+first\s+(on\s+the\s+list|in\s+line)
            | (I|we)\s+(would|'d)\s+(love|like)\s+to\s+be\s+first\s+(on\s+the\s+list|in\s+line)
            | tell\s+me\s+the\s+day\s+the\s+doors\s+open
            )""",
            re.I | re.X,
        ),
        "asks to be kept in mind or kept first, which puts you in the position of needing them",
        "a thank-you, or nothing",
    ),
    (
        # Flowery phrases struck by name on guest and status emails. A status
        # update says the status and one warm line, not a critique of the
        # reader's own work back at them.
        "struck-phrase",
        re.compile(
            r"""(
              spine\s+of\s+the\s+episode
            | the\s+piece\s+I\s+keep\s+thinking\s+about
            )""",
            re.I | re.X,
        ),
        "a flowery phrase that says nothing",
        "say where it stands and one warm line, nothing about their work back at them",
    ),
    (
        # A setup sentence or label standing on its own. In one sweep of 51
        # drafted messages, these were the single largest cause of rewrites.
        # Only the exact sentences are caught, and only when they stand alone.
        "setup-label",
        re.compile(
            r"""(
              (?:^|[.!?]\s+)\s*(?:
                  Quick\s+one\.
                | Two\s+things\.
                | Three\s+things\.
                | Ten\s+questions\.
                | One\s+question\s+before\s+I\s+decide\.
                | Random\s+\w+day\s+hello\.
              )
            | here'?s\s+my\s+light\s+check[\s-]?in
            )""",
            re.I | re.X,
        ),
        "a setup sentence or a label standing on its own",
        "cut it; a standalone sentence carries content or goes",
    ),
    (
        # Pointing at an ask by its number or position on a page the reader is
        # not looking at ("what's the call on decision 1?"). A label exists so
        # the READER can point at an option they are looking at; it is not a
        # handle for the writer to point at something they are not. A lettered
        # option on the same page (A, B, C) stays legal.
        "numbered-ask",
        re.compile(
            r"""(
              \b(decision|question)s?\s+(one|two|three|four|five|\d+)\b
            | \basks?\s+\d+\b
            | \bthe\s+(first|second|third|fourth)\s+(decision|question|card|item)\s+(above|below|this\s+morning|earlier)\b
            )""",
            re.I | re.X,
        ),
        "points at an ask by its number instead of saying the thing",
        "say what is true, what the ask is, and what happens if it waits",
    ),
    # ------------------------------------------------------------------
    # AND NOW YOURS. The shape of a business-specific rule, as an
    # illustration only (commented out, not live): a headline number that is
    # only defensible when its source is named. Every wording that states it
    # bare has to fail, and the wordings drift.
    #
    # (
    #     "bare-number",
    #     re.compile(
    #         r"""(
    #           \$\s?2(\.\d)?\s?M\b
    #         | 2\s?million\s+(in|of)\b
    #         )""",
    #         re.I | re.X,
    #     ),
    #     "states the headline figure with no source next to it",
    #     "name where the number comes from in the same sentence, or leave it out",
    # ),
    #
    # Other good candidates: an old handle or address that now 404s, a
    # product name you renamed, a page you retired.
    # ------------------------------------------------------------------
]


# ---------------------------------------------------------------------------
# OPTIONAL, on with --strict. Right for many businesses, wrong for some.
# ---------------------------------------------------------------------------

OPTIONAL_CLAIMS = [
    (
        # Describing your own business as new in marketing copy ("we started a
        # new company", "a new venture", "newly launched"). For an established
        # practice it takes away credibility: the reader discounts everything
        # after it. The rule is about the age of the BUSINESS, not the word
        # "new"; see ALLOW for the legitimate uses.
        "company-age",
        re.compile(
            r"""(
              start(ed|ing)?\s+(a\s+)?(new\s+)?(company|business|venture|firm|agency)
            | (new|newly)\s+(company|venture|business)
            | newly\s+(launched|founded|formed|created)
            | brand[\s-]new\s+(company|business|venture|firm|agency)
            )""",
            re.I | re.X,
        ),
        "describes the business as new, which takes away credibility",
        "describe what you focus on, not how old the business is",
    ),
]


# ---------------------------------------------------------------------------
# ADVISORY TIER. Voice, not claims. These WARN and never fail the run.
#
# Matched against the whole text with newlines folded, because mail bodies
# arrive hard-wrapped at about 76 characters and every one of these is longer
# than that. Precision over recall: each is a construction seen recurring with
# a fixed wording, not a phrase somebody disliked once.
# ---------------------------------------------------------------------------

VOICE_PATTERNS = [
    (
        "connoisseur-rating",
        re.compile(
            r"""(clearest|sharpest|smartest|bravest|best|most\s+\w+)
                [^.\n]{0,45}
                \bI\s*(have|'ve)\s+(ever\s+)?(heard|seen|read)""",
            re.I | re.X,
        ),
        "rates the thing instead of reacting to it; nobody ranks anything out loud this way",
        "say what it made you think",
    ),
    (
        "antithesis",
        re.compile(
            r"""(
              (is|are)\s+(a\s+)?(very\s+)?different\s+(animal|beast|thing)\s+from
            | it'?s\s+not\s+(about\s+)?\w[^.\n]{0,40},\s+it'?s
            | (stops|starts)\s+being\s+\w+[^.\n]{0,30}\s+and\s+starts\s+being
            )""",
            re.I | re.X,
        ),
        "a two-part contrast whose job is to sound clever; only the second half does work",
        "say the one thing and drop the contrast",
    ),
    (
        "essay-flourish",
        re.compile(
            r"""(
              in\s+a\s+way\s+(that\s+)?most\b[^.\n]{0,40}\b(never|don'?t|do\s+not|rarely)
            | something\s+(that\s+)?most\b[^.\n]{0,40}\b(skip|miss|avoid|never)
            | is\s+a\s+different\s+animal
            | is\s+where\s+(almost\s+)?(everybody|everyone|most\s+people)\s+(actually\s+)?live
            )""",
            re.I | re.X,
        ),
        "an essay construction that reads well in print and lands oddly in a short message",
        "one plain sentence, then stop",
    ),
    (
        "aphorism-closer",
        re.compile(
            r"""(
              the\s+useful\s+(move|part|thing)\s+is
            | which\s+is\s+why\s+it\s+(survives|persists|works)
            | and\s+that'?s\s+the\s+whole\s+(point|game|thing)\s*\.
            )""",
            re.I | re.X,
        ),
        "a closing clause whose only job is to sound wise",
        "cut the last clause",
    ),
]


# ---------------------------------------------------------------------------
# Context for hedged-question. Both markers are things a connection-request
# note cannot carry, which is what keeps the approved note legal.
# ---------------------------------------------------------------------------

POST_ACCEPT_OPENER = re.compile(
    r"""(
      thanks\s+for\s+(the\s+)?(connect(ing|ion)?|accept(ing)?|add)
    | thank\s+you\s+for\s+(connect(ing|ion)?|accept(ing)?)
    | (great|good|nice|lovely)\s+to\s+connect
    )""",
    re.I | re.X,
)

# ", because <claim>" still inside the same sentence as the hedge.
HEDGE_BECAUSE = re.compile(r"^[^.!?\n]{0,220}?,\s*because\b", re.I)


# ---------------------------------------------------------------------------
# THE ALLOW LIST. Keyed by rule id, matched against a window of about 40
# characters either side of the hit, so an allowed phrase in one corner of a
# long line cannot excuse a genuine offender in the other corner. "*" applies
# to every rule.
# ---------------------------------------------------------------------------

ALLOW = {
    "*": re.compile(r"copy-check:\s*allow", re.I),
    "label-intent": re.compile(
        r"""(
          not\s+quite\s+a\s+cold\s+(note|email|message)
        | not\s+a\s+cold\s+(note|email|message)
        )""",
        re.I | re.X,
    ),
    "keyword-reply": re.compile(
        r"""reply\s+(with\s+)?(your|the)\s+(availability|address|invoice|number)""",
        re.I | re.X,
    ),
    # The age of the business, not the word "new".
    "company-age": re.compile(
        r"""(
          new\s+address
        | new\s+(hire|seat|role|posting|job|client|episode|guest|name|number|page|version)
        | new\s+business\s+(intake|development|department|team|committee|group)
        )""",
        re.I | re.X,
    ),
}


def _allowed(rule_id, window):
    """True when this hit is exempted, either globally or for this rule."""
    if ALLOW["*"].search(window):
        return True
    rule_allow = ALLOW.get(rule_id)
    return bool(rule_allow and rule_allow.search(window))


def blocks_by_line(text):
    """Line number -> the blank-line-separated block (paragraph) it sits in.

    Context for hedged-question and bare-link has to be LOCAL. A long rules
    file carries "thanks for connecting" in one section and an approved
    connection note in another, and a whole-file test would refuse the note on
    the strength of a sentence 400 lines away.
    """
    lines = text.splitlines()
    out, i, n = {}, 0, len(lines)
    while i < n:
        if not lines[i].strip():
            out[i + 1] = ""
            i += 1
            continue
        j = i
        while j < n and lines[j].strip():
            j += 1
        block = "\n".join(lines[i:j])
        for k in range(i, j):
            out[k + 1] = block
        i = j
    return out


def check_text(text, strict=False):
    """Fail-tier findings. Returns a list of (rule_id, line_no, line, message, instead)."""
    rules = ALWAYS + BANNED_CLAIMS + (OPTIONAL_CLAIMS if strict else [])
    findings = []
    blocks = blocks_by_line(text)
    for line_no, line in enumerate(text.splitlines(), 1):
        if ALLOW["*"].search(line):
            continue
        block = blocks.get(line_no) or line
        for rule_id, pattern, message, instead in rules:
            if rule_id == "bare-link":
                continue  # handled below, needs line context
            for m in pattern.finditer(line):
                lo = max(0, m.start() - 40)
                hi = min(len(line), m.end() + 40)
                if _allowed(rule_id, line[lo:hi]):
                    continue
                if rule_id == "hedged-question":
                    if not POST_ACCEPT_OPENER.search(block) \
                       and not HEDGE_BECAUSE.search(line[m.end():]):
                        continue
                findings.append((rule_id, line_no, line.strip()[:160], message, instead))
        for m in bare_link_hits(line, block):
            findings.append((
                "bare-link", line_no, line.strip()[:160],
                f"\"{m.group(0)[:60]}\" has no https:// on the front, so whether it "
                f"becomes a link is up to the client and the TLD",
                "put https:// on the front of the address",
            ))
    return findings


def check_warnings(text):
    """Advisory voice findings. Same shape as check_text, never fails a run.

    Matched against the whole text with newlines folded to single spaces. A
    line-by-line first build found 2 of 5 offenders in a batch of hard-wrapped
    letters, missing the rest purely on where the wrap fell. Fold first, then
    match, then recover the line number from the character offset.
    """
    flat = re.sub(r"\s+", " ", text)
    line_starts, n = [], 0
    for ln in text.splitlines(True):
        line_starts.append(n)
        n += len(re.sub(r"\s+", " ", ln))

    def line_of(pos):
        lo = 1
        for i, start in enumerate(line_starts, 1):
            if start <= pos:
                lo = i
            else:
                break
        return lo

    found = []
    for rule_id, pattern, message, instead in VOICE_PATTERNS:
        for m in pattern.finditer(flat):
            lo = max(0, m.start() - 40)
            hi = min(len(flat), m.end() + 40)
            if _allowed(rule_id, flat[lo:hi]):
                continue
            found.append(
                (rule_id, line_of(m.start()), m.group(0).strip()[:160], message, instead)
            )
    return sorted(found, key=lambda f: f[1])


# ---------------------------------------------------------------------------
# SELF-TEST. Neutral fixtures. The second element is the rule that must catch
# the line, None when the line must come back clean. The clean cases are the
# guards against a pattern that is too greedy, and they matter as much as the
# hits: every approved template you freeze belongs in here as a None case.
# The third element, when present, is True for cases that need --strict.
# ---------------------------------------------------------------------------

SELF_TEST = [
    # always on
    ("This is the offer\u2014and it is good.", "em-dash"),
    ("This is the offer \u2013 and it is good.", "em-dash"),
    ("Pages 10\u201320 cover it.", None),
    ("Here are the examples: example.com/case-studies see you Tuesday.", "bare-link"),
    ("Book a slot here: scheduler.example.org/your-name/30min", "bare-link"),
    ("Here it is properly: https://example.com/case-studies/", None),
    ("The old note pointed at `example.com/case-studies` before today.", None),
    ("The page is at <code>example.com/case-studies</code> now.", None),
    ("<a href=\"example.com/case-studies\">the examples</a>", None),
    ("See [the examples](https://example.com/case-studies/).", None),
    ("Run python3 scripts/copy_check.py outputs/drafts/note.md first.", None),
    ("Write to hello@example.com and we will answer.", None),
    ("The site is example.com if you want to look.", None),
    ("Do not paste the old note. It offered example.net/old-page, which is now "
     "a redirect stub.", None),
    # banned claims
    ("Quick question rather than a pitch: how is the project going?", "label-intent"),
    ("This is not quite a cold note, we met at the conference.", None),
    ("Just reply YES and I will send it over.", "keyword-reply"),
    ("Reply with your availability and I will book it.", None),
    ("I hope this helps, and feel free to reach out.", "chatbot-artifact"),
    ("Thanks for connecting. Curious what the role actually covers day to day.",
     "hedged-question"),
    ("Thanks for the connect. Curious what owning all of it looks like, because "
     "most people in the seat say it arrived on top of a full job.",
     "hedged-question"),
    ("Curious whether the team has hired for this yet, because most have not.",
     "hedged-question"),
    ("Thanks for connecting. What is taking most of your week at the moment?", None),
    ("Curious what owning all of it actually looks like right now.", None),
    # an approved connection-request note: sent before anyone has connected
    ("Hi, I saw you are hiring for an operations lead. Curious what you hope to "
     "achieve with that position, and happy to share what is working.", None),
    ("I am curious about the budget for this.", None),
    ("I will send the questions on Friday so nothing lands cold on the day.",
     "purpose-clause"),
    ("I am copying you both so nothing gets lost between the two of you.",
     "purpose-clause"),
    ("We will cut it for you so you have something to post on its own.",
     "purpose-clause"),
    ("I will fill in the form so it's zero work for you.", "purpose-clause"),
    ("Keep me first on the list and tell me the day the doors open.",
     "supplicant-close"),
    ("Happy to help, just keep us in mind when the search opens.", "supplicant-close"),
    ("If a seat opens I would love to be first in line.", "supplicant-close"),
    ("You joined an earlier session, so you're first on the list for the next one.",
     None),
    ("That answer is the spine of the episode.", "struck-phrase"),
    ("Your line about pricing is the piece I keep thinking about.", "struck-phrase"),
    ("Quick one. Are you free Tuesday?", "setup-label"),
    ("Two things. The recording is done and the link goes out Friday.", "setup-label"),
    ("Random Wednesday hello. How is the week going?", "setup-label"),
    ("Hope all is well, here's my light check-in.", "setup-label"),
    ("She sent two things over on Friday and both were useful.", None),
    ("What's the call on decision 1?", "numbered-ask"),
    ("Decision one above still needs your answer.", "numbered-ask"),
    ("The second decision above is about the venue.", "numbered-ask"),
    ("A. Build it tonight. B. Paste the list yourself. C. Skip it.", None),
    ("Option C is my favourite, the lilac one.", None),
    ("We have to take a step back and ask one fundamental question first.", None),
    ("That episode landed for me, and the part about pricing stuck.", None),
    # escape hatch
    ("I hope this helps. copy-check: allow", None),
    # optional, --strict only
    ("We started a new company this summer.", "company-age", True),
    ("We started a new company this summer.", None),
    ("It is a new role for her and she starts in October.", None, True),
    ("We are focusing on the training side of the business.", None, True),
]


def self_test():
    """Prove each rule refuses what it was written for, and passes clean copy."""
    failures = []
    for case in SELF_TEST:
        text, want = case[0], case[1]
        strict = len(case) > 2 and case[2]
        got = {f[0] for f in check_text(text, strict=strict)}
        if want is None:
            if got:
                failures.append((text, "expected clean", sorted(got)))
        elif want not in got:
            failures.append((text, f"expected {want}", sorted(got) or ["nothing"]))
    for text, want, got in failures:
        print(f"FAIL  {want}, got {got}")
        print(f"      {text}")
    total = len(SELF_TEST)
    print(f"\nself-test: {total - len(failures)}/{total} cases pass")
    return 1 if failures else 0


def report(label, findings, warnings):
    if not findings:
        print(f"clean: {label}")
    else:
        print(f"\nFLAGGED: {label}")
        for rule_id, line_no, line, message, instead in findings:
            print(f"  line {line_no} [{rule_id}] {message}")
            print(f"    {line}")
            print(f"    say instead: {instead}")
    if warnings:
        print(f"\nvoice, advisory only: {label}")
        for rule_id, line_no, line, message, instead in warnings:
            print(f"  line {line_no} [{rule_id}] {message}")
            print(f"    {line}")
            print(f"    say instead: {instead}")
        print("  (these never fail the run; your ear wins over the pattern)")


def main(argv):
    args = argv[1:]
    if args and args[0] in ("--self-test", "--selftest"):
        return self_test()
    if not args or any(a in ("-h", "--help") for a in args):
        print(__doc__.strip())
        return 0
    strict = "--strict" in args
    paths = [a for a in args if a != "--strict"]

    total = 0
    for p in paths:
        if p == "-":
            text, label = sys.stdin.read(), "(stdin)"
        else:
            f = Path(p)
            if not f.is_file():
                print(f"skip, not a file: {p}")
                continue
            try:
                text, label = f.read_text(encoding="utf8", errors="replace"), p
            except OSError as err:
                print(f"skip, unreadable: {p} ({err})")
                continue
        findings = check_text(text, strict=strict)
        warnings = check_warnings(text)
        total += len(findings)
        report(label, findings, warnings)

    if total:
        print(f"\n{total} flagged. Nothing ships carrying these.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
