---
name: learn-occam
description: Use when the user is torn over whether to learn something and to what depth, or when making trade-offs across time / energy / projects. The "simplification strategy" first presses for the established problem to be solved, checks whether existing knowledge can handle it, assesses the rate of knowledge depreciation and ROI, uses "exploration vs. application" to judge whether to learn something new or use what already exists, and delivers a "learn / don't learn / learn only the minimum sufficient" verdict, avoiding the hoarding of knowledge that will depreciate. Triggers: whether to learn X, whether it's worth going deep, how deep is enough, what to learn when time is short, whether to dig deep or just get by.
---

# Simplification Strategy (learn-occam)

> Core creed: **The most valuable thing in this world is not knowledge, it is your time.** If something can be solved with existing knowledge, don't learn something new; what you'll need later, learn later.

## When to use

The user is torn over "whether to learn X / to what depth / where to put energy." This is the **brake** on the "breadth-first, over-long interest queue" tendency.

## Process

### Step 1: First find the "established problem"

Press with one question: **What is the specific problem you want to solve?** No specific problem, purely "feels like I should learn it / everyone else is learning it" → go straight into the "learn later" queue, taking no energy right now. Understanding the function of knowledge matters more than the knowledge itself.

### Step 2: Can existing knowledge handle it

**Ask clearly what the user already knows**—if it can solve the problem, **don't learn something new**. If unsure "whether they might already know it," pair with `learn-crossover`.

### Step 3: Depreciation rate + ROI

How soon will this knowledge depreciate? (Tech stacks / tools often update noticeably within 6–12 months) Is it worth it relative to your limited time? **Depreciates fast + can be outsourced to AI / looked up anytime → you only need to "know it exists and what it governs," no need to truly learn it.**

### Step 4: Exploration vs. application (N-armed bandit)

Right now, should you "explore" (learn new) or "apply" (use existing)? The higher the cost of exploration → the more you should lean toward application. Only when the goal is hard enough and existing knowledge truly can't reach it does the simplification strategy **push** you to learn.

### Step 5: Give the verdict

Clearly pick one of three: **① Learn** (worth it and existing knowledge can't handle it) / **② Don't learn** (into the "learn later" queue) / **③ Learn only the minimum sufficient piece** (point out exactly which small piece). If deep diving is needed, switch to `learn-graph` to build a path.

## Notes

> ⚠️ **Iron rule · Use only confirmed known knowledge**: Judging "what the user already knows" may only rely on knowledge they have **confirmably learned** (personally confirmed or reliable background); it is **strictly forbidden** to treat "the material being taught / the article author's background / knowledge others have in the conversation" as something the user knows. If unsure → ask directly "⚠️ Have you learned ___?"—never assume it on their behalf.

- The simplification strategy is not "learn less," it is "let the problem decide what you learn."
- Its downside is a tendency to get stuck in local optima—when unsure "whether prerequisite knowledge is missing," switch to `learn-graph`.
- Sibling skills: `learn-crossover` (what you already know) `learn-graph` (systematic mapping) `learn-prototype` (hands-on iteration) `learn-feynman` (self-check).
