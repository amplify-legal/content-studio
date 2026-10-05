#!/usr/bin/env python3
"""
first_taste_check.py, the check at the end of the 20 minute path.

WHAT THIS IS FOR

The first thing you make with this pack is a taste file: 3 pieces by other
people that stopped you, your own words on why each one worked, and the rule
the 3 of them point at. SETUP's first section walks you through it.

That sitting can go wrong in 4 quiet ways, and all 4 look like success while
you are in the conversation:

  1. It interviewed you for 15 minutes and wrote nothing to disk.
  2. It wrote a file with your 3 examples missing or merged into prose.
  3. It paraphrased you instead of quoting you. A voice file written in
     somebody else's prose describes your voice rather than holding it.
  4. It pasted the blank template and left the square brackets in.

None of those raise an error. You find out weeks later when a draft comes
back sounding like a competent stranger, and by then you have stopped
opening the file.

So the file gets a check, and the check runs before you close the laptop.

WHAT IT CHECKS

  exists      the file is there and has something in it
  examples    3 or more separate entries
  your words  3 or more passages in quotation marks, one per example
  the rule    a section naming what the 3 have in common, with something
              written under it
  filled in   no unfilled [SQUARE BRACKETS] left over from the template

The first 4 must pass. The last one warns.

USAGE

    python3 scripts/first_taste_check.py content/taste/hooks.md

Exit 0 when the file is real, 1 when something on it needs another 5
minutes. Standard library only, so it runs anywhere python3 runs with
nothing installed.

IT IS A FLOOR, NOT A JUDGE

It counts structure. It cannot tell whether the rule you found is a good
one. Reading the file yourself is still the real check, and this exists so
that you are reading a file that is actually there.
"""

import re
import sys
from pathlib import Path

MIN_EXAMPLES = 3
MIN_QUOTES = 3
MIN_QUOTE_CHARS = 12

# An entry is a numbered item, a bullet, or its own sub-heading. The interview
# is free to shape the file any of those 3 ways, so all 3 count.
ENTRY = re.compile(r"^\s{0,3}(?:\d+[.)]\s+|[-*+]\s+|#{3,6}\s+)\S")

# Straight quotes and curly quotes both count as the operator's own words.
# Matched against the whole file rather than line by line, because a real
# verbatim quote wraps over 2 or 3 lines and a per-line scan finds none of
# them. Capped at 400 characters so one stray quotation mark cannot swallow
# the rest of the file and report itself as a quote.
QUOTED = re.compile(r"[\"“]([^\"“”]{%d,400})[\"”]" % MIN_QUOTE_CHARS)

RULE_HEADING = re.compile(r"^#{1,6}\s+.*\b(rule|rules|pattern|patterns|common|why)\b", re.I)

# [like this], but not a markdown link [like this](http...) and not a task box.
PLACEHOLDER = re.compile(r"\[([^\]\n]{4,})\](?!\()")

# The same thing, but allowed to wrap over lines, for blanking a section out.
PLACEHOLDER_SPAN = re.compile(r"\[[^\[\]]{4,}\](?!\()", re.S)


