# The three-critic loop, a pilot

A pilot for 1 page that is worth the tokens, not a step every build runs. A public run of the same
method by a design creator cost 2 to 3 million tokens, so pick the page on purpose.

```
Goal: rebuild one page against a bar file.
Bar: 5 to 7 visible mechanisms written from a page the creator already approved.
Critics, each with fresh context, judging screenshots only, pass or fail:
  brief critic:  does the page do what its one sentence says
  system critic: does it follow core.json, RULINGS.md and finish.md
  craft critic:  ours beside the reference, labels stripped, which is better,
                 the single biggest gap
Stop when all 3 pass, or when the creator stops it. Log the rounds and the gaps,
never a self-reported token count. The craft critic runs on your strongest model.
```

## How a session runs it

1. Pick the page and write its 4-line brief (SKILL.md, BUILD step 0). Write the bar file first: 5
   to 7 mechanisms a person can see on the page the creator approved, each a check, never an
   adjective.
2. Build, run the finish pass (`references/finish.md`) and the page check
   (`scripts/page_check.py`) until it passes.
3. Each round, 3 sub-agents with fresh context get the screenshots the page check wrote (1440 and
   390, first screen and full page) and their own one question, never the code. The craft critic
   runs on your strongest model, because it is the critical check.
4. Each answers pass or fail and names the single biggest gap. Fix the gaps in one batch, render
   again, next round.
5. Stop when all 3 pass in the same round, or when the creator stops it.
6. Log each round beside the page: the round, each critic's verdict and gap, what changed, the
   clock time.

Untested as a routine step. The first run says how many rounds it took and what the craft critic
caught that the page check did not.
