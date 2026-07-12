# Learner Notes (per-course preference fitting)

Preference fitting makes tutoring fit **the learner**, not just the material — the actual 2-sigma lever. All learner preferences are **per-course**: they live in a `## Learner Notes` section inside that course's `syllabus.md`. There is **no global profile file** — courses are independent, and each one's context stays self-contained.

## When to interview

- **Every new topic**: run **one** short preference round before generating anything — at most 4 questions, then in the **same turn** generate `syllabus.md` (with the answers captured in Learner Notes) + `01.md`.
- The interview asks about **preferences and background only — never content diagnostics** (no "what do you know about X" quizzes; the `01.md` feedback loop handles that).
- If the user's request already answers a question (e.g. "extended course", a stated goal), don't re-ask it — only ask what's genuinely unknown, and skip the round entirely if nothing is.

## Interview questions (pick at most 4, adapt wording to the topic)

1. **Goal** — why this topic; what should you be able to *do* afterwards?
2. **Background** — related fields/tools/experience relevant to *this topic* (feeds crossover bridging)
3. **Style** — analogies-first or formal-first? How much hands-on (🎯 micro-quest density)? Side quests: freely / sparingly / never?
4. **Scope** — depth (simple/standard/deep) and length (standard/extended), if not already stated

## `## Learner Notes` format (inside the course's `syllabus.md`)

```markdown
## Learner Notes

- Goal: [what the user wants from this course, in their words]
- Background: [relevant prior knowledge/tools, for crossover bridging]
- Style: [analogies-first / formal-first / mixed] · hands-on [high / medium / low] · side quests [freely / sparingly / never]
- Observed: [YYYY-MM-DD] [dated one-liners appended during learning]
```

## Silent refinement rules

- During each bridging phase, if feedback / `???` / 🚩 flags reveal a pattern **repeated across ≥2 articles**, append one dated line to "Learner Notes → Observed"
- Change the Style line only on clear evidence, and never override an explicit user statement
- Apply the notes in article design (framing, example choice, micro-quest density, side-quest offers) **without announcing it** — the fit should be felt, not narrated
- User asks why content looks the way it does → then it's fine to show the notes
