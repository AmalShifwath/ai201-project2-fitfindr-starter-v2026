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

**Why this target:** My search is a plain keyword match with no plural handling, and two of the three tools call a model that can be rate limited or unreachable, so I allow one miss.
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:** The empty branch is a plain 'if' statement on a list and model call is involved, so the same impossible query should behave identically every time.
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->

---

## 3. Something about state

<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->


  
On a query that matches at least one listing, session["selected_item"]["id"] equals the id of session["search_results"][0], and the item passed into suggest_outfit has that same id, in 5 of 5 tries.  

**Why this target:** This is plain Python with no model involved. The same query gives the same search results every time, so there’s no reason for it to ever fail. A 4 of 5 target would be too easy. If it misses even once, my loop is dropping or replacing the item somewhere.



---

## 4. Something about the fit card

<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->


  
Across 5 runs of the same matching query with caching off, all 5 fit cards contain the item’s price and platform name, at least 4 of 5 are two to four sentences long, and no two of the 5 are word-for-word identical.  

**Why this target:** The price and platform are in the prompt, so leaving them out means my prompt is weak, which is why 5 of 5. Sentence count depends on the model following instructions, so I allow one miss (4 of 5). “Not identical” checks that temperature is working. Two cards can differ by one word and still pass, so this guards against caching or TEMPERATURE = 0 rather than proving the cards are good.



---

## 5. Your choice - The price request is acknowledged and the parsed price of the results is correct.

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->


  
For 5 different queries that each include a price limit (such as “under `$`20”, “`$`35 or less”), session["parsed"]["max_price"] equals the number typed, and every listing in session["search_results"] costs that amount or less, in 5 of 5 queries.  

**Why this target:** One of the main concerns of a thrift shoppers is their budget, if not the most primary reason. My regex and the filter in search_listings are both deterministic, so 5 of 5 is fair. The risk is parsing phrasings like “under 30 bucks” or “less than thirty dollars”, which my regex may miss. If it does, I’ve found a real gap to diagnose in unit 4, not a reason to lower the target. 



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
