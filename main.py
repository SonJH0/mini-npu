import json
import math
import re
import time
from pathlib import Path

from create_data import generate_cross

EPSILON = 1e-9
REPEATS = 1000


def mac_2d(pattern, filter_matrix):
    """같은 위치의 숫자끼리 곱하고 모두 더합니다."""
    total = 0.0

    for row in range(len(pattern)):
        for col in range(len(pattern[row])):
            total += pattern[row][col] * filter_matrix[row][col]

    return total


def classify(score_a, score_b, label_a="A", label_b="B"):
    """유효한 점수를 epsilon 기준으로 비교합니다."""
    if not math.isfinite(score_a) or not math.isfinite(score_b):
        raise ValueError("연산 결과가 유효한 유한수가 아닙니다.")

    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"

    if score_a > score_b:
        return label_a

    return label_b


def normalize_label(label):
    """라벨 표기를 Cross 또는 X로 통일합니다."""
    if not isinstance(label, str):
        raise ValueError("라벨은 문자열이어야 합니다.")

    labels = {
        "+": "Cross",
        "cross": "Cross",
        "x": "X",
    }

    normalized = labels.get(label.strip().lower())

    if normalized is None:
        raise ValueError(f"지원하지 않는 라벨: {label!r}")

    return normalized


def validate_matrix(matrix, size, name):
    """배열의 행·열 개수와 숫자 값을 검증합니다."""
    if not isinstance(matrix, list) or len(matrix) != size:
        raise ValueError(f"{name}: 행 개수가 {size}개여야 합니다.")

    for row_index, row in enumerate(matrix, start=1):
        if not isinstance(row, list) or len(row) != size:
            raise ValueError(
                f"{name}: {row_index}행의 열 개수가 {size}개여야 합니다."
            )

        for value in row:
            if type(value) not in (int, float):
                raise ValueError(f"{name}: 숫자가 아닌 값이 있습니다.")

            try:
                finite = math.isfinite(value)
            except OverflowError:
                finite = False

            if not finite:
                raise ValueError(f"{name}: 유효한 유한수만 사용할 수 있습니다.")


def read_matrix(size, name):
    """잘못 입력한 행은 다시 요청합니다."""
    matrix = []
    print(f"\n{name}: 각 줄에 숫자 {size}개를 입력하세요.")

    for row_index in range(size):
        while True:
            parts = input(f"{row_index + 1}/{size}행: ").split()

            if len(parts) != size:
                print(f"입력 형식 오류: 숫자 {size}개를 입력하세요.")
                continue

            try:
                row = [float(value) for value in parts]
            except ValueError:
                print("입력 형식 오류: 숫자만 입력하세요.")
                continue

            if not all(math.isfinite(value) for value in row):
                print("입력 형식 오류: nan, inf는 사용할 수 없습니다.")
                continue

            matrix.append(row)
            break

    return matrix


def print_matrix(title, matrix):
    print("\n" + title)

    for row in matrix:
        print(" ".join(f"{value:g}" for value in row))


def measure_average_ms(pattern, filter_matrix):
    """入出力を含めず、MAC呼び出しの平均時間を測定します。"""
    for _ in range(10):
        mac_2d(pattern, filter_matrix)

    total_seconds = 0.0

    for _ in range(REPEATS):
        start = time.perf_counter()
        mac_2d(pattern, filter_matrix)
        total_seconds += time.perf_counter() - start

    return total_seconds / REPEATS * 1000


def print_performance(sizes):
    print("\n성능 분석")
    print(f"생성한 십자가 패턴과 필터 하나로 크기별 {REPEATS}회 측정")
    print("입력·출력·파일 읽기·패턴 생성 시간은 제외합니다.")
    print(f"{'크기':<10} {'평균 시간(ms)':>15} {'MAC 횟수(N²)':>15}")

    for size in sizes:
        pattern = generate_cross(size)
        filter_matrix = generate_cross(size)

        average_ms = measure_average_ms(pattern, filter_matrix)

        print(
            f"{str(size) + 'x' + str(size):<10} "
            f"{average_ms:>15.6f} "
            f"{size * size:>15}"
        )


