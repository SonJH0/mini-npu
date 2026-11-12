import copy
import json
from pathlib import Path
from unittest.mock import mock_open, patch

from main import classify, run_json


def check_epsilon():
    """작은 점수 차이를 올바르게 비교하는지 확인합니다."""
    print("\n===== epsilon 비교 검증 =====")

    cases = [
        ("완전히 같은 점수", 1.0, 1.0, "UNDECIDED"),
        ("epsilon보다 작은 차이", 1.0 + 5e-10, 1.0, "UNDECIDED"),
        ("epsilon보다 큰 차이", 1.0 + 2e-9, 1.0, "A"),
        ("B 점수가 더 큰 경우", 1.0, 2.0, "B"),
    ]

    passed = 0

    for name, score_a, score_b, expected in cases:
        actual = classify(score_a, score_b)

        if actual == expected:
            passed += 1
            print(f"PASS | {name} | 결과: {actual}")
        else:
            print(
                f"FAIL | {name} | "
                f"예상: {expected}, 실제: {actual}"
            )

    print(f"epsilon 검증: 전체 {len(cases)}개 / 통과 {passed}개")


def main():
    path = Path(__file__).resolve().parent / "data.json"

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            original = json.load(file)
    except (OSError, ValueError) as error:
        print(f"data.json 읽기 오류: {error}")
        return

    # 원본 대신 복사본에 오류 데이터를 추가합니다.
    data = copy.deepcopy(original)
    patterns = data["patterns"]

    # 1. 5×5여야 하는데 행이 4개인 패턴
    patterns["size_5_3"] = {
        "input": copy.deepcopy(patterns["size_5_1"]["input"][:-1]),
        "expected": "+",
    }

    # 2. 지원하지 않는 정답 라벨
    patterns["size_5_4"] = {
        "input": copy.deepcopy(patterns["size_5_1"]["input"]),
        "expected": "triangle",
    }

    # 3. 키 형식 오류
    patterns["wrong_key"] = {
        "input": copy.deepcopy(patterns["size_5_1"]["input"]),
        "expected": "+",
    }

    # 4. expected 항목 누락
    patterns["size_5_5"] = {
        "input": copy.deepcopy(patterns["size_5_1"]["input"]),
    }

    # 5. 모든 칸이 1이므로 두 필터가 동점
    patterns["size_5_6"] = {
        "input": [[1 for _ in range(5)] for _ in range(5)],
        "expected": "+",
    }

    # 오류 케이스 뒤에도 정상 분석이 계속되는지 확인
    patterns["size_5_99"] = copy.deepcopy(patterns["size_5_1"])

    print("===== 오류 데이터 분석 검증 =====")
    print("원본 data.json은 변경하지 않습니다.")
    print("프로그램에 임시 데이터를 전달해 분석합니다.")
    print("기본 데이터 6개 기준 예상: 전체 12개 / 통과 7개 / 실패 5개")

    # run_json이 파일을 읽는 동안에만 임시 데이터를 제공합니다.
    temporary_json = json.dumps(data, ensure_ascii=False)

    with patch("main.Path.open", mock_open(read_data=temporary_json)):
        run_json()

    check_epsilon()


if __name__ == "__main__":
    main()