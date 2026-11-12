import time

from create_data import generate_cross, generate_x
from main import EPSILON, mac_2d

REPEATS = 1000
ROUNDS = 5


def flatten(matrix):
    """2차원 배열을 행 순서대로 펼칩니다."""
    result = []

    for row in matrix:
        for value in row:
            result.append(value)

    return result


def mac_1d(pattern, filter_values):
    """1차원 배열의 같은 위치 값을 곱하고 누적합니다."""
    total = 0.0

    for index in range(len(pattern)):
        total += pattern[index] * filter_values[index]

    return total


def measure_average_ms(function, pattern, filter_values):
    """동일한 반복 횟수로 MAC 호출 구간을 측정합니다."""
    total_seconds = 0.0

    for _ in range(REPEATS):
        start = time.perf_counter()
        function(pattern, filter_values)
        total_seconds += time.perf_counter() - start

    return total_seconds / REPEATS * 1000


def verify_scores(size):
    """Cross/X의 네 가지 조합에서 계산 결과를 확인합니다."""
    cross = generate_cross(size)
    x_pattern = generate_x(size)

    combinations = [
        (cross, cross),
        (cross, x_pattern),
        (x_pattern, cross),
        (x_pattern, x_pattern),
    ]

    for pattern, filter_matrix in combinations:
        score_2d = mac_2d(pattern, filter_matrix)
        score_1d = mac_1d(flatten(pattern), flatten(filter_matrix))

        if abs(score_2d - score_1d) >= EPSILON:
            raise ValueError(
                f"{size}×{size} 결과 불일치: "
                f"2차원={score_2d}, 1차원={score_1d}"
            )


def compare_size(size):
    verify_scores(size)

    pattern_2d = generate_cross(size)
    filter_2d = generate_cross(size)

    # 배열 변환은 시간 측정 전에 수행합니다.
    pattern_1d = flatten(pattern_2d)
    filter_1d = flatten(filter_2d)

    # 두 방식 모두 준비 실행
    for _ in range(10):
        mac_2d(pattern_2d, filter_2d)
        mac_1d(pattern_1d, filter_1d)

    times_2d = []
    times_1d = []

    # 측정 순서의 영향을 줄이기 위해 순서를 번갈아 바꿉니다.
    for round_index in range(ROUNDS):
        if round_index % 2 == 0:
            time_2d = measure_average_ms(
                mac_2d, pattern_2d, filter_2d
            )
            time_1d = measure_average_ms(
                mac_1d, pattern_1d, filter_1d
            )
        else:
            time_1d = measure_average_ms(
                mac_1d, pattern_1d, filter_1d
            )
            time_2d = measure_average_ms(
                mac_2d, pattern_2d, filter_2d
            )

        times_2d.append(time_2d)
        times_1d.append(time_1d)

    average_2d = sum(times_2d) / ROUNDS
    average_1d = sum(times_1d) / ROUNDS

    return average_2d, average_1d


def main():
    print("2차원 / 1차원 MAC 성능 비교")
    print(f"각 방식: 라운드당 {REPEATS}회 × {ROUNDS}라운드")
    print("동일한 십자가 패턴과 필터를 사용합니다.")
    print("패턴 생성·배열 변환·출력 시간은 제외합니다.")
    print("점수 일치는 크기별 Cross/X 네 가지 조합으로 확인합니다.")

    print(
        f"\n{'크기':<8} "
        f"{'2차원(ms)':>12} "
        f"{'1차원(ms)':>12} "
        f"{'시간 비율':>10} "
        f"{'MAC 횟수':>9}"
    )

    for size in (3, 5, 13, 25):
        average_2d, average_1d = compare_size(size)

        if average_1d > 0:
            ratio_text = f"{average_2d / average_1d:.2f}"
        else:
            ratio_text = "측정 불가"

        print(
            f"{str(size) + 'x' + str(size):<8} "
            f"{average_2d:>12.6f} "
            f"{average_1d:>12.6f} "
            f"{ratio_text:>10} "
            f"{size * size:>9}"
        )

    print("\n점수 일치 검증: 16개 조합 모두 PASS")
    print("시간 비율 = 2차원 평균 시간 ÷ 1차원 평균 시간")
    print("비율이 1보다 크면 이번 측정에서 1차원이 더 빠릅니다.")
    print("비율이 1보다 작으면 이번 측정에서 2차원이 더 빠릅니다.")
    print("두 방식의 시간 복잡도는 모두 O(N²)입니다.")


if __name__ == "__main__":
    main()