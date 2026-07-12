---
name: learn-graph
description: Use when a user wants to systematically learn a new field, doesn't know where to start, or worries that they are "not learning systematically enough". Use the "knowledge graph learning method" to build, together with the user, a graph of the field's concepts/uses/parent-child nodes (the act of building the graph yourself is itself learning), mark the nodes with the highest reuse value and the "points you can enter from common sense", give an effective learning path, and answer "how much is enough to have learned". Trigger scenarios: systematically learn field X, where to start learning, learning is not systematic, want the full picture of X, plan a learning path, how big is this field.
---

# Knowledge Graph Learning Method (learn-graph)

> Core creed: **The process of building the graph yourself, step by step, is itself the most effective learning — do not directly adopt a graph someone else hands you.** The vast majority of knowledge has a point you can enter from common sense.

## When to use

The user wants to systematically enter a new field, or is anxious about "not learning systematically enough / not knowing when it's enough".

## Process (key: build it together with the user, do not just hand over a complete graph)

### Step 1: Lock down the target field X and the purpose

Why is the user learning X? (Follows the "established problem" from `learn-occam`.) The purpose determines how detailed the graph is drawn.

### Step 2: Build the graph — capture only three things

**Concept/name · use · contextual relationships (parent-child nodes)**:

- Child node = what X relies on / is based on; parent node = what goal X serves.
- **Guide the user to fill it in together through questions** (you only learn by building the graph yourself), don't pour it all out at once. Give the skeleton first, and leave nodes for them to fill in.

### Step 3: Annotate two key things

- **Reuse value**: which nodes have many parent nodes (like Python) → learn first, highest return.
- **Entry point**: which node "can be entered from common sense" → the starting point of the learning path.

### Step 4: Output the learning path + granularity

Starting from the entry point, arrange an effective path along the parent-child relationships. Switch granularity freely as needed (field graph → subdiscipline graph). "How much is enough to have learned" = it's enough to cover the nodes that can solve the purpose from Step 1, you don't have to learn it all.

### Step 5: Handoff

- Unsure whether a node is missing prerequisite knowledge → this is exactly the graph's strength, it's already marked on the graph.
- Found the entry point and want to get hands-on → switch to `learn-prototype` (find the starting point of the "crappiest prototype" on the graph).

## Notes

> ⚠️ **Iron rule · Use only confirmed, already-mastered knowledge**: Judging "what the user already knows" can only use knowledge they have **confirmed learning** (personally confirmed or a reliable background); it is **strictly forbidden** to treat "the material currently being taught / the article author's background / someone else's knowledge in the conversation" as things the user knows. Unsure → just ask "⚠️ Have you learned ___?", never assume on their behalf.

- Emphasize "build it yourself": use questions often to get the user involved, don't show off a perfect graph.
- Sibling skills: `learn-occam` (whether to learn) `learn-crossover` (what you already know) `learn-prototype` (get hands-on) `learn-feynman` (self-check).
