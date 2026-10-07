# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:** My search is a plain keyword-overlap match over title,
description, category, and style tags — it has no synonym handling, so a
phrasing like "vibey old band shirt" can score zero against a listing whose
text only ever says "graphic tee". That's a real miss mode for a query I'd
still call reasonable, which is why this isn't 5 of 5. It's 4 of 5 and not
lower because the five example queries in app.py were checked against the
data before being written down, so the only way to miss is a genuinely odd
phrasing, not a broken search.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:** Unlike criterion 1, this path isn't competing against a
fuzzy keyword match — it's one `if not results:` check in `run_agent`, which
is deterministic code with no model call and no scoring ambiguity involved.
Either `search_listings` returned an empty list and the branch fires, or it
didn't. There's no plausible source of run-to-run variance here, so anything
less than 5 of 5 would mean the branch itself is broken, not that it's
occasionally unlucky.

---

## 3. The item that reaches `suggest_outfit` is the item `search_listings` found

For 5 of 5 runs of a matching query, `session["selected_item"]["id"]` is
identical to `session["search_results"][0]["id"]`, and that same `id` appears
in the `new_item` argument the agent actually passed into `suggest_outfit` —
checked by printing both at the call site, not by reading the code and
assuming it's true.

**Why this target:** This one isn't a model call and isn't a keyword match —
it's a dict going into the session and coming back out unchanged. There's no
source of randomness between `search_listings` returning and `suggest_outfit`
being called, so anything less than 5 of 5 means the session is dropping or
replacing state, which is the exact failure mode this criterion exists to
catch.

---

## 4. The fit card is a caption, not a template, and it says what it has to say

For 5 different items run through `create_fit_card`, no two of the five
resulting captions share an opening sentence, and each of the five mentions
its own item's price and platform at least once — in at least 4 of 5 tries.

**Why this target:** 4 of 5 and not 5 of 5 because the model is free to vary
how it opens a sentence and occasionally may fold the price into a phrase my
simple string check doesn't recognize as "mentioning the price" (e.g. writing
"thirty bucks" instead of "$30"). 5 of 5 on the no-shared-opening-sentence
half would be nice but isn't the part I'm targeting strictly, since TEMPERATURE
0.9 makes two openings colliding by chance possible, if unlikely, across only
five samples.

---

## 5. An empty wardrobe never breaks the run

Given a query that matches a listing, run with `--empty-wardrobe` 5 times.
In 5 of 5 tries the agent still returns a non-empty fit card, and
`outfit_suggestion` contains general styling advice rather than an empty
string, a crash, or a reference to a wardrobe item that doesn't exist.

**Why this target:** 5 of 5 because this path has no keyword matching and no
network flakiness of its own to blame — it's one `if` check on
`wardrobe["items"]` inside `suggest_outfit`, and that condition is either
tested or it isn't. Anything less than 5 of 5 would mean the empty-wardrobe
branch is sometimes not being taken at all, which is a bug in the tool, not
variance in the model's wording.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
