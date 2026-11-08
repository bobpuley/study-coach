---
name: study-coach:practicing
description: Generates practice exercises from existing learning path knowledge. Use when the user types @practice, wants to drill on a topic outside the curriculum, or asks for extra exercises.
---
# Practicing

## Purpose

Synthesizes exercises from completed learning path content. Generative and open-ended — no curriculum, no pass/fail, no PLAN.md impact.

---

## Invocation

```
@practice                        # coach picks any topic from any path
@practice <path>                 # scoped to that path
@practice <path> <topic>         # scoped to a specific topic
```

---

## Flow

### Step 1 — Determine scope

- No path given: list completed units across all paths; ask which one to practice.
- Path given, no topic: read `<path>/PLAN.md` for completed units; propose one or ask the user to pick.
- Path + topic given: proceed directly.

**Cold-start check:** if the path has fewer than 2 completed units, warn the user that problem generation may be shallow and ask whether to proceed or pick a different scope.

### Step 2 — Load knowledge base

Read (never write) from the scoped path:
- `<path>/book/` — lesson content
- `<path>/reference/glossary.md` and any `<path>/reference/*-cheatsheet.md`
- `<path>/flashcards/` — card decks

Read `.claude/memory/<path>/profile.md` for difficulty calibration.

### Step 3 — Generate problem

Synthesize a problem inspired by the knowledge base:
- Test understanding, not recall
- Be distinct from drill questions already in `reviews/*-drill.md`
- Match the user's level from `profile.md`

### Step 4 — Create session folder

Derive a slug: `<YYYY-MM-DD>-<path>-<kebab-topic>`.

Create `practicing/<slug>/` (create `practicing/` itself if missing):
- Write `problem.md` with the generated problem statement.
- Pre-scaffold `attempt.md` from `.claude/templates/attempt.template.md`, adapted to the problem.

Tell the user: "Open `practicing/<slug>/attempt.md` in your editor and write your solution. When done, type `@done`."

### Step 5 — Review

Read the user's attempt. Conduct review on the terminal (Socratic questions first, then direct feedback).

Write coach feedback to `practicing/<slug>/review.md`.

### Step 6 — Log gaps

Append one line to `.claude/memory/<path>/practicing-log.md` (create if missing):

```
<date> | <topic> | <gap summary>
```

If multiple paths were touched in the session, append one entry per path.

---

## Session end

No PLAN.md update. No pass/fail. The gap log is the only persistent output beyond the session folder.
