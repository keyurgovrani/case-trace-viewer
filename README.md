# Case Trace Viewer

A single-page viewer for AI agent case exports: every user turn, the span timeline with latency, tokens, cache use and cost, the full input and output of each model call and tool call, and the conversation.

Hosted at https://keyurgovrani.github.io/case-trace-viewer/

## Use

1. Open the page.
2. Pick the `.json` written by `to_json.py`, or the raw `case-traces-<caseId>-<runId>.jsonl` the Export Case Traces automation produced.

The file is parsed in the browser. Nothing is uploaded.

## What you get

- **Turns**, latest first. Each card shows latency, input and output tokens, cached tokens, cost and span count.
- **Trace timeline**: Query, Agent Execution, then every step with a duration bar, latency and cost. Steps group by sub-agent lane. Tool calls carry no task id in the platform trace, so the viewer pairs each tool span with the model call whose `tool_calls` name and arguments match, and takes the lane from there.
- **Step details**: start, latency, tokens, cache, cost, model or tool, lane. Input and output blocks open in a read-only Monaco editor (folding, sticky headers, Cmd+F find), as a foldable tree, or raw. Prose blocks (system prompt, response text) open as rendered markdown.
- **Query row**: the user message and the agent's final reply.
- **Conversation**: user and agent messages, dispatches to sub-agents, sub-agent results, platform context rows and thoughts, rendered as markdown with lane and kind filters.

## Convert an export

```sh
python3 to_json.py case-traces-<caseId>-<runId>.jsonl
```

Writes a pretty-printed `.json` next to the input. The viewer opens either file.

## Run locally

Open `index.html` directly, or serve the folder:

```sh
python3 -m http.server 8765
```

## Notes

- Monaco 0.56.0, marked, DOMPurify and lodash load from cdnjs. Monaco's stylesheet is inlined in the page so the viewer also works where a cross-origin stylesheet is blocked. 0.52.2 mis-stacked sticky headers over wrapped lines, which is why the version matters.
- A 115 MB export opens in a few seconds in Chrome.
