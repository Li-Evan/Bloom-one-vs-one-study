---
name: learn-deep
description: The default in-depth entry point for whenever a user learns any new concept / new technology / new theory — it explains the concept thoroughly through five lenses in one pass and helps them choose a direction to go deeper: crossover leverages what they already know, occam frames how deep they should learn, graph builds a knowledge map, prototype iterates on a minimal prototype, feynman interrogates and tests. Trigger scenarios: I want to learn X, understand X, what is X, tell me about X, get a grip on X, learn a bit of X, go deep on X, walk me through X. Unless the user explicitly wants only one lens (in which case switch to the corresponding single learn-* skill).
---

# Learn a concept in depth (learn-deep)

> Orchestrates the five lenses `learn-crossover` / `learn-occam` / `learn-graph` / `learn-prototype` / `learn-feynman` into a single panoramic pass, giving the user a "one sweep through + pick a direction" for learning any concept.

## When to use

When the user says "I want to learn / understand / get a grip on / tell me about a concept X" — **this is the default entry point**: run all five lenses in one pass, then let the user choose which to go deeper on.
**Exception**: the user explicitly wants only one angle ("explain it with a crossover", "help me build a map", "quiz me") → use the corresponding single `learn-*` skill directly, don't run them all.

## Before starting

**First, ask about the user's background**: which related fields they've studied, what they've built, which tools / theories they're familiar with. crossover / occam / graph all rely on this later. Only accept what the user has personally confirmed they've learned.

## Execution order of the five lenses (this arc flows best: first lower the barrier → set the depth → provide a map → get hands-on → verify mastery)

### 1️⃣ crossover — first lower the barrier with "you already know half of it"
Grab the essential structure of X (strip the jargon), and following the three conjectures point out the meta-knowledge: 🎁 already learned it / 🔗 structurally isomorphic (field-level correspondence table) / 🧩 explainable with existing knowledge. **First build confidence, then talk about going deeper.**

### 2️⃣ occam — frame "how deep should you learn"
Pin down the "given problem" (what does learning X solve), whether existing knowledge is enough, X's rate of depreciation and ROI, and give a **depth boundary**: "stop once it's good enough / only learn the minimal piece / worth deep digging". This isn't about talking them out of it, it's to prevent over-drilling right from the start.

### 3️⃣ graph — provide a map so they know where X sits and when they've learned enough
The skeleton of X's knowledge graph within its field (concepts/uses/parent-child nodes), marking the highest-reuse-value nodes + the entry points reachable from common sense, and give a learning path. **Guide the user to fill in nodes** (you only learn it by building the map yourself).

### 4️⃣ prototype — provide a minimal-prototype starting point and pass the hands-on ball to the user
Give a "trashiest-but-it-runs prototype" starting point + guiding questions (let the user discover the flaws themselves), and forewarn the pitfalls they'll hit. **Don't do it for them.**

### 5️⃣ feynman — throw out 2–4 questions that hit the blind spots to verify mastery
Have the user answer in their own words; the spots where the answer doesn't flow = the gaps where they don't truly understand. Aim the last question at X's fundamental limitations (the touchstone of true understanding).

### 6️⃣ Wrap-up: pick a direction
**Explicitly recommend which 1–2 directions to go deeper on** (combining occam's ROI judgment + the user's goals + which lens struck them most), and point out which single skill to hand off to next (want to get hands-on → `learn-prototype`, want to verify mastery → `learn-feynman`).

## Notes

> ⚠️ **Iron rule · only use confirmed prior knowledge**: judging "what the user already knows" may only draw on knowledge they have **confirmed they've learned** (personally confirmed or reliable background); it is **strictly forbidden** to treat "the material currently being explained / the article author's background / other people's knowledge in the conversation" as something the user knows. When unsure → just ask "⚠️ Have you learned ___?", never assume on their behalf.

- **Each of the five lenses has its own focus, repetition is strictly forbidden**: crossover leverages / occam only discusses how deep to learn / graph only gives a map / prototype only gives the hands-on path / feynman only interrogates. Don't explain the same content five times over.
- **Keep each lens concise** — this is a "sweep through the panorama", the deep dive is left for after the user chooses. Better too short than to overload.
- Single-lens sub-entry points (use when the user wants only one): `learn-crossover` `learn-occam` `learn-graph` `learn-prototype` `learn-feynman`.
