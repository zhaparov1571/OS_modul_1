"""Блок A, задание 3: алгоритм банкира для bank_state.txt и bank_state2.txt.

Каждый процесс должен завершиться, получив не более своего Need = Max - Allocation.
Безопасная последовательность существует => SAFE; иначе UNSAFE.
"""
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent


@dataclass
class State:
    available: list[int]
    allocation: dict[str, list[int]]
    maximum: dict[str, list[int]]


def read_state(path: Path) -> State:
    sections: dict[str, list[str]] = {"Available": [], "Allocation": [], "Max": []}
    section = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.endswith(":"):
            section = line[:-1]
            if section not in sections:
                raise ValueError(f"Неизвестная секция {section} в {path.name}")
        elif section is None:
            raise ValueError("Строка вне секции: " + line)
        else:
            sections[section].append(line)

    if len(sections["Available"]) != 1:
        raise ValueError("Available должна содержать ровно одну строку")
    available = list(map(int, sections["Available"][0].split()))
    n = len(available)

    def parse_processes(lines: list[str]) -> dict[str, list[int]]:
        result = {}
        for line in lines:
            pid, *numbers = line.split()
            values = list(map(int, numbers))
            if pid in result or len(values) != n:
                raise ValueError("Неверная строка процесса: " + line)
            result[pid] = values
        return result

    allocation = parse_processes(sections["Allocation"])
    maximum = parse_processes(sections["Max"])
    if allocation.keys() != maximum.keys():
        raise ValueError("Наборы PID в Allocation и Max различаются")
    if any(x < 0 for x in available):
        raise ValueError("Available не может быть отрицательным")
    for pid in allocation:
        if any(a < 0 or m < a for a, m in zip(allocation[pid], maximum[pid])):
            raise ValueError("Max должен быть >= Allocation: " + pid)
    return State(available, allocation, maximum)


def check_safety(state: State) -> tuple[bool, list[str], list[str]]:
    """Вернуть (SAFE?, порядок завершения, незавершённые процессы)."""
    work = state.available.copy()
    remaining = list(state.allocation)
    sequence = []
    while True:
        advanced = False
        for pid in remaining[:]:
            need = [m - a for m, a in zip(state.maximum[pid], state.allocation[pid])]
            if all(needed <= free for needed, free in zip(need, work)):
                work = [free + held for free, held in zip(work, state.allocation[pid])]
                remaining.remove(pid)
                sequence.append(pid)
                advanced = True
        if not advanced:
            break
    return not remaining, sequence, remaining


def check_requests(original: State, path: Path) -> None:
    print("\nЗапросы из requests.txt (все независимо от исходного состояния):")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        pid, *values = line.split()
        request = list(map(int, values))
        if pid not in original.allocation or len(request) != len(original.available) or any(x < 0 for x in request):
            raise ValueError("Неверный запрос: " + line)
        need = [m - a for m, a in zip(original.maximum[pid], original.allocation[pid])]
        prefix = f"{pid} {request}: "
        if any(r > n for r, n in zip(request, need)):
            print(prefix + "ОШИБКА: запрос превышает Max - Allocation (Need)")
            continue
        if any(r > a for r, a in zip(request, original.available)):
            print(prefix + "ОЖИДАНИЕ: недостаточно Available")
            continue
        trial = State(
            available=[a - r for a, r in zip(original.available, request)],
            allocation={p: held.copy() for p, held in original.allocation.items()},
            maximum=original.maximum,
        )
        trial.allocation[pid] = [a + r for a, r in zip(trial.allocation[pid], request)]
        safe, sequence, _ = check_safety(trial)
        if safe:
            print(prefix + "ВЫДАТЬ: безопасно; " + " -> ".join(sequence))
        else:
            print(prefix + "ОТКАЗАТЬ: UNSAFE после выдачи")


def main() -> None:
    for filename in ("bank_state.txt", "bank_state2.txt"):
        state = read_state(ROOT / filename)
        safe, sequence, remaining = check_safety(state)
        print(f"{filename}: Available={state.available}")
        print("Need = Max - Allocation:")
        for pid in state.allocation:
            need = [m - a for m, a in zip(state.maximum[pid], state.allocation[pid])]
            print(f"  {pid}: {need}")
        if safe:
            print("SAFE: " + " -> ".join(sequence))
        else:
            print("UNSAFE: полная безопасная последовательность отсутствует")
            print("  Можно завершить: " + (" -> ".join(sequence) or "никого"))
            print("  Оставшиеся: " + ", ".join(remaining))
        print()
    check_requests(read_state(ROOT / "bank_state.txt"), ROOT / "requests.txt")


if __name__ == "__main__":
    main()