def run_manual():
    filter_a = read_matrix(3, "필터 A 입력")
    filter_b = read_matrix(3, "필터 B 입력")

    print_matrix("저장된 필터 A", filter_a)
    print_matrix("저장된 필터 B", filter_b)

    pattern = read_matrix(3, "패턴 입력")
    print_matrix("저장된 입력 패턴", pattern)

    try:
        start = time.perf_counter()
        score_a = mac_2d(pattern, filter_a)
        score_b = mac_2d(pattern, filter_b)
        elapsed_ms = (time.perf_counter() - start) * 1000

        result = classify(score_a, score_b)
    except (ValueError, OverflowError) as error:
        print(f"\n계산 오류: {error}")
        return

    print("\nMAC 계산 결과")
    print(f"A 점수: {score_a:g}")
    print(f"B 점수: {score_b:g}")
    print(f"두 필터 MAC 연산 시간: {elapsed_ms:.6f} ms")
    print("최종 판정:", result)

    print_performance((3,))


def get_filters(filters, size):
    """크기에 맞는 필터를 선택하고 키를 정규화합니다."""
    group = filters.get(f"size_{size}")

    if not isinstance(group, dict):
        raise ValueError(f"size_{size} 필터 묶음이 없거나 형식이 잘못됐습니다.")

    normalized = {}

    for key, matrix in group.items():
        label = normalize_label(key)

        if label in normalized:
            raise ValueError(f"{label} 필터가 중복되었습니다.")

        validate_matrix(matrix, size, f"{label} 필터")
        normalized[label] = matrix

    if set(normalized) != {"Cross", "X"}:
        raise ValueError("Cross와 X 필터가 모두 필요합니다.")

    return normalized


def analyze_case(case_id, case, filters):
    match = re.fullmatch(r"size_([1-9]\d*)_([1-9]\d*)", case_id)

    if match is None:
        raise ValueError("패턴 키는 size_N_idx 형식이어야 합니다.")

    size = int(match.group(1))

    if not isinstance(case, dict):
        raise ValueError("패턴 항목은 객체 형식이어야 합니다.")

    if "input" not in case or "expected" not in case:
        raise ValueError("input 또는 expected가 없습니다.")

    pattern = case["input"]
    validate_matrix(pattern, size, "입력 패턴")

    expected = normalize_label(case["expected"])
    selected = get_filters(filters, size)

    cross_score = mac_2d(pattern, selected["Cross"])
    x_score = mac_2d(pattern, selected["X"])
    predicted = classify(cross_score, x_score, "Cross", "X")

    print(
        f"\n{case_id} | Cross 점수: {cross_score:g} "
        f"| X 점수: {x_score:g}"
    )
    print(f"판정: {predicted} | 정답: {expected}")

    if predicted == expected:
        return True, ""

    if predicted == "UNDECIDED":
        return False, f"epsilon 기준 동점: 정답은 {expected}"

    return False, f"판정 {predicted}와 정답 {expected}가 다릅니다."


def run_json():
    path = Path(__file__).resolve().parent / "data.json"

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)
    except (OSError, ValueError) as error:
        print(f"\n파일 읽기 오류: {error}")
        return

    if not isinstance(data, dict):
        print("데이터 구조 오류: 최상위 값은 객체여야 합니다.")
        return

    patterns = data.get("patterns")

    if not isinstance(patterns, dict):
        print("데이터 구조 오류: patterns 객체가 필요합니다.")
        return

    filters = data.get("filters")
    failures = []
    passed = 0

    print("\ndata.json 분석 시작")

    for case_id, case in patterns.items():
        try:
            if not isinstance(filters, dict):
                raise ValueError("filters 객체가 없거나 형식이 잘못됐습니다.")

            success, reason = analyze_case(case_id, case, filters)
        except (ValueError, OverflowError) as error:
            success = False
            reason = f"데이터 또는 계산 오류: {error}"
            print(f"\n{case_id} | 점수·판정: 계산 불가")

        if success:
            passed += 1
            print("결과: PASS")
        else:
            failures.append((case_id, reason))
            print(f"결과: FAIL | 사유: {reason}")

    print_performance((3, 5, 13, 25))

    print("\n결과 요약")
    print("전체 테스트 수:", len(patterns))
    print("통과 수:", passed)
    print("실패 수:", len(failures))

    if failures:
        print("\n실패 케이스 목록")

        for case_id, reason in failures:
            print(f"- {case_id}: {reason}")
    else:
        print("실패 케이스 없음")

    if not patterns:
        print("주의: 패턴이 없어 실제로 분석한 케이스가 없습니다.")


def main():
    print("Mini NPU 시뮬레이터")

    while True:
        print("\n1. 사용자 입력 (3×3)")
        print("2. data.json 분석")
        print("0. 종료")

        choice = input("선택: ").strip()

        if choice == "1":
            run_manual()
        elif choice == "2":
            run_json()
        elif choice == "0":
            print("프로그램을 종료합니다.")
            break
        else:
            print("0, 1, 2 중 하나를 입력하세요.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n프로그램을 종료했습니다.")