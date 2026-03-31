from __future__ import annotations

from collections.abc import MutableMapping
from functools import lru_cache

import pandas as pd


TRACE_COLUMNS = [
    "original_number",
    "capture_iteration",
    "capture_state",
    "capture_number",
]


def next_collatz(number: int) -> int:
    if number < 1:
        raise ValueError("Collatz inputs must be positive integers.")
    return number // 2 if number % 2 == 0 else (3 * number) + 1


def two_adic_valuation(number: int) -> int:
    if number < 1:
        raise ValueError("2-adic valuation is defined here for positive integers only.")

    valuation = 0
    current = int(number)
    while current % 2 == 0:
        current //= 2
        valuation += 1
    return valuation


@lru_cache(maxsize=None)
def collatz_values(number: int) -> tuple[int, ...]:
    if number < 1:
        raise ValueError("Collatz inputs must be positive integers.")

    values = [int(number)]
    current = int(number)
    while current != 1:
        current = next_collatz(current)
        values.append(current)
    return tuple(values)


def collatz_full(number: int) -> list[dict[str, int | str]]:
    trajectory = collatz_values(number)
    return [
        {
            "original_number": int(number),
            "iteration_index": iteration_index,
            "value": value,
            "state": "EVEN" if value % 2 == 0 else "ODD",
        }
        for iteration_index, value in enumerate(trajectory)
    ]


def collatz_stopping_time(number: int) -> int:
    return len(collatz_values(number)) - 1


def collatz_peak(number: int) -> tuple[int, int]:
    trajectory = collatz_values(number)
    peak_value = max(trajectory)
    peak_iteration = trajectory.index(peak_value)
    return peak_value, peak_iteration


def collatz_2adic_profile(number: int) -> list[int]:
    trajectory = collatz_values(number)
    return [two_adic_valuation(value) for value in trajectory]


def calc(number: int) -> pd.DataFrame:
    """Python port of the original R calc() function."""
    if number < 1:
        raise ValueError("Collatz inputs must be positive integers.")

    original_number = int(number)
    rows: list[dict[str, int | str]] = []
    current = original_number
    iteration = 1

    if current == 1:
        rows.append(
            {
                "original_number": original_number,
                "capture_iteration": 1,
                "capture_state": "END",
                "capture_number": 1,
            }
        )
        return pd.DataFrame(rows, columns=TRACE_COLUMNS)

    while current != 1:
        rows.append(
            {
                "original_number": original_number,
                "capture_iteration": iteration,
                "capture_state": "EVEN" if current % 2 == 0 else "ODD",
                "capture_number": current,
            }
        )
        current = next_collatz(current)
        iteration += 1

    rows.append(
        {
            "original_number": original_number,
            "capture_iteration": iteration,
            "capture_state": "END",
            "capture_number": 1,
        }
    )
    return pd.DataFrame(rows, columns=TRACE_COLUMNS)


def trace_length_inclusive(
    number: int, cache: MutableMapping[int, int] | None = None
) -> int:
    """
    Return the inclusive trace length used by the R analysis.

    This counts the starting value and the terminal 1, so 2 -> 2 and 3 -> 8.
    """
    if number < 1:
        raise ValueError("Collatz inputs must be positive integers.")

    if cache is None:
        cache = {1: 1}
    elif 1 not in cache:
        cache[1] = 1

    if number in cache:
        return cache[number]

    path: list[int] = []
    current = int(number)
    while current not in cache:
        path.append(current)
        current = next_collatz(current)

    length = cache[current]
    for value in reversed(path):
        length += 1
        cache[value] = length

    return cache[number]
