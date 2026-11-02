"""Блок A, задание 2: перевод без взаимоблокировки.

Всегда берём блокировки в одном глобальном порядке (A перед B).
Ни sleep, ни timeout для предотвращения deadlock не используются.
"""
import threading

accounts = {"A": 1000, "B": 1000}
locks = {name: threading.Lock() for name in accounts}


def transfer(src: str, dst: str, amount: int, n: int) -> None:
    if src == dst:
        raise ValueError("Счета отправителя и получателя должны отличаться")
    first, second = sorted((src, dst))  # Глобальный порядок: A, затем B.
    for _ in range(n):
        with locks[first]:
            with locks[second]:
                if accounts[src] < amount:
                    raise ValueError(f"Недостаточно денег на счёте {src}")
                accounts[src] -= amount
                accounts[dst] += amount


def main() -> None:
    t1 = threading.Thread(target=transfer, args=("A", "B", 10, 100), name="кассир-1")
    t2 = threading.Thread(target=transfer, args=("B", "A", 10, 100), name="кассир-2")
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    total = sum(accounts.values())
    print("Готово:", accounts, "сумма =", total)
    assert accounts == {"A": 1000, "B": 1000}, "Неверный баланс после переводов"
    assert total == 2000, "Нарушена сохранность суммы денег"
    print("Проверка: 200 переводов выполнены, deadlock отсутствует, общая сумма сохранена.")


if __name__ == "__main__":
    main()
