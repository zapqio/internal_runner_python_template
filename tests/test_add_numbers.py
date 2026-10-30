import json
from pathlib import Path
import unittest

from tools.run_local import execute, LOGGER_NAME


ROOT = Path(__file__).resolve().parents[1]
METHOD = "template-add-numbers"


class AddNumbersTests(unittest.TestCase):
    def test_example_input_produces_documented_output(self):
        result = execute((ROOT / "examples/add-numbers-input.json").read_text(encoding="utf-8"), METHOD)
        expected = json.loads((ROOT / "examples/add-numbers-output.json").read_text(encoding="utf-8"))
        self.assertIsInstance(result, str)
        self.assertEqual(expected, json.loads(result))

    def test_zero_negative_and_fractional_numbers(self):
        for a, b, expected in [(0, 0, 0), (-7, 2, -5), (1.25, 2.5, 3.75), (2, 0.5, 2.5)]:
            with self.subTest(a=a, b=b):
                result = execute(json.dumps({"a": a, "b": b}), METHOD)
                self.assertEqual({"sum": expected}, json.loads(result))

    def test_integer_arithmetic_does_not_convert_to_float(self):
        result = execute(json.dumps({"a": 10 ** 400, "b": 1}), METHOD)
        self.assertEqual({"sum": 10 ** 400 + 1}, json.loads(result))

    def test_invalid_json_and_non_object_input_are_rejected(self):
        for data in ["", "not-json", "[]", "null", "2", "true"]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                execute(data, METHOD)

    def test_both_fields_are_required(self):
        for payload in [{}, {"a": 2}, {"b": 3}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                execute(json.dumps(payload), METHOD)

    def test_fields_must_be_finite_numbers(self):
        for field in ("a", "b"):
            for value in ["2", True, False, None, [], {}, float("nan"), float("inf"), float("-inf")]:
                payload = {"a": 2, "b": 3, field: value}
                with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, field):
                    execute(json.dumps(payload), METHOD)

    def test_float_overflow_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "sum"):
            execute('{"a": 1e308, "b": 1e308}', METHOD)

    def test_success_is_logged_separately_from_the_result(self):
        with self.assertLogs(LOGGER_NAME, level="INFO") as logs:
            result = execute('{"a": 2, "b": 3}', METHOD)
        self.assertEqual({"sum": 5}, json.loads(result))
        self.assertTrue(any("Numbers added." in entry for entry in logs.output))


if __name__ == "__main__":
    unittest.main()
