# The checks

> Some claims must never ship. So a script checks the copy before it goes out, rather than a longer paragraph in an instructions file.
>
> Working implementation: `scripts/copy_check.py`. Run `python3 scripts/copy_check.py --self-test` once after install to prove every rule refuses what it was written for and passes clean copy.

---

## The pattern

You write a rule. The rule is clear, correct, and sitting in a file that loads every session.

The rule gets broken anyway.

You write the rule again, more emphatically, maybe in a second file. It gets broken a third time, and this time the person catching it is your reader.

**When a rule keeps being broken with the rule in context, the fix is a script or a hook, not a longer paragraph.** Prose competes for attention with every other piece of prose. A script does not compete with anything; it just fails the run.

The threshold that works in practice: **the second time.** Once is a miss. Twice, with the rule loaded both times, means the rule is unenforceable as prose.

---

## Why prose fails here specifically

3 reasons, and the third is the one that changes how you write the check.

**1. Banned phrasings do not look like each other.** One banned claim got past 3 separate template variants. One said "started a new company", one said "moved on to a new venture", one said "started <the business name> this summer". No grep for any one of those would have caught the other 2. 17 letters went out before anybody noticed, and the person who noticed was the recipient's side of the table.

**2. The offending phrase is the kind of thing that gets typed without being noticed.** A rule was written in 2 separate rules files, in plain language, and 5 drafts still carried the exact phrase it banned. The reviewer cut it by hand from every one. Nobody had failed to read the rule. The phrase is just a reflex, which is precisely what a regex is for.

**3. A rule learned in one place does not travel.** A voice ruling landed against 2 messages on one channel, went into the rules file for that channel, and never reached the email templates. The identical voice problem shipped again 5 days later inside copy that was supposed to be frozen. A checker that runs on every outgoing file does not care which channel taught it the rule.

---

## The tiers, and keeping them separate is the point

**Form rules are always on and fail the run.** Mechanical, with no defenders: em dashes, and a link meant to be clicked with no `https://` on the front.

**Banned claims fail the run.** Something factually or strategically wrong, or a phrase somebody has struck by name more than once. It does not ship, full stop, and the exit code says so.

**Optional claims fail the run only with `--strict`.** Rules that are right for many businesses and wrong for some, so you opt in.

**Voice patterns warn and never fail the run.** Constructions that usually read as machine-written. A human ear outranks the pattern every time, and a check that blocks on taste will be disabled within a week.

Mixing them is how a useful checker becomes an ignored one. If the tool cries wolf on register, nobody reads it when it catches a real claim.

---

## A starting check list

Steal what fits. All of these ship in `copy_check.py`; delete the rows you disagree with. **A check you do not agree with is a check you will route around**, and a routed-around check is worse than none because it creates false confidence.

### Shipped on, for everybody

The first 2 rows are the always-on form rules. The rest ship in the editable `BANNED_CLAIMS` table: each is a phrase or shape that has been struck by hand, by name, more than once in real drafts.

| Check | Why |
|---|---|
| **Em dashes** | The single most reliable tell of machine-written prose. A comma or a full stop does the job. Not editable in `copy_check.py`, on purpose |
| **A bare link** (`host/path` with no `https://`) | Messaging clients decide for themselves whether a bare address becomes a link, and they decide differently by top-level domain. In one measured case the same client linkified a bare address on one domain and left another as plain text, and dozens of people got a correct address that did nothing when tapped. The scheme is the only form that always links. Exempt: a bare domain with no path, anything in backticks or `<code>`, href and src values, markdown link targets, file paths. Always on |
| **Chatbot artifacts** | "I hope this helps", "Great question", "Certainly", "Would you like me to", "Feel free to reach out". A person writing to another person never types these |
| **Labelling the message's own intent** | "No pitch", "not trying to sell you", "this isn't a sales email". If a message is not a pitch, it shows. Labelling it makes it read like one |
| **Reducing a question to a keyword reply** | "Just reply YES", "hit reply with A or B", "just say the word". That is a machine asking for structured input, not a person asking a question. Ask the actual question and let them answer however they answer |
| **A hedge in front of a question, in the post-connect shape** | "Thanks for connecting. Curious what X actually...", often with a trailing "because" clause that answers the question before the reader can. Fires only when one of those 2 markers is present, so an approved connection-request note ("Curious what you hope to achieve with that role") stays legal |
| **Purpose clauses** | "so nothing lands cold", "so nothing gets lost between the two of you", "so it's zero work for you". A clause explaining why the message exists says nothing |
| **Supplicant closes** | "keep me in mind", "keep us first", "tell me the day the doors open". It puts you in the position of needing them. Fires only when you are the one being placed, so "you're first on the list for the next one" stays legal |
| **Setup sentences and labels** | "Quick one.", "Two things.", "here's my light check-in". A standalone sentence carries content or goes. In one sweep of 51 drafts these were the largest single cause of rewrites |
| **Flowery phrases struck by name** | "spine of the episode", "the piece I keep thinking about". A status update says the status and one warm line |
| **Pointing at an ask by its number** | "What's the call on decision 1?" A label exists so the reader can point at something they are looking at. In a message, say the thing: what is true, what the ask is, what happens if it waits. Lettered options on a page stay legal |

