from typing import TypeVar

T = TypeVar("T")


def get(arr: list[T], index: int) -> T | None:
    try:
        return arr[index]
    except IndexError:
        return None


def get_file_at_path(
    path: str,
):
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        print("The file was not found.")
    except IOError:
        print("An error occurred while reading the file.")


def create_file_at_path(
    path: str,
    content: str,
):
    with open(path, "w") as f:
        f.write(content)
