import json
from pathlib import Path


def validate_size(size):
    """패턴 크기는 양의 홀수만 허용합니다."""
    if type(size) is not int or size <= 0 or size % 2 == 0:
        raise ValueError("크기는 1 이상의 홀수여야 합니다.")


def generate_cross(size):
    """가운데 행과 가운데 열이 1인 십자가를 생성합니다."""
    validate_size(size)

    matrix = []
    center = size // 2

    for row in range(size):
        line = []

        for col in range(size):
            if row == center or col == center:
                line.append(1)
            else:
                line.append(0)

        matrix.append(line)

    return matrix


def generate_x(size):
    """두 대각선이 1인 X 패턴을 생성합니다."""
    validate_size(size)

    matrix = []

    for row in range(size):
        line = []

        for col in range(size):
            if row == col or row + col == size - 1:
                line.append(1)
            else:
                line.append(0)

        matrix.append(line)

    return matrix


def print_pattern(name, matrix):
    print("\n" + name)

    for row in matrix:
        print(" ".join(str(value) for value in row))


def preview_patterns():
    """사용자가 입력한 크기로 패턴을 생성합니다."""
    while True:
        text = input("\n패턴 크기 N 입력 (양의 홀수, 0은 취소): ")

        try:
            size = int(text)
        except ValueError:
            print("정수를 입력하세요. 예: 3, 5, 7")
            continue

        if size == 0:
            return

        try:
            validate_size(size)
        except ValueError as error:
            print(error)
            continue

        cross = generate_cross(size)
        x_pattern = generate_x(size)

        print_pattern(f"{size}×{size} 십자가", cross)
        print_pattern(f"{size}×{size} X", x_pattern)
        print("\n패턴 생성 완료!")
        return


def create_sample_data():
    """정상 패턴 6개를 가진 연습용 JSON을 생성합니다."""
    data = {
        "filters": {},
        "patterns": {},
    }

    for size in (5, 13, 25):
        data["filters"][f"size_{size}"] = {
            "cross": generate_cross(size),
            "x": generate_x(size),
        }

        data["patterns"][f"size_{size}_1"] = {
            "input": generate_cross(size),
            "expected": "+",
        }

        data["patterns"][f"size_{size}_2"] = {
            "input": generate_x(size),
            "expected": "x",
        }

    path = Path(__file__).resolve().parent / "data.json"

    try:
        with path.open("x", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except FileExistsError:
        print("\ndata.json이 이미 있습니다. 기존 파일을 유지합니다.")
        return
    except OSError as error:
        print(f"\n파일 저장 오류: {error}")
        return

    print("\n연습용 data.json 생성 완료!")
    print("필터 크기: 5×5, 13×13, 25×25")
    print("전체 패턴 수:", len(data["patterns"]))
    print("저장 위치:", path)


def main():
    print("패턴 생성기")

    while True:
        print("\n1. 크기 N을 입력해 십자가와 X 생성")
        print("2. 연습용 data.json 생성")
        print("0. 종료")

        choice = input("선택: ").strip()

        if choice == "1":
            preview_patterns()
        elif choice == "2":
            create_sample_data()
        elif choice == "0":
            print("패턴 생성기를 종료합니다.")
            break
        else:
            print("0, 1, 2 중 하나를 입력하세요.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n패턴 생성기를 종료했습니다.")