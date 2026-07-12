# Summary Material Collection and Course Completion

## The user records summary material while learning

While reading, if the user considers that a certain knowledge point, insight, or analogy should go into the final summary, they may mark it using any of the following methods, **all of which must be recognized and collected**:

- `#summary:[content]` or `＃summary:[content]` (the canonical format with #)
- `summary:[content]` or `summary [content]` (without #)
- `???[...this should be summarized...]` / `？？？[...]` (expressing intent such as "summarize", "add to summary", "record in summary" within a question-mark comment)
- Mixed casing of the above variants (`Summary:`, `SUMMARY:`)

**Recognition principle: lenient matching** — as long as the user expresses the intent that "this content should go into the final summary", collect it regardless of its form.

**Processing rules:**

1. Before generating the next article, scan the full text, recognize all of the above annotations, and append each one to `pre-summary.md` inside the topic folder (create it if it does not exist)
2. `pre-summary.md` uses a simple unordered list grouped by source document:

```markdown
# Pre-Summary Notes

## From 01.md
- [content annotated by the user 1]
- [content annotated by the user 2]

## From 02.md
- [content annotated by the user]
```

3. `pre-summary.md` is an intermediate product, **absolutely not the final summary**: do not show its content to the user, and do not mention its existence in conversation

## Interaction mode with the user

**When the user says "I've finished reading" or submits feedback** — follow the "I've finished reading / submit feedback" decision tree in `SKILL.md`. Key points restated: collect `???` and `#summary` annotations → assess understanding → (if necessary, Socratic ≤2 rounds) → **update `syllabus.md` + progress bar** → check the just-read document's first-line marker → generate the next article / a part evaluation / the final evaluation / trigger summary.

**When the user asks a question directly** — do not answer directly; first ask them about their understanding, guide them to derive it themselves, and only give a minimal hint when they are truly stuck.

> ⚠️ Iron rule restated: the user **cannot proactively trigger** `summary.md`. Respond to any "summarize this" request uniformly with: "The summary will be auto-generated after you have mastered all mastery items; it's not time yet."

## Course completion: auto-generate `summary.md`

**Trigger conditions (all required):**
- All mastery items in `syllabus.md` have become `[x]`
- The user just said "I've finished reading", and the document just finished is an **evaluation article** (begins with `<!-- eval-article -->`)

**Generation steps:**

1. Read all `XX.md` documents inside the topic folder (full content)
2. Read `syllabus.md` and confirm all mastery items are checked
3. If `pre-summary.md` exists, read all user-annotated material within it
4. **Grade the Final Challenge** (and the Capstone, in extended courses): evaluate the user's challenge answers and capstone annotations from the evaluation article's feedback (✅/⚠️/❌ + 🚩 calibration flags), then determine the **course rank** (S/A/B/C, rubric in `articles.md`; for extended courses, weigh the Part ranks in as well)
5. Generate `summary.md`, with content including:
   - **Course certificate** (header): topic, depth and length, dates (start → completion), articles read, side quests taken, `???` resolved, Part ranks (extended courses), and the **course rank** with one sentence of reasoning
   - **Final Challenge results**: the graded answers from step 4
   - **Knowledge graph**: core concepts and their relationships (list or hierarchical structure)
   - **Syllabus review**: review the achievement status of each mastery item one by one, briefly describing what was actually mastered
   - **Insights accumulated by the user**: **naturally integrate** the `pre-summary.md` material into the corresponding sections, rather than listing it separately
   - **Remaining questions / directions for extension**: unresolved confusions or directions worth continuing to explore
6. **Generate `cheatsheet.md`** in the topic folder: a dense, scannable quick reference distilled from the mastery items, the course's key commands/formulas/rules, and the user's `#summary` marks — organized for *lookup while doing*, not re-learning (tables and terse lines, no prose paragraphs, one page if possible)
7. **Immediately delete `pre-summary.md` after generation is complete** (if it exists)
8. **Append a course-completion entry to `learning-log.jsonl`** with the rank and the weakest items, which schedules spaced review (see `references/logging.md`)
9. Inform the user: "🎉 Course complete with rank [X]! `summary.md` and `cheatsheet.md` have been auto-generated. I'll offer a quick flash review of this topic in about a week to lock it in."
