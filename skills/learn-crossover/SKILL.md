---
name: learn-crossover
description: Use when the user is learning or encountering a new concept / new technology / new algorithm / new field (especially when it feels unfamiliar or a bit hard). Apply the "crossover principle" to leverage the knowledge the user has already mastered to quickly bootstrap new knowledge — point out the same thing they have in fact already learned (under a different name), old knowledge that is structurally isomorphic, existing knowledge that can explain the new knowledge, and highlight the cross-domain meta-knowledge pattern the new concept embodies. Turn "learning something new" into "discovering you already know half of it." Trigger scenarios: learn X, encountering X, this is so hard, what is X, help me understand X.
---

# Crossover Principle Learning Method (learn-crossover)

> Core creed: **Truly fast learning is really "you have already learned it."** Crossover matches **structure**, not nouns.

## When to use

When the user is learning / encountering a new concept X (new technology, new algorithm, new theory, new field...), especially when they feel it is "unfamiliar / a bit hard." Difficulty is often not an intelligence problem; it is that relative to the user there is still "old knowledge that has not been connected up."

## Process

### Step 1: Grasp the essential structure of X (do not pile on jargon)

Use a sentence or two to state clearly what X is actually doing — what its core mechanism / structure is. Strip off the shell of jargon and leave "in essence it is a ___." **Only once you have the structure can you go match it against what the user has learned.**

### Step 2: Figure out what the user already knows

**Actively ask** to build a checklist of the "knowledge the user has mastered":

- Ask about the user's background: which related fields they have studied, what projects they have done, which tools / theories they are familiar with
- Only adopt knowledge the user has **personally confirmed** in the conversation that they have learned
- Purpose: find old knowledge that is structurally isomorphic to X, or that can explain X

When unsure, just ask "Have you studied ___?", and **never infer what the user knows from the material being taught / the article author's background**.

### Step 3: Organize output around the "three crossover conjectures" (core)

1. **🎁 You have in fact already learned it (under a different name)** — highest priority. Is X just the Y the user already knows with a different field name? (e.g. derivative = gradient = rate of change). On a hit, just say "you already know it, it is merely renamed X."
2. **🔗 Structurally isomorphic (very similar)** — provide a **field-level correspondence table** between the Z the user has learned and X (A↔a, B↔b...), and **explicitly mark what is the same and what is different**. Iron rule: what differs is what differs, but the similar parts are the learning lever — do not refuse to use it just because it is "strictly different."
3. **🧩 Can be explained (explained with existing knowledge)** — use the W the user has mastered to make X clear.

### Step 4: Point out the meta-knowledge

Which **recurring underlying pattern** does X embody? (divide and conquer, self-bootstrapping / bootstrap, damping-negative feedback, exploration vs. exploitation, quantitative change to qualitative change, controlling variables, state machine...). Tell the user "you have also seen this pattern in ___, ___," hooking X onto their meta-knowledge network.

### Step 5: Landing point

Wrap up in one sentence, lowering the fear of learning + pointing out the minimal part that remains to be newly learned:

> "So for X you already know the ___ part; the only thing that is truly new and needs to be learned from scratch is ___."

## Notes

> ⚠️ **Iron rule · only use confirmed known knowledge**: judging "what the user already knows" may only use knowledge they have **confirmed learning** (personally confirmed or reliable background); it is **strictly forbidden** to treat "the material being taught / the article author's background / someone else's knowledge in the conversation" as what the user knows. When unsure → just ask "⚠️ Have you studied ___?", and never assume on their behalf. (The most common wipeout point: wrongly pinning the material author's background onto the learner, which invalidates the whole crossover.)

- **Better to give more concrete examples** (case-driven); do not hand over an abstract framework.
- Structural correspondence must be given down to the **field-level mapping table**; do not vaguely say "they are very similar."
- When unsure whether a crossover connection holds, **mark it "this is an analogy yet to be verified"** — propose a hypothesis, allow it to be refuted.
- Sibling skills: for "should I learn this at all" use `learn-occam`, for "systematically build a map" use `learn-graph`, for "hands-on iteration" use `learn-prototype`, for "self-check whether I understood" use `learn-feynman`.
