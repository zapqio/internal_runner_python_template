import json
from pathlib import Path
import unittest

from tools.run_local import execute, LOGGER_NAME


ROOT = Path(__file__).resolve().parents[1]


class TemplateTests(unittest.TestCase):
    def test_example_input_produces_documented_output(self):
        result = execute((ROOT / "examples/input.json").read_text(encoding="utf-8"))
        expected = json.loads((ROOT / "examples/output.json").read_text(encoding="utf-8"))
        self.assertEqual(expected, json.loads(result))

    def test_unicode_and_surrounding_whitespace(self):
        result = json.loads(execute(json.dumps({"name": "  Łukasz  "}, ensure_ascii=False)))
        self.assertEqual("Cześć, Łukasz!", result["message"])

    def test_secret_is_optional(self):
        self.assertFalse(json.loads(execute('{"name":"Anna"}'))["secret_loaded"])

    def test_secret_value_does_not_reach_output_or_logs(self):
        secret = "test-sentinel-never-log-this-value"
        with self.assertLogs(LOGGER_NAME, level="INFO") as logs:
            result = execute(
                '{"name":"Anna","check_secret":true}',
                constants={"EXAMPLE_API_TOKEN": secret},
            )
        self.assertTrue(json.loads(result)["secret_loaded"])
        self.assertNotIn(secret, result)
        self.assertNotIn(secret, "\n".join(logs.output))

    def test_missing_requested_secret_fails(self):
        with self.assertRaises(KeyError):
            execute('{"name":"Anna","check_secret":true}')

    def test_empty_requested_secret_fails(self):
        with self.assertRaises(ValueError):
            execute('{"name":"Anna","check_secret":true}', constants={"EXAMPLE_API_TOKEN": ""})

    def test_invalid_input_is_rejected(self):
        for data in ["", "not-json", "[]", "null", '{"name":null}', '{"name":42}', '{"name":""}', '{"name":"  "}']:
            with self.subTest(data=data), self.assertRaises(ValueError):
                execute(data)

    def test_secret_flag_must_be_boolean(self):
        for flag in ["true", 1, None, []]:
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                execute(json.dumps({"name": "Anna", "check_secret": flag}))

    def test_output_matches_declared_contract(self):
        metadata = json.loads((ROOT / "methods/template-hello.json").read_text(encoding="utf-8"))
        result = json.loads(execute('{"name":"Anna"}'))
        self.assertTrue(set(metadata["out"]["required"]).issubset(result))
        self.assertIsInstance(result["message"], str)
        self.assertIsInstance(result["secret_loaded"], bool)


if __name__ == "__main__":
    unittest.main()
