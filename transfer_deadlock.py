"""Проект 2, блок A. Переводы между счетами.

Два кассира одновременно переводят деньги: первый со счёта A на счёт B,
второй со счёта B на счёт A. Каждый блокирует оба счёта, чтобы перевод был атомарным.

Запуск:  python3 transfer_deadlock.py
Через 5 секунд faulthandler выведет, на какой строке ждёт каждый поток, и завершит программу.
"""
import faulthandler
import threading
import time

faulthandler.dump_traceback_later(5, exit=True)   # «чёрный ящик»: через 5 с печатает стеки всех потоков

accounts = {"A": 1000, "B": 1000}
locks = {"A": threading.Lock(), "B": threading.Lock()}


def transfer(src, dst, amount, n):
    for _ in range(n):
        with locks[src]:
            time.sleep(0.001)          # имитация проверки баланса
            with locks[dst]:
                accounts[src] -= amount
                accounts[dst] += amount


t1 = threading.Thread(target=transfer, args=("A", "B", 10, 100), name="кассир-1")
t2 = threading.Thread(target=transfer, args=("B", "A", 10, 100), name="кассир-2")
t1.start(); t2.start()
t1.join(); t2.join()

faulthandler.cancel_dump_traceback_later()
print("Готово:", accounts, "сумма =", sum(accounts.values()))
