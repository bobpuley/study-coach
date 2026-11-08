---
name: whiteboard
description: Display diagrams and visual content on the agent-whiteboard canvas (mermaid, svg, html, katex, vega-lite, step-frames). Use whenever showing an architecture diagram, request flow, algorithm walkthrough, estimation formula, or chart during coaching.
---

# Whiteboard

Push all visual content to the agent-whiteboard MCP (requires the whiteboard server running at http://localhost:3000).

## Available tools

- `render(type, payload, options?)` — push content to the canvas. Supported types: mermaid, svg, html, katex, vega-lite, step-frames. Options: title (label shown above canvas), node_to_frame (step-frames only — map of node ID → frame
  index for click-to-jump navigation without `wait_click()`).
- `step(direction)` — advance ("next") or rewind ("prev") a step-frames sequence.
- `seek(frame)` — jump the step-frames cursor to an arbitrary zero-based frame index directly.
- `clear()` — reset the canvas to blank.
- `slideshow(slides, delay_ms)` — auto-advance a playlist of slides on a server-side timer. slides is an array of `{ type, payload, title? }` (same types as render() except step-frames). A new call cancels any running slideshow.
- `slideshow_stop()` — cancel the running slideshow; the last slide stays on screen.
- `wait_click(node_actions?)` — arm the browser for a single node/edge click on the current Mermaid diagram; blocks until the user clicks. Optional `node_actions: { nodeId: ["Action A", "Action B"] }` shows a popup menu on click.
  Returns `{ type, id, label, action }` or `{ type: "timeout" }` after 10 min.
- `wait_done()` — block until the user clicks the Done button in the browser. Use after render() when the user should review before you continue.
- `export()` — retrieve the current canvas source.
- `init_step_frames(<payload>)` — initialize a step frames and return the `id` to use later for adding slides one by one `append_frame({ id: "<returned-id>", <payload> })` (slides are incrementally rendered), at the end `commit_step_frames({ id: "<returned-id>" })` will finalize the creation

Pass the `render(options.workspace)` parameter with value "study-coach_<learning path>"

## When to use each type

- Architecture diagrams → mermaid (graph TD or sequenceDiagram)
- Step-by-step walkthroughs (e.g. request flows, algorithm steps) → sequential render() calls (see Sequential walkthrough pattern below)
- Math / estimation formulas → katex
- Charts and data visualizations → vega-lite
- Auto-paced presentations → slideshow()
- Interactive diagrams (let user pick a node) → render() + wait_click()

## Sequential walkthrough pattern

For multi-frame lessons, render one frame at a time:

1. Initialize the step frames `init_step_frames`
2. Render frame N with a title like "Step 3 of 8 — Insertion" `append_frame`
3. Use `wait_done()` Print in terminal: `▶ frame 3/8 — click done to continue (or ask a question)`
4. On user "done", render frame N+1
5. Repeat until last frame, `commit_step_frames`, then resume coaching flow

**Why not step-frames directly:** step-frames front-loads all frame content into a single tool call, consuming large context before the user sees frame 0.

`step()`, `seek()`, and `wait_done()` are still valid for interactive diagrams and auto-paced slideshows — not for coached walkthroughs.

## Rules

- Always include a title in options so the diagram is labeled on screen.
- If the active path has a `coach-notes/conventions.md`, Mermaid diagrams must follow it (node shapes, labels, arrows).