### Yours to write, and the ones worth thinking about

- **Any claim about your business that must never appear.** One that ships as an optional rule (`--strict`): the business is never described as new in marketing copy, because that hands the reader a reason to discount everything after it. Yours will be different and you will know it the first time somebody says the wrong thing out loud.
- **An old handle, address or page that now 404s or redirects.** It comes back from memory, not from a template. Ban the exact string the day you retire it.
- **Any number that must carry its source.** If a revenue figure, a case-study result or a statistic ships bare, the check flags it and the copy either names the receipt or drops the number.
- **Any promise stated in a shape you have ruled out.** Ours was a promise written as the sum of its components, which overstated one part and understated the whole. If a shape has been ruled wrong once in a meeting, write the regex that day.
- **A phrase somebody keeps cutting by hand.** The clearest signal there is. If a reviewer has deleted the same phrase from 3 drafts, that is a check, not a conversation.

### Voice patterns, advisory only

These 4 machine constructions recur across letters and posts, and naming them is most of the fix:

- **The antithesis.** "A thing built this way is a different animal from a thing built that way." Say the one thing and drop the contrast.
- **The connoisseur's rating.** "The clearest example I have heard of", "the most honest answer I have heard to". Nobody rates a thing out loud this way.
- **The aphorism closer.** A final clause whose job is to sound wise: "and that is where almost everybody actually lives", "which is why it survives so long".
- **The essay verb.** An episode "cites", "draws the line", "insists", "touches on something most conversations skip". An episode says things.

---

## How to write a check that survives

**Precision over recall.** Every pattern should be a construction that has actually recurred, not a phrase somebody used once. A false positive costs a glance; but 10 false positives cost you the checker, because people stop reading its output.

**Fold newlines before matching the voice tier.** Mail bodies arrive hard-wrapped at around 76 characters, which splits most of these constructions across a line break. One build of a voice tier caught 2 of 5 real offenders and missed the rest purely on the wrap. Match against the flattened text and recover the line number from the character offset.

**Ship an allow list.** Every rule has legitimate exceptions, and a member needs somewhere to put them that is not "edit the regex and hope".

**Look at a window around the hit, not the whole line.** Otherwise an allowed phrase at the start of a paragraph excuses a genuine violation at the end of it.

**A template you approved and froze must exit 0.** When a first build of a rule refuses your own approved copy, the rule is wrong, not the copy. Narrow the pattern to the direction and the shape that was actually struck (one hedge rule was narrowed to fire only beside a thanks-for-connecting opener or a trailing "because"; one close rule was narrowed to fire only when "me" or "us" is the one being placed), then add the approved line to the self-test as a case that must come back clean.

**Every rule gets self-test cases in both directions.** The lines it must catch, and the nearby lines it must leave alone. The clean cases are the guard against a pattern that grows greedy, and they are what lets you change a regex without fear.

**A script owns phrases, a reader owns constructions.** The antithesis, the connoisseur's rating and the purpose clause in new words are shapes, and a regex that tried to catch them all would fire on good sentences. Those go to a person or a voice-check agent that reads your writing rules at run time. The script refuses what somebody wrote down word for word.

**A frequency problem is not a ban.** A reaction phrase that is fine once and tiring in 36 letters out of 97 needs a batch check (no single phrase in more than about 1 letter in 8), not a ban. Banning it pushed everybody to one replacement phrase, which then carried 36 of 97 letters too. A checker that reads one file at a time can never see a batch.

**A rule file will flag itself**, because it quotes the banned phrases in order to ban them. That is correct and expected. **Run the checker on the copy that ships, never on the documents that describe the copy, and never rewrite a rule to satisfy the checker.**

---

## Where the check runs

3 places, in increasing order of how much you trust yourself:

1. **By hand, before something ships.** `python3 scripts/copy_check.py draft.md`. Zero setup, and it works the day you install the pack.
2. **In the skill.** Any skill that produces copy runs the check before calling a draft final. One line in the SKILL.md.
3. **As a hook.** Fires automatically on write or on commit, so nothing gets past it even on the day somebody is rushing. This is the one that actually holds, and it is the one worth setting up once the rule list has settled.

---

## When a check is the wrong answer

Be honest about the limit. A checker catches a **string**. It cannot catch a piece that is technically clean and still says nothing, a number that is sourced and wrong, or a draft in somebody else's voice.

Those are taste problems, and taste lives in files that a person wrote and a person maintains. See `content/reference/taste-system.md`. **A check enforces what has already been decided. It never decides anything.**
