#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p reports
printf '\n=== Исправленные переводы ===\n'
python3 transfer_fixed.py | tee reports/transfer_fixed_result.txt
printf '\n=== Алгоритм банкира ===\n'
python3 banker.py | tee reports/banker_result.txt
printf '\nОригинальная версия намеренно зависает — для её диагностики отдельно запустите:\n  python3 transfer_deadlock.py\n'
