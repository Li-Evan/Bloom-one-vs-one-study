# AGENTS.md

Portable entry point for any coding agent (OpenCode, Codex, Cursor, Aider, …).
The Bloom tutoring logic lives in `skills/*/SKILL.md` — plain Markdown instructions,
no Claude-specific tools. This file just tells a non-Claude agent when and how to load them.

## Skills

| Trigger | Load and follow |
|---|---|
| User wants 1-on-1 Socratic tutoring on a topic — "help me learn X", "开个文件夹学 X", "我读完了", "继续 / 下一篇", "整理学习" | `skills/bloom-tutor/SKILL.md` (+ its `references/*.md`) |
| Deep-dive a concept from five angles | `skills/learn-deep/SKILL.md` |
| Learn via analogy to what the user already knows | `skills/learn-crossover/SKILL.md` |
| Decide whether / how deeply to learn something (ROI) | `skills/learn-occam/SKILL.md` |
| Map a field as a knowledge graph + learning path | `skills/learn-graph/SKILL.md` |
| Learn by building the crappiest working prototype | `skills/learn-prototype/SKILL.md` |
| Verify understanding by explaining it back | `skills/learn-feynman/SKILL.md` |

## How to run a skill

1. Read the matched `SKILL.md` in full, plus every file under its `references/` folder.
2. Obey its rules literally (the tutor skill's 工作守则 are non-negotiable — e.g. one lesson per turn), **except the language rule, which rule 0 overrides**.
3. The skills need only filesystem read/write in the working directory — no MCP, no special tools.

Each skill folder is self-contained and dependency-free.
