import json
import os
import unittest
import unittest.mock as mock

from typing import Any
from typing import Dict

from target_avro.converter import json2avro


class TestSchemaConvert(unittest.TestCase):
    @mock.patch("random.choices")
    def test_json2avro(self, choices_mock) -> None:
        choices_mock.return_value = ["1"]
        json_schema: Dict[str, Any]
        with open(os.path.join(os.path.dirname(__file__), "data/schema.json")) as f:
            json_schema = json.load(f)
        avro_schema: Dict[str, Any]
        with open(
            os.path.join(os.path.dirname(__file__), "data/schema.avsc.json")
        ) as f:
            avro_schema = json.load(f)
        fields = json2avro(
            json_schema["schema"]["properties"],
            json_schema["schema"].get("required", []),
        )
        assert fields is not None
        self.assertDictEqual(
            {
                "fields": fields,
                "name": "issue",
                "namespace": "app.kageboushi.integrations.v1",
                "type": "record",
            },
            avro_schema,
        )

    def test_object_items(self) -> None:
        props = {"contents": {"type": "array", "items": {"type": "number"}}}
        want = [
            {
                "name": "contents",
                "type": ["null", {"type": "array", "items": "double"}],
            },
        ]
        got = json2avro(props, [])
        self.assertListEqual(got, want)

    @mock.patch("random.choices")
    def test_nested_object(self, choices_mock) -> None:
        choices_mock.return_value = ["1"]
        props = {
            "payload": {
                "type": ["null", "object"],
                "properties": {
                    "commits": {
                        "type": ["null", "array"],
                        "items": {
                            "type": ["null", "object"],
                            "properties": {"distinct": {"type": ["null", "boolean"]}},
                        },
                    }
                },
            }
        }
        want = [
            {
                "name": "payload",
                "type": [
                    "null",
                    {
                        "name": "1",
                        "type": "record",
                        "fields": [
                            {
                                "name": "commits",
                                "type": [
                                    "null",
                                    {
                                        "type": "array",
                                        "items": [
                                            "null",
                                            {
                                                "name": "1",
                                                "type": "record",
                                                "fields": [
                                                    {
                                                        "name": "distinct",
                                                        "type": ["null", "boolean"],
                                                    }
                                                ],
                                            },
                                        ],
                                    },
                                ],
                            }
                        ],
                    },
                ],
            },
        ]
        got = json2avro(props, [])
        self.assertListEqual(got, want)

    @mock.patch("random.choices")
    def test_required_fields(self, choices_mock) -> None:
        choices_mock.return_value = ["1"]
        props = {
            "contents": {
                "type": "object",
                "properties": {"name": {"type": "number"}},
                "required": [],
            }
        }
        want = [
            {
                "name": "contents",
                "type": [
                    "null",
                    {
                        "type": "record",
                        "name": "1",
                        "fields": [{"name": "name", "type": ["null", "double"]}],
                    },
                ],
            },
        ]
        got = json2avro(props, [])
        self.assertListEqual(got, want)


if __name__ == "__main__":
    unittest.main()
