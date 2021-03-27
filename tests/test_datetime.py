import unittest

from target_avro.converter import str2datetime


class TestRecordConvert(unittest.TestCase):
    def test_str2datetime(self) -> None:
        props = {"updated_at": {"type": ["null", "string"], "format": "date-time"}}
        record = {"updated_at": "2020-11-24T23:49:24.000000Z"}
        str2datetime(record, props)
        self.assertEqual(1606229364000, record["updated_at"])

    def test_str2datetime_object(self) -> None:
        props = {
            "a": {
                "type": ["null", "object"],
                "properties": {
                    "b": {"type": ["null", "string"], "format": "date-time"}
                },
            }
        }
        record = {"a": {"b": "2020-11-24T23:49:24.000000Z"}}
        str2datetime(record, props)
        self.assertEqual(1606229364000, record["a"]["b"])

    def test_str2datetime_array(self) -> None:
        props = {
            "a": {
                "type": ["null", "array"],
                "items": {"type": "string", "format": "date-time"},
            }
        }
        record = {"a": ["2020-11-24T23:49:24.000000Z"]}
        str2datetime(record, props)
        self.assertEqual(1606229364000, record["a"][0])

    def test_str2datetime_array_record(self) -> None:
        props = {
            "a": {
                "type": ["null", "array"],
                "items": {"type": "object", "properties": {"b": {"type": "number"}}},
            }
        }
        record = {"a": [{"b": 1}]}
        str2datetime(record, props)
        self.assertEqual(1, record["a"][0]["b"])

    def test_str2datetime_array_nested(self) -> None:
        props = {
            "a": {
                "type": ["null", "array"],
                "items": {
                    "type": "array",
                    "items": {"type": "string", "format": "date-time"},
                },
            }
        }
        record = {"a": [["2020-11-24T23:49:24.000000Z"]]}
        str2datetime(record, props)
        self.assertEqual(1606229364000, record["a"][0][0])


if __name__ == "__main__":
    unittest.main()