def load(path: Path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except IsADirectoryError:
        return None
    except OSError:
        return None


def count_quotes(text):
    # Quotation marks only, over the whole file. A blockquote line does not
    # count on its own, because every file in this pack opens with one
    # explaining what it is.
    return len(QUOTED.findall(text))


def blank_placeholders(text):
    """Blank out [unfilled template brackets], including ones that wrap.

    A placeholder is often 2 or 3 lines long in the templates, so a line by
    line test sees an ordinary sentence and calls the section written. Blanking
    the whole span first is what makes an unfilled section read as empty, which
    is what it is. Markdown links are left alone.
    """
    return PLACEHOLDER_SPAN.sub(lambda m: " " * len(m.group(0)), text)


def rule_section_has_content(lines):
    for i, line in enumerate(lines):
        if not RULE_HEADING.match(line):
            continue
        for follower in lines[i + 1:]:
            if follower.startswith("#"):
                break
            body = follower.strip()
            if not body:
                continue
            if PLACEHOLDER.fullmatch(body):
                continue
            return True
    return False


def report(ok, label, detail):
    mark = "PASS" if ok else "MISSING"
    print("  %-8s %-12s %s" % (mark, label, detail))


def main(argv):
    if len(argv) != 2:
        print("Usage: python3 scripts/first_taste_check.py <path to your taste file>")
        print("Most likely: python3 scripts/first_taste_check.py content/taste/hooks.md")
        return 1

    path = Path(argv[1]).expanduser()
    print("Checking %s" % path)
    print("")

    # A folder and a missing file are not the same problem, and the advice for
    # one is wrong for the other. Tab completion stops at the folder, so this
    # is the likeliest way the path comes out wrong.
    if path.is_dir():
        report(False, "exists", "that is a folder, not a file")
        print("")
        guess = path / "hooks.md"
        print("Point it at the file inside the folder:")
        print("")
        print("  python3 scripts/first_taste_check.py %s" % guess)
        print("")
        if guess.exists():
            print("That file is there, so this is only the path being short.")
        else:
            print("Nothing called hooks.md is in there yet. If the interview has")
            print("happened, go back to that same conversation and say: \"write what")
            print("I have told you so far into %s now, before anything else\"." % guess)
        return 1

    text = load(path)
    if text is None or not text.strip():
        report(False, "exists", "nothing is there, or the file is empty")
        print("")
        print("The interview did not write to disk. Go back to that same")
        print("conversation and say, in these words:")
        print("")
        print('  "write what I have told you so far into')
        print('   %s now, before anything else"' % path)
        print("")
        print("Everything you said is still in the conversation. Nothing is lost")
        print("unless you close it.")
        return 1

    lines = text.splitlines()
    entries = sum(1 for line in lines if ENTRY.match(line))
    quotes = count_quotes(text)
    has_rule = rule_section_has_content(blank_placeholders(text).splitlines())
    placeholders = [
        m.group(1) for line in lines for m in PLACEHOLDER.finditer(line)
        if not line.lstrip().startswith(("|", ">"))
    ]

    report(True, "exists", "%d lines" % len(lines))
    report(entries >= MIN_EXAMPLES, "examples", "%d found, %d wanted" % (entries, MIN_EXAMPLES))
    report(quotes >= MIN_QUOTES, "your words", "%d quoted passages, %d wanted" % (quotes, MIN_QUOTES))
    report(has_rule, "the rule", "a section naming what the 3 have in common")

    print("")
    failures = []
    if entries < MIN_EXAMPLES:
        failures.append(
            "Fewer than %d separate examples. Say: \"break that back out into\n"
            "  one entry per piece, %d of them, each with its own line\"." % (MIN_EXAMPLES, MIN_EXAMPLES)
        )
    if quotes < MIN_QUOTES:
        failures.append(
            "Your own words are not in there. It summarised you instead of\n"
            "  quoting you, which is the failure that makes the file useless\n"
            "  later. Say: \"go back through what I actually said and put my\n"
            "  sentences in as quotes, one per example, not your summary\"."
        )
    if not has_rule:
        failures.append(
            "No rule. The 3 examples are the evidence and the rule is the\n"
            "  point. Say: \"what do my 3 have in common, ask me until we have\n"
            "  1 rule I agree with, then write it into the file\"."
        )

    if placeholders:
        shown = ", ".join("[%s]" % p for p in placeholders[:3])
        word = "placeholder" if len(placeholders) == 1 else "placeholders"
        print("Warning: %d unfilled %s left in, such as %s" % (len(placeholders), word, shown))
        print("  The blank template got pasted and not filled in. Either answer")
        print("  those, or say \"delete the sections I have not answered, an empty")
        print("  file is honest and a half-filled one is not\".")
        print("")

    if failures:
        word = "thing" if len(failures) == 1 else "things"
        print("Not finished. %d %s to fix, about 5 minutes:" % (len(failures), word))
        for f in failures:
            print("- %s" % f)
        print("")
        print("Reopen the same conversation. Do not start a new one, because the")
        print("answers it needs are in that one.")
        return 1

    print("This is a real taste file. Open it and read it:")
    print("")
    print("  open %s" % path)
    print("")
    print("If you do not recognise yourself in it, that is worth saying out loud")
    print("in the same conversation. It is the only correction that gets harder")
    print("to make later.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
