import random
import string

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import dateutil.parser


def _random_name(n):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


def _process_json2avro(
    schema: Dict[str, Any], t: str
) -> Optional[Union[str, Dict[str, Any]]]:
    if t == "object":
        fields = json2avro(schema.get("properties"), schema.get("required", []))
        if not fields:
            return None
        return {"name": _random_name(10), "type": "record", "fields": fields}
    elif t == "array":
        if "items" not in schema:
            # ignore array without items
            return None
        # TODO: check items type, dict or list.
        if "type" not in schema["items"]:
            # ignore empty type
            return None
        next_t = schema["items"]["type"]
        types = [next_t] if isinstance(next_t, str) else next_t
        items = [_process_json2avro(schema["items"], nt) for nt in types]
        if len(items) == 0:
            return None
        if len(items) == 1:
            return {"type": "array", "items": items[0]}
        if len(items) >= 2:
            return {"type": "array", "items": items}
    elif t == "string" and schema.get("format") == "date-time":
        return {"type": "long", "logicalType": "timestamp-millis"}
    elif t == "integer":
        return "long"
    elif t == "number":
        return "double"
    return t


def json2avro(
    props: Optional[Dict[str, Any]], required: List[str]
) -> List[Dict[str, Any]]:
    if props is None:
        # ignore empty properties
        return []
    result = []
    for prop, schema in props.items():
        # TODO: check singer metadata.
        if "type" not in schema:
            # ignore empty type
            continue
        types = []
        for t in (
            [schema["type"]] if isinstance(schema["type"], str) else schema["type"]
        ):
            r = _process_json2avro(schema, t)
            if r:
                types.append(r)
        if not types or len(types) == 1 and types[0] == "null":
            # ignore empty types
            continue
        ts = ["null", *types] if prop not in required and len(types) == 1 else types
        # TODO: check avro name restriction.
        # see http://avro.apache.org/docs/current/spec.html#names
        result.append({"name": prop, "type": ts})
    return result


def _process_str2datetime(records: List[Any], schema: Dict[str, Any]) -> List[Any]:
    t = schema["type"]
    if t == "object":
        return [str2datetime(rec, schema["properties"]) for rec in records]
    elif t == "array":
        return [_process_str2datetime(recs, schema["items"]) for recs in records]
    elif t == "string" and schema.get("format") == "date-time":
        return [int(dateutil.parser.parse(rec).timestamp()) * 1000 for rec in records]
    return records


def str2datetime(record: Dict[str, Any], props: Dict[str, Any]) -> Dict[str, Any]:
    for prop, schema in props.items():
        if "type" not in schema:
            # ignore empty type
            continue
        types = [schema["type"]] if isinstance(schema["type"], str) else schema["type"]
        if "object" in types:
            if record.get(prop) is None:
                continue
            str2datetime(record[prop], schema["properties"])
        if "array" in types:
            if record.get(prop) is None:
                continue
            if "items" not in schema:
                continue
            if "type" not in schema["items"]:
                continue
            record[prop] = _process_str2datetime(record[prop], schema["items"])
        elif "string" in types and schema.get("format") == "date-time":
            if record.get(prop) is None:
                continue
            record[prop] = int(dateutil.parser.parse(record[prop]).timestamp()) * 1000
    return record
