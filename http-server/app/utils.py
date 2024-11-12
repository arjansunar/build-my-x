from typing import TypeVar

T = TypeVar("T")


def get(arr: list[T], index: int) -> T | None:
    try:
        return arr[index]
    except IndexError:
        return None
