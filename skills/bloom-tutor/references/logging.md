# Learning Log and Progressive Loading

`learning-log.jsonl` lives in the working root directory; append-only, never overwrite or modify existing entries.

## `/organize learning` — Record incremental learning to the log

**Triggers:** `/organize learning`, "organize what I've recently learned", "record this in the learning log"

**Steps:**

1. **Read the log baseline**: read the root-directory `learning-log.jsonl`, take the `date` and `courses` from the last record (the last document read in each topic)
2. **Scan all topic folders**: list every subfolder under the root directory (excluding hidden directories and `.templates`), and for each topic:
   - List every `XX.md` (excluding `syllabus.md` and `summary.md`)
   - Compare against the baseline to find the **newly added documents** (those completed after the last record)
   - Read these new documents and distill 3-5 core concepts / key points
3. **Generate the log entry**: construct the following single-line JSON and **append** it to `learning-log.jsonl`:

```json
{
  "date": "YYYY-MM-DD",
  "courses": [
    {
      "name": "topic name (folder name)",
      "new_docs": ["02.md", "03.md"],
      "key_concepts": ["concept 1", "concept 2", "concept 3"],
      "progress": "X of Y documents completed"
    }
  ],
  "summary": "one-sentence summary of this learning increment",
  "total_new_docs": 0
}
```

4. **Show the user a summary**: concisely present (in the session language, English by default) which content was newly added to which topics, without repeating the raw JSON

**Rules:**
- Append only; never overwrite or modify existing entries
- When there are no newly added documents at all, still append one entry with `total_new_docs` set to 0 and `summary` set to "no new learning content this period"
- On the first run (when the log is empty), scan all existing documents as the initial baseline and set `summary` to "initialize learning log"

## `/view learning log` — Review history

**Triggers:** `/view learning log`, "what have I learned recently", "review my learning records"

**Steps:**
1. Read all entries in the root-directory `learning-log.jsonl`
2. In reverse chronological order (newest first), format and present (in the session language, English by default): date, topic, number of new documents, core concepts

## Spaced Review (retention after course completion)

Entries without a `type` field are the `/organize learning` increments above. Two additional typed entries drive spaced review:

**On course completion** (step 7 of `references/summary.md`), append:

```json
{"type": "course_complete", "date": "YYYY-MM-DD", "topic": "topic name", "rank": "A", "weakest_items": ["item …", "item …"], "next_review_days": 7}
```

**Offering a flash review** — at the start of any bloom-tutor conversation (after reading the log), check every `course_complete` topic: if `next_review_days` have passed since its latest `course_complete` or `flash_review` entry, **offer** a flash review ("It's been a while since [topic] — up for a 3-question flash review?"). Never force it; if declined, simply don't ask again until the next due window.

**Running a flash review** — conversational, no new files:

1. Pick 3 questions from the topic's mastery items, prioritizing `weakest_items` and past 🚩 miscalibrations (read `syllabus.md`/`summary.md` of that topic only if the log lacks detail)
2. Evaluate the answers ✅/⚠️/❌ conversationally, with brief corrections
3. Append the result, expanding the interval (7 → 30 → 90 days; on a poor result, keep the current interval instead of expanding):

```json
{"type": "flash_review", "date": "YYYY-MM-DD", "topic": "topic name", "score": "2/3", "next_review_days": 30}
```

## Progressive Loading Principle

`learning-log.jsonl` is the **first entry point** for understanding learning state. When the user asks "what have I learned recently", "how is my progress", or in any scenario that requires understanding learning state:

1. **Read `learning-log.jsonl` first** — it records the latest progress of every topic, the completed documents, and a summary of core concepts
2. **When the log is sufficient, do not proactively expand into specific documents**; answer directly based on the log
3. **Only drill down into specific documents in the following cases**:
   - The user has a question about some concept and needs to see the original details
   - The user explicitly requests "show me document N of topic XX"
   - The log information is insufficient to answer, and you have already told the user that a deeper look is needed

> Start from the lightest summary layer (the log), and drill down into specific documents only when needed, rather than loading all topic content at once.
