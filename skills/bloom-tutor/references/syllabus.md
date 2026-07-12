# Course Syllabus `syllabus.md` Rules

**Core philosophy: learning objectives are fixed, the learning path is flexible.**

- The syllabus specifies **what you will be able to do after completing this course**, not "what article 01 covers, what article 02 covers"
- There is no limit on the number of documents — some people finish in 4 articles, others need 10; it depends entirely on the starting point and pace
- Every learning outcome in the syllabus is a specific, verifiable ability, not a vague "be aware of / understand"
- The syllabus has **two independent, user-pickable axes**:
  - **Depth** — **simple**, **standard**, **deep** (how deep each module goes). Default: **standard**.
  - **Length** — **standard** (3-5 modules, one final evaluation) or **extended** (~12-20 modules grouped into **Parts**, a part-evaluation "mid-boss" after each Part, then the final evaluation). Default: **standard**. Pick extended when the user says "marathon course", "extended course", or asks for a long/comprehensive course.
- **Source-grounded courses**: derive modules from what the corpus in `sources.md` covers; "Out of Scope" must name relevant areas the corpus lacks (see `references/sources.md`)

## Format

```markdown
# [Topic name] · Course Syllabus

> This syllabus defines all the abilities you will master after completing this topic.
> Learning depth: [simple / standard / deep] · Course length: [standard / extended]
> The number of documents varies from person to person, but the mastered content is not compromised.

**Progress:** `░░░░░░░░░░` 0/[total] mastery items

## Learner Notes

- Goal: [what the user wants from this course, in their words]
- Background: [relevant prior knowledge/tools, for crossover bridging]
- Style: [analogies-first / formal-first / mixed] · hands-on [high / medium / low] · side quests [freely / sparingly / never]
- Observed: [dated one-liners appended during learning]

## Core Mastery Items

After completing this topic, you will be able to:

### [Module one name]
- [ ] [Specific ability description, using the "be able to……" sentence form, verifiable]
- [ ] [Specific ability description]

### [Module two name]
- [ ] [Specific ability description]
- [ ] [Specific ability description]

(Grouped by knowledge module, each item represented with a checkbox, to be checked off after learning)

(**Extended courses only**: group the modules under `## Part N · [Part name]` headings, 3-5 modules per Part, ordered so each Part builds on the previous ones; standard courses omit Part headings entirely)

## Out of Scope for This Topic

- [Explicitly list which related topics this course does not cover, to avoid mismatched expectations]

## Learning Progress

| Document | Mastery items covered | Generation date |
|------|-----------|---------|
| (Automatically append a row after each new document is generated) |
```

## Requirements for Generating the Syllabus

1. All mastery items must be **verifiable behaviors** (able to explain, able to derive, able to apply, able to judge); writing unverifiable statements like "be aware of X" or "be familiar with Y" is prohibited
2. Learning depth determines the scope of each module's expansion (counts below are for **standard length**):
   - **Simple**: 2-3 modules, 8-10 mastery items; focus on the main thread, the minimum necessary concepts, and high-frequency applications
   - **Standard**: 3-4 modules, 10-12 mastery items; cover core concepts, key reasoning, typical applications, and common misconceptions
   - **Deep**: 4-5 modules, 12-15 mastery items; add first principles, underlying mechanisms, boundary conditions, counterexamples, and transfer judgment
   - **Extended length**: 12-20 modules total, grouped into 4-6 Parts of 3-5 modules each; per-module item density follows the chosen depth (roughly 35-60 mastery items total). Each Part must be a coherent sub-arc with its own narrative (foundations → mechanisms → applications → frontiers is a typical shape).
3. Modules must be organized according to the intrinsic logic of the knowledge; standard courses must not exceed 5 modules, extended courses must not exceed 5 modules per Part
4. **"Out of Scope for This Topic" must be filled in**, to help the user establish clear boundary expectations

## Linkage Between the Syllabus and Documents

- **Before** each new document is generated, check which mastery items in the syllabus have not yet been covered, to ensure the overall progress does not veer off course; each article's content should map to at least one mastery item in the syllabus, and no content unrelated to the syllabus should be generated
- **After** each new document is generated, this file must be updated immediately:
  1. Change the `[ ]` corresponding to the mastery items covered by this article to `[x]`
  2. **Update the progress bar**: `▓` for each mastered item's share, `░` for the rest, over 10 characters, plus the `N/total` count (e.g. `▓▓▓░░░░░░░ 7/24`)
  3. Append a row to the "## Learning Progress" table: document number, mastery items covered (briefly listed), generation date
- Side quests (`sq-XX.md`) do **not** check items, do **not** move the progress bar, and are **not** added to the progress table
- **Extended courses**: when all of the current Part's items have become `[x]`, generate a **part evaluation article** (`<!-- part-eval -->`, see `articles.md`) before starting the next Part
- When all mastery items have become `[x]`, **do not directly generate `summary.md`**; instead, first generate the "evaluation article" (see `articles.md`)
