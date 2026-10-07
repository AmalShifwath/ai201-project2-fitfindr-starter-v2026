# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

A user types a plain-language request — "a vintage graphic tee under $30,
size M" — and FitFindr searches the listings data for matches, picks the
best one, works out what it would go with given the user's wardrobe (or
general styling advice if they haven't entered one), and writes a short
caption they could actually post about the find. If nothing in the data
matches the request, the agent stops after the search and tells the user
what to change, instead of asking the model to style and caption an item
that doesn't exist.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Filters the listings data by price and size, scores what's
  left by keyword overlap with the description, and returns the matches
  ranked best-first.
- **Inputs:** `description` (str) — keywords describing what the user wants.
  `size` (str or None) — a size token to match; None skips size filtering.
  `max_price` (float or None) — inclusive price ceiling; None skips price
  filtering.
- **Returns:** A list of listing dicts, best match first, each with
  `id`, `title`, `description`, `category`, `style_tags` (list), `size`,
  `condition`, `price` (float), `colors` (list), `brand` (str or None),
  `platform`. At most `config.SEARCH_RESULT_LIMIT` of them.
- **When it has nothing:** Returns `[]` — an empty list, never `None`, never
  an exception.

### `suggest_outfit`

- **What it does:** Asks the model for one or two outfit ideas combining a
  new item with the user's existing wardrobe.
- **Inputs:** `new_item` (dict) — a listing dict, the item being considered.
  `wardrobe` (dict) — a wardrobe dict with an `items` key holding a list of
  wardrobe item dicts; the list may be empty.
- **Returns:** A non-empty string of outfit suggestions from the model.
- **When it has nothing:** When `wardrobe["items"]` is empty, returns general
  styling advice for the new item (what *kind* of pieces would pair with it)
  rather than naming specific pieces from a closet that doesn't exist.

### `create_fit_card`

- **What it does:** Writes a two-to-four sentence caption someone would
  actually post about the thrifted item, built from the outfit suggestion.
- **Inputs:** `outfit` (str) — the string `suggest_outfit` returned.
  `new_item` (dict) — the listing dict for the item.
- **Returns:** A string caption that mentions the item, its price, and its
  platform once each.
- **When it has nothing:** If `outfit` is empty or whitespace-only, returns a
  descriptive string naming the item and saying no caption could be written,
  rather than calling the model or raising.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in
`session["error"]` naming what the user could change (price ceiling, size
filter, keywords) and stop — do not call `suggest_outfit`. Otherwise, take
the first result as `session["selected_item"]` and continue to
`suggest_outfit` and then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex. `parse_query()` in `agent.py` pulls a
price ceiling out of patterns like "under $30" / "below 40" / "up to $50",
and a size out of "size X", then strips both matched spans out of the
original query and treats what's left as the search description. This is
enough for every query in `app.py`'s `EXAMPLE_QUERIES`, and it costs zero
model calls to parse one query.

**What moves through the session:** `query` → `parsed` (from `parse_query`) →
`search_results` (from `search_listings`) → `selected_item` (first of
`search_results`) → `outfit_suggestion` (from `suggest_outfit`, given
`selected_item` and `wardrobe`) → `fit_card` (from `create_fit_card`, given
`outfit_suggestion` and `selected_item`). `error` is set only on the
empty-search branch, and every field after `search_results` stays `None` when
it fires.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

> This container has no `GEMINI_API_KEY` configured, so the live model calls
> (`suggest_outfit`, `create_fit_card`) can't run here. The run below shows
> the real `ModelUnavailable` path — search and the branch logic ran for
> real; the model call failed because there's no key, exactly like unit 4
> Milestone 2 asks you to trigger on purpose. Once a real key is in `.env`,
> re-run this and replace the output below with the real fit card.

```
$ python app.py ask 'vintage graphic tee under $30'

  ModelUnavailable: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.
0 model calls this session
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'price': 18.0, 'size': 'S/M', ...},
 {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'price': 24.0, 'size': 'L', ...},
 {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'price': 15.0, 'size': 'S/M', ...},
 {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'price': 19.0, 'size': 'L', ...},
 {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'price': 27.0, 'size': 'W29', ...},
 {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'price': 26.0, 'size': 'L', ...}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

  <needs a real GEMINI_API_KEY to run — paste the real output here once you have one>
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

  <needs a real GEMINI_API_KEY to run — paste the real output here once you have one>
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* Help implementing `search_listings`'s size matching,
  given the starter's warning that `"s" in "us 9"` and `"l" in "xl"` are both
  `True`.
- *What came back:* A tokenizer (`re.findall(r"[a-z0-9]+|...")`) that splits
  both the user's size and the listing's size string into whole tokens and
  checks for a shared token, instead of a substring check.
- *What I changed:* Verified it against the actual data (`python app.py
  listings --full -n 6` and the full size list in `data/listings.json`) —
  sizes like `"XL (oversized)"` and `"US 9"` tokenize into `{"xl",
  "oversized"}` and `{"us", "9"}`, so `"L"` correctly does *not* match
  `"XL (oversized)"` while `"M"` correctly does match `"S/M"`. Ran
  `search_listings('graphic tee', size='M', max_price=30)` and
  `search_listings(..., size='L', ...)` side by side to confirm they return
  different result sets before trusting it.

**Moment 2**

- *What I asked for:* A sanity check on the first draft of criterion 4 (the
  fit-card criterion), which originally just said "the fit card reads
  naturally and isn't a generic template."
- *What came back:* A pointed question back — could someone test "reads
  naturally" from that sentence alone without asking what I meant? No.
  "Template" also wasn't defined.
- *What I changed:* Rewrote it to two checkable things: no shared opening
  sentence across 5 different items, and price + platform mentioned in at
  least 4 of 5 captions — both are things you can check from the text alone,
  without asking me what I meant by "natural."

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
