# target-avro

This is a [Singer](https://singer.io) target that reads JSON-formatted data
following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

## Features

- Output Avro files for [Singer](https://singer.io) streams
- Output to cloud storages like Google Cloud Storage and Amazon S3, etc are supported powered by [smart_open](https://github.com/RaRe-Technologies/smart_open).

## Install

```sh
pip install target-avro
```

## Usage

```sh
# simple
cat <<EOF | target-avro -c sample_config.json
{"type":"STATE","value": {}}
{"key_properties":["id"],"schema":{"properties":{"assignee":{"properties":{},"type":["null","object"]},"created_at":{"format":"date-time","type":["null","string"]},"id":{"type":["null","integer"]},"labels":{"items":{"properties":{"id":{"type":["null","integer"]},"name":{"type":["null","string"]}},"type":"object"},"type":["null","array"]},"locked":{"type":["null","boolean"]},"pull_request":{"properties":{"url":{"type":["null","string"]}},"type":["null","object"]},"title":{"type":"string"}},"selected":true,"type":["null","object"]},"stream":"issues","type":"SCHEMA"}
{"type": "RECORD", "stream": "issues", "record": {"created_at":"2020-11-24T23:49:24.000000Z","id":12,"labels":[{"id":238,"name":"ABCDEFGHIJKLMNOPQRSTUV"}],"locked":true,"pull_request":{"url":"https://api.github.com/repos/sample/issues/pulls/999999"},"title":"ABCDEFGHIJKLMNOPQRSTUVWXY"}, "time_extracted": "2021-03-25T12:53:51.817781Z"}
{"type": "STATE", "value": {"bookmarks": {"singer-io/singer-python": {"issues": {"since": "2020-11-24T23:49:24.000000Z"}}}}}
EOF

# complex
cat ./tests/data/github.jsonl | target-avro -c sample_config.json
```

## Configuration

The fields available to be specified in the config file are specified
here.

| Field | Type | Default | Details |
| ---- | ---- | ---- | ---- |
| `prefix` | `["string"]`  | `N/A` | The output uri prefix. See [smart_open](https://github.com/RaRe-Technologies/smart_open) for information about valid values and credentials. |
| `disable_collection` | `["boolean", "null"]` | `false` | Include `true` in your config to disable [Singer Usage Logging](#usage-logging). |
| `logging_level` | `["string", "null"]`  | `"INFO"` | The level for logging. Set to `DEBUG` to get things like HTTP requests executed, JSON and Avro schemas, etc. See [Python's Logger Levels](https://docs.python.org/3/library/logging.html#levels) for information about valid values. |

## Known Limitations

- Requires a [JSON Schema](https://json-schema.org/) for every stream.
- Only string, string with date-time format, integer, number, boolean,
  object, and array types with or without null are supported. Arrays can
  have any of the other types listed, including objects as types within
  items.
    - Example of JSON Schema types that work
        - `['number']`
        - `['string']`
        - `['string', 'null']`
    - Exmaple of JSON Schema types that **DO NOT** work
        - `['string', 'integer']`
        - `['integer', 'number']`
        - `['any']`
        - `['null']`
- JSON Schema combinations such as `anyOf` and `oneOf` are not supported.
- JSON Schema `$ref` is not supported.

## Usage Logging
[Singer.io](https://www.singer.io/) requires official taps and targets to collect anonymous usage data. This data is only used in aggregate to report on individual tap/targets, as well as the Singer community at-large. IP addresses are recorded to detect unique tap/targets users but not shared with third-parties.

To disable anonymous data collection set disable_collection to true in the configuration JSON file.

---

Copyright &copy; 2021 Kageboushi
