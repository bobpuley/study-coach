---
name: study-coach:learning-path-creator
description: Runs the full new-learning-path setup flow. Use when the user says @new_learning_path, wants to start a new topic, or asks to create a learning path.
---
# Learning Path Creator

## Purpose

This skill runs the full `@new_learning_path` flow: it interviews the user to define a new
learning path, creates the domain skill file if it doesn't exist, generates a draft curriculum,
and scaffolds the folder structure. It is invoked only on demand — never loaded automatically.

---

## Flow

Execute these steps in order. Do not skip steps. Ask one question at a time.

### Step 1 — Identify the path

Ask the user: **"What topic do you want to learn?"**

Derive a kebab-case folder name from the answer (e.g., "algorithms" → `algorithms`,
"object-oriented programming" → `oo-programming`). Confirm the folder name with the user.

### Step 2 — Check for existing skill

Look for `.claude/skills/<name>/SKILL.md`.

- **If it exists:** skip to Step 5 (folder structure).
- **If it doesn't exist:** continue to Step 3.

### Step 3 — Define the domain skill (domain interview)

Ask these questions one at a time. For each question, provide a recommended answer.

1. **Expert persona:** "How should I present myself when coaching this topic?
   (e.g., 'You are an expert algorithms coach who teaches from first principles')"

2. **Reference material:** "What is the primary source this learning path is based on?
   (e.g., a book title and author, a course name, a set of standards)"

3. **Mode:** "Which learning mode fits this topic?
   - `full` — teach → attempt → review → debrief → note → drill (recommended: deep mastery)
   - `passive-learning` — teach only (content consumption)
   - `active-learning` — teach → attempt → review → debrief → note (understanding without timed testing)
   - `interview` — drill only (exam prep)"

4. **Unit label:** "What do you call the unit of progression in this topic?
   (e.g., `chapter`, `problem`, `pattern`, `session`, `module`)"

After collecting answers, summarize the skill definition and ask the user to confirm before writing.

### Step 4 — Write the skill file

Write `.claude/skills/<name>/SKILL.md` by filling in `.claude/templates/skill.template.md`
with the answers collected in Step 3.

Tell the user: **"Skill file written. You will need to run `/reload-skills` before this skill
becomes active. I'll continue scaffolding while you do that."**

### Step 5 — Generate draft curriculum

Based on the reference material field, generate a draft `PLAN.md` for this path.

- If the reference is a well-known book (e.g., CLRS, Clean Code, DDIA), enumerate its chapters/parts
- If the reference is a topic area (e.g., "LeetCode patterns"), propose a logical unit sequence
- Use `.claude/templates/plan.template.md` as the format reference

Show the draft to the user and ask: **"Does this curriculum look right? Edit anything you want,
then confirm."** Wait for confirmation before writing.

### Step 6 — Scaffold folder structure

Create the following directories (use `.gitkeep` to make empty dirs trackable):

```
<path>/
├── path.yml
├── PLAN.md
├── book/
├── my-work/
├── reviews/
├── flashcards/
├── reference/
└── coach-notes/
    └── concepts/
```

Write `<path>/path.yml`:
```yaml
skill: <name>
mode: <mode>
```

Write the confirmed `<path>/PLAN.md`.

Create `.claude/memory/<path>/profile.md` (empty, will be filled at first session start).
Create `.claude/memory/<path>/session.md` from `.claude/templates/session.template.md` (copy as-is).

### Step 7 — Done

Confirm to the user:

> Learning path **<name>** is ready.
> - Skill: `.claude/skills/<name>/SKILL.md`
> - Curriculum: `<path>/PLAN.md`
> - Memory: `.claude/memory/<path>/`
>
> **Run `/reload-skills` now to activate the domain skill**, then start your first session.
