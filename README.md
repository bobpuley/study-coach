# Study Coach

A learning-coach agent for [Claude Code](https://docs.claude.com/en/docs/claude-code). It turns a folder into a personal study vault: you pick a topic, the coach builds a curriculum and then runs structured sessions (teach → attempt → review → debrief → note → drill), remembering where you left off.

Lessons and diagrams are shown visually on [**agent-whiteboard**](https://github.com/bobpuley/agent-whiteboard), its natural companion. The coach also works without it, falling back to the terminal.

This repository contains **only the agent** (protocol, templates, skills). Your learning paths, notes and progress are yours and stay out of it.

## How it works

| Piece | Role |
|-------|------|
| `CLAUDE.md` | The coach's protocol: session start/end, file naming, step vocabulary, handoff rules |
| `.claude/skills/learning-path-creator` | `@new_learning_path` — interviews you and scaffolds a path |
| `.claude/skills/practicing` | `@practice` — extra exercises from what you already learned |
| `.claude/skills/whiteboard` | Rules for rendering lessons on agent-whiteboard |
| `.claude/skills/<domain>` | One skill per subject (persona, reference book, workflow, unit label). `core-java` is included as an example |
| `.claude/templates/` | Scaffolds for attempts, notes, reviews, debriefs, flashcards, plan, session |
| `.claude/scripts/glossary.py` | Helper to maintain each path's glossary |
| `.mcp.json` | Connects Claude Code to the whiteboard at `http://localhost:3000/mcp` |

Generated at runtime (not in this repo):

```
<path>/                 one folder per learning path
├── path.yml            { skill, mode }
├── PLAN.md             curriculum + checkboxes
├── book/               coach lessons
├── my-work/            your attempts and notes
├── reviews/            reviews, debriefs, drill reports
├── flashcards/         Obsidian Spaced Repetition decks
└── reference/          glossary + cheatsheets
.claude/memory/<path>/  your profile, session position, gap log
practicing/             @practice sessions
```

## Setup

**Requirements:** Claude Code, Python 3 (glossary script), and — optionally but recommended — Node.js ≥ 18 for the whiteboard.

```bash
git clone https://github.com/bobpuley/study-coach.git
cd study-coach

# in a separate terminal: start the whiteboard (opens a browser tab, serves :3000)
npx agent-whiteboard

# in this folder
claude
```

On first launch run `/mcp` in Claude Code and enable `agent-whiteboard` (the server must be running first). If you change the whiteboard's `PORT`, update the URL in `.mcp.json`.

> **License note:** agent-whiteboard is released under PolyForm Noncommercial 1.0.0; this repo is MIT. Check the whiteboard's license for your use.

### Obsidian (optional)

Open the folder as an Obsidian vault to read lessons and cheatsheets with rendered tables and Mermaid, and install the **Spaced Repetition** plugin to review the generated `flashcards/` decks.

## Use cases

### 1. Start a new learning path

```
@new_learning_path
```

The coach asks for the topic, the expert persona, the reference material, the mode and the unit label, writes `.claude/skills/<domain>/SKILL.md`, drafts `PLAN.md` for your approval, and scaffolds the folder. Run `/reload-skills` when asked.

### 2. Study session

Start `claude` in the folder and say which path to continue (or let it list them). The coach reads your profile, `session.md` and `PLAN.md`, tells you where you stopped, and resumes at the exact step. Within a unit:

| Command | What happens |
|---------|--------------|
| `@teach <topic>` | Lesson with diagrams on the whiteboard, saved to `book/` |
| `@attempt <topic>` | Coach pre-scaffolds `my-work/…-attempt.md`; you write in your editor |
| `@review` | Socratic questions about gaps, no direct answers; repeatable |
| `@debrief` | Your work vs. the reference, deltas highlighted |
| `@note` | You write a synthesis; once "stable" the coach generates flashcards, a cheatsheet and glossary entries |
| `@drill <topic>` | Timed, no notes, pass/fail; a pass ticks the unit in `PLAN.md` |
| `@hint` | Escape hatch: direct answer, logged in `session.md` |

### 3. Choose how deep to go (modes)

Set `mode` in `<path>/path.yml`, or override for one session with `@mode <name>`:

| Mode | Steps |
|------|-------|
| `full` | teach → attempt → review → debrief → note → drill |
| `active-learning` | teach → attempt → review → debrief → note |
| `passive-learning` | teach |
| `interview` | drill only (exam prep) |

### 4. Extra practice

```
@practice                    # coach picks
@practice <path>             # scoped to a path
@practice <path> <topic>     # scoped to a topic
```

Creates `practicing/<date>-<path>-<topic>/` with `problem.md`, your `attempt.md` and the coach's `review.md`; recurring gaps are logged to `.claude/memory/<path>/practicing-log.md` and surfaced at the next session start.

### 5. Without the whiteboard

If the whiteboard server isn't running (or the MCP server is disabled), the coach falls back to terminal output with Markdown tables and Mermaid code blocks saved in `book/`. Nothing else changes.

### 6. Add or customise a subject

Create a domain skill by hand (copy `.claude/templates/skill.template.md`, or see `.claude/skills/core-java/SKILL.md`): persona, reference material, workflow (a subset of the steps above) and `unit_label`. Reference it from `<path>/path.yml`.

## Keeping your study data private

`.gitignore` excludes learning paths, `practicing/`, `.claude/memory/` and all non-bundled domain skills. When you create a new path, add its folder to `.gitignore` (or keep your vault in a private repository and use this one as the agent template).

## License

[MIT](LICENSE)
