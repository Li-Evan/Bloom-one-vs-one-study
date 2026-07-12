# Source-Grounded Courses (`sources.md`)

Ground a course in the user's own library: the course becomes a guided path **through their books**, with real citations, instead of model-memory prose.

**Triggers**: "learn X from <folder>", "mine this folder for a course on X", "build a course from these books", or the user names local materials when starting a topic.

## Building the manifest (at course start, before the syllabus)

1. List the given folder (non-recursive unless the user says otherwise); shortlist candidate files by name/extension (PDF primarily; note unreadable formats to the user instead of failing silently)
2. For each candidate, read **only the TOC / front matter** — enough to judge relevance and chapter coverage, never whole books at this stage
3. Write `sources.md` in the topic folder:

```markdown
# Sources

> Corpus for this course. Citations in the articles point here.

| # | File | Relevance | Chapters → syllabus modules |
|---|------|-----------|------------------------------|
| S1 | books/foo.pdf | primary | ch.2-4 → Module 1; ch.7 → Module 3 |
| S2 | books/bar.pdf | supplementary | ch.1 → Module 2 |

## Not used
- [files judged irrelevant, one line of reasoning each — so the user can override]
```

4. If the corpus covers the topic only partially, say so plainly before generating the syllabus, and let the user choose: narrow the course to the corpus, or fill gaps from general knowledge.

## Grounding rules

- **Syllabus**: derive modules from what the corpus actually covers; "Out of Scope" must name relevant areas **the corpus lacks** — honest boundaries
- **Articles**: major claims and explanations drawn from a source carry a citation `(S1 ch.3, p.42)`; quote key passages sparingly and verbatim; end each body article with a short **Further reading** section pointing into specific chapters
- Where the corpus is silent, teach from general knowledge **without inventing citations**
- **Progressive loading**: before writing an article, read only the chapters mapped to that article's modules — never re-read the whole corpus
- Update the manifest's chapter→module mapping if the syllabus or reading reveals it was wrong; `sources.md` is working state, not a one-shot artifact
- Everything else (feedback loop, `???`, evaluations, ranks, summary) is unchanged; `summary.md`'s Further-reading/extension section should point at unused chapters of the corpus
