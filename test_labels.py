import unittest

from create_data import generate_cross, generate_x
from main import analyze_case, get_filters, normalize_label


# 새 별칭을 지원하면 (입력 표기, 표준 라벨) 사례를 여기에 추가합니다.
LABEL_CASES = [
    ("+", "Cross"),
    ("cross", "Cross"),
    ("Cross", "Cross"),
    (" CROSS ", "Cross"),
    ("x", "X"),
    ("X", "X"),
    (" x ", "X"),
]


class LabelPolicyTests(unittest.TestCase):
    def test_supported_spellings(self):
        for source, expected in LABEL_CASES:
            with self.subTest(source=source):
                self.assertEqual(normalize_label(source), expected)

    def test_unknown_labels_are_rejected(self):
        for source in ("triangle", "", "plus"):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    normalize_label(source)

    def test_non_string_labels_are_rejected(self):
        for source in (None, 1, True, [], {}):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    normalize_label(source)

    def test_filter_aliases_and_expected_share_policy(self):
        filters = {
            "size_3": {
                " + ": generate_cross(3),
                " X ": generate_x(3),
            }
        }
        self.assertEqual(set(get_filters(filters, 3)), {"Cross", "X"})
        case = {"input": generate_cross(3), "expected": " CROSS "}
        success, reason = analyze_case("size_3_1", case, filters)
        self.assertTrue(success, reason)

    def test_duplicate_aliases_are_rejected(self):
        filters = {
            "size_3": {
                "cross": generate_cross(3),
                "+": generate_cross(3),
                "x": generate_x(3),
            }
        }
        with self.assertRaisesRegex(ValueError, "중복"):
            get_filters(filters, 3)


if __name__ == "__main__":
    unittest.main()
