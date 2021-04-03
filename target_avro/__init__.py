#!/usr/bin/env python3

import http.client
import io
import json
import logging
import sys
import threading
import urllib.parse

from typing import Any
from typing import Dict
from typing import Optional

import fastavro
import pkg_resources
import singer

from jsonschema import FormatChecker
from jsonschema.validators import Draft4Validator
from smart_open import open

from target_avro.converter import json2avro
from target_avro.converter import str2datetime


REQUIRED_CONFIG_KEYS = ["prefix"]

logger = singer.get_logger()


def emit_state(state: Optional[Dict[str, Any]]) -> None:
    if state is not None:
        line = json.dumps(state)
        logger.debug("Emitting state {}".format(line))
        sys.stdout.write("{}\n".format(line))
        sys.stdout.flush()


def persist_lines(
    config: Dict[str, Any], lines: io.TextIOWrapper
) -> Optional[Dict[str, Any]]:
    state = None
    objects: Dict[str, Any] = {}
    schemas: Dict[str, Dict[str, Any]] = {}
    writers: Dict[str, fastavro.write.Writer] = {}
    key_properties = {}
    validators: Dict[str, Draft4Validator] = {}

    # Loop over lines from stdin
    for line in lines:
        try:
            o = json.loads(line)
        except json.decoder.JSONDecodeError:
            logger.error("Unable to parse:\n{}".format(line))
            raise

        if "type" not in o:
            raise Exception("Line is missing required key 'type': {}".format(line))
        t = o["type"]

        if t == "RECORD":
            if "stream" not in o:
                raise Exception(
                    "Line is missing required key 'stream': {}".format(line)
                )
            if o["stream"] not in schemas:
                raise Exception(
                    "A record for stream {} was encountered before a corresponding schema".format(
                        o["stream"]
                    )
                )
            record = o["record"]
            validators[o["stream"]].validate(record)
            str2datetime(record, schemas[o["stream"]]["properties"])
            writers[o["stream"]].write(record)
            state = None
        elif t == "STATE":
            logger.debug("Setting state to {}".format(o["value"]))
            state = o["value"]
        elif t == "SCHEMA":
            if "stream" not in o:
                raise Exception(
                    "Line is missing required key 'stream': {}".format(line)
                )
            stream = o["stream"]
            schemas[stream] = o["schema"]
            validators[stream] = Draft4Validator(
                o["schema"], format_checker=FormatChecker()
            )
            if "key_properties" not in o:
                raise Exception("key_properties field is required")
            key_properties[stream] = o["key_properties"]

            props = o["schema"]["properties"]
            logger.debug(" ".join([t, stream, "JSON", json.dumps(props)]))
            fields = json2avro(props, o["schema"].get("required", []))
            logger.debug(" ".join([t, stream, "Avro", json.dumps(fields)]))

            name = "{}.{}.avro".format(config["prefix"], stream)
            f = open(name, "wb")
            objects[stream] = f
            writers[stream] = fastavro.write.Writer(
                f,
                fastavro.parse_schema(
                    {
                        "fields": fields,
                        "name": stream,
                        "namespace": "app.kageboushi.integrations.v1",
                        "type": "record",
                    }
                ),
            )
        else:
            raise Exception(
                "Unknown message type {} in message {}".format(o["type"], o)
            )

    for it in writers.keys():
        writers[it].flush()
    for it in objects.keys():
        o = objects[it]
        name = "{}.{}.avro".format(config["prefix"], it)
        stat = {
            "type": "counter",
            "stat": "size",
            "value": o.tell(),
            "tags": {"name": name},
        }
        logger.info("STAT: {}".format(json.dumps(stat)))
        objects[it].close()

    return state


def send_usage_stats() -> None:
    try:
        version = pkg_resources.get_distribution("target-avro").version
        conn = http.client.HTTPConnection("collector.singer.io", timeout=10)
        conn.connect()
        params = {
            "e": "se",
            "aid": "singer",
            "se_ca": "target-storage",
            "se_ac": "open",
            "se_la": version,
        }
        conn.request("GET", "/i?" + urllib.parse.urlencode(params))
        conn.getresponse()
        conn.close()
    except Exception as err:
        logger.debug("Collection request failed")
        logger.debug(err)


def main() -> None:
    args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)
    config = args.config

    logger.setLevel(config.get("logging_level", logging.INFO))
    if not config.get("disable_collection", False):
        logger.info(
            "Sending version information to singer.io. "
            + "To disable sending anonymous usage data, set "
            + 'the config parameter "disable_collection" to true'
        )
        threading.Thread(target=send_usage_stats).start()

    state = persist_lines(config, io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8"))

    emit_state(state)
    logger.debug("Exiting normally")


if __name__ == "__main__":
    main()
