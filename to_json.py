#!/usr/bin/env python3
"""Turn an Export Case Traces .jsonl file into one readable, pretty-printed .json.

usage: python3 to_json.py <export.jsonl> [out.json]

Only for that automation's output (records shaped {kind, key, data}). Any other
file is refused rather than turned into an empty skeleton.

Layout of the result:
  caseId
  turns[]        one per user message, in order
    timeline     the span tree the observability view shows
    spans[]      every trace span of that turn (all agents, sub-agents included),
                 by start time. Tool outputs stored as JSON text are parsed back
                 into objects so they read as data, not escaped strings.
  otherSpans[]   spans whose turn is not in the turn list (normally empty)
  messages[]     chat messages and per-step THOUGHT rows, by time
"""
import json
import sys
from collections import defaultdict

# Server-owned bookkeeping on every row; it only adds noise when reading.
NOISE = {'grants', 'standard', 'deleted', 'lastPlatformUpdateBy', 'lastPlatformUpdateOn', 'projectId', 'entityType'}


def unwrap(value):
    """Parse JSON held in a string, and the MCP envelope `{content:[{text}]}` inside it."""
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text or text[0] not in '{[':
        return value
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return value
    body = parsed.get('result', parsed) if isinstance(parsed, dict) else parsed
    content = body.get('content') if isinstance(body, dict) else None
    if isinstance(content, list) and content and isinstance(content[0], dict) and 'text' in content[0]:
        return {**body, 'content': [{**part, 'text': unwrap(part.get('text'))} for part in content]}
    return parsed


def span_view(row):
    props = dict(row.get('properties') or {})
    view = {
        'id': row.get('id'),
        'type': props.pop('currentType', None),
        'agent': props.pop('aiAgentId', None),
        'task': props.pop('taskId', None),
        'tool': props.pop('toolName', None),
        'startTime': props.pop('startTime', None),
        'parent': props.pop('parent', None),
        'input': props.pop('input', None),
        'output': unwrap(props.pop('output', None)),
        'outputObject': props.pop('outputObject', None),
    }
    view = {key: value for key, value in view.items() if value is not None}
    view['details'] = props
    return view


EXPORT_KINDS = {'turns', 'timeline', 'trace', 'message'}


def read_records(source):
    """Every line as JSON. A line that is not JSON stops the run with its line number."""
    records = []
    with open(source) as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                sys.exit(f'{source}:{number}: not JSON ({error.msg})')
    return records


def is_case_export(records):
    return bool(records) and all(
        isinstance(record, dict) and record.get('kind') in EXPORT_KINDS and 'data' in record for record in records
    )


def case_layout(records):
    case_id, turns, timelines, messages = None, [], {}, []
    spans_by_turn = defaultdict(list)
    for record in records:
        kind, key, data = record.get('kind'), record.get('key'), record.get('data')
        if kind == 'turns':
            case_id = key
            turns.append(data)
        elif kind == 'timeline':
            timelines[key] = data
        elif kind == 'trace':
            spans_by_turn[(data.get('properties') or {}).get('messageId')].append(span_view(data))
        elif kind == 'message':
            messages.append({k: v for k, v in data.items() if k not in NOISE})

    turn_ids = {turn.get('traceId') for turn in turns}
    result = {
        'caseId': case_id,
        'turns': [
            {
                **turn,
                'timeline': timelines.get(turn.get('traceId')),
                'spans': sorted(spans_by_turn.get(turn.get('traceId'), []), key=lambda span: span.get('startTime') or 0),
            }
            for turn in turns
        ],
        'otherSpans': sorted(
            (span for turn_id, spans in spans_by_turn.items() if turn_id not in turn_ids for span in spans),
            key=lambda span: span.get('startTime') or 0,
        ),
        'messages': sorted(messages, key=lambda message: (message.get('properties') or {}).get('channelCreatedTime') or 0),
    }
    span_total = sum(len(turn['spans']) for turn in result['turns']) + len(result['otherSpans'])
    return result, f'case export: {len(turns)} turns, {span_total} spans, {len(messages)} messages'


def main():
    source = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else source.rsplit('.', 1)[0] + '.json'
    records = read_records(source)
    if not is_case_export(records):
        sys.exit(f'{source}: not an Export Case Traces file (every line must be {{kind, key, data}})')
    result, summary = case_layout(records)
    with open(target, 'w') as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)
    print(f'{target}: {summary}')


if __name__ == '__main__':
    main()
