# Case Trace Viewer

A single-page viewer for AI agent case exports: every user turn, the span timeline with latency, tokens, cache use and cost, the full input and output of each model call and tool call, and the conversation.

Hosted at https://keyurgovrani.github.io/case-trace-viewer/

## Use

1. Open the page.
2. Pick the `<agent>-<caseId>.json` the Export Case Traces automation produced. Older `.jsonl` exports and `to_json.py` output open too.

The file is parsed in the browser. Nothing is uploaded.

## What you get

- **Turns**, latest first. Each card shows latency, input and output tokens, cached tokens, cost and span count.
- **Trace timeline**: Query, Agent Execution, then every step with a duration bar, latency and cost. A model call's row leads with what it decided (`→ loadSkill`, `→ reply`), with the model name after it. Steps group by sub-agent lane. Each lane is named after the agent the brief went to and the brief's title, so a row reads `Workflow Agent · Explore SharePoint Documents` and not a task id. Tool calls carry no task id in the platform trace, so the viewer pairs each tool span with the model call whose `tool_calls` name and arguments match, and takes the lane from there.
- **Finding the slow and costly steps**: the order menu lists every step flat, slowest, costliest or heaviest in input tokens first. Double-click a lane to scale the timing bars to it. `Collapse lanes` folds each lane to one row. A `failed` chip appears when a turn has failed steps and filters to them.
- **Step details**: start, offset into the turn, latency, tokens, cache, cost, model or tool, lane. The head stays pinned, with previous and next buttons and links to each section. A tool links to the model call that asked for it, and a model call links to the tool runs it started. Input and output blocks open in a read-only Monaco editor (folding, sticky headers, Cmd+F find), as a foldable tree, or raw. Prose blocks (system prompt, response text) open as rendered markdown.
- **Model call inputs** open as a chat, newest message first, so the message the model was answering leads. Thinking, tool calls and tool results each get their own card. Code and JSON inside tool arguments print as real multi-line blocks. The Code tab keeps the exact JSON, and the raw span record keeps the original order.
- **Lane details**: model and tool call counts, the tools the lane used with call counts and total time, the brief the sub-agent got and the result it sent back.
- **Query row**: the user message and the agent's final reply.
- **App Builder runs**: when the Solution Agent calls Generate App, the App Builder works in a turn of its own. The turn list marks that turn `App Builder · Build <app>` (or `Edit`) and indents it. Its Query row links back to the Generate App call, and the call links forward to the run. The runs are matched by app id and start time, because the App Builder's spans carry the Solution Agent's id. In Conversation, the brief shows as a dispatch and the App Builder's thoughts appear on the app's lane.
- **Layout and theme**: drag the edges between panels to resize them (arrow keys work on a focused edge, double-click resets). The turns panel collapses to a thin rail, and a System / Light / Dark switch sits in the header. The code editor's colors follow the page theme. The browser remembers sizes, collapse and theme.
- **Keyboard**: `j` / `k` next and previous step, `[` / `]` older and newer turn, `/` filter, `t` / `c` switch view, `o` open a file, `?` lists them all.
- **Opening files**: `Open another file` goes straight to the file picker, and the open case stays on screen until the new one parses. A file can be dropped anywhere on the window.
- **Conversation**: user and agent messages, dispatches to sub-agents, sub-agent results, platform context rows and thoughts, rendered as markdown with lane and kind filters. `Open in trace` on a message jumps to its turn, or to its lane for sub-agent traffic.

## Convert an older export

Exports made before 2026-09-30 are JSON Lines. To read one outside the viewer:

```sh
python3 to_json.py case-traces-<caseId>-<runId>.jsonl
```

Writes a pretty-printed `.json` next to the input.

## Run locally

Open `index.html` directly, or serve the folder:

```sh
python3 -m http.server 8765
```

## Notes

- Monaco 0.56.0, marked, DOMPurify and lodash load from cdnjs. Monaco's stylesheet is inlined in the page so the viewer also works where a cross-origin stylesheet is blocked. 0.52.2 mis-stacked sticky headers over wrapped lines, which is why the version matters.
- A 115 MB export opens in a few seconds in Chrome.
