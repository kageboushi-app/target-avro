import subprocess
import sys

from typing import Callable


def _sys_exit(func: Callable[[], int]):
    def wrapper():
        code = func()
        if code != 0:
            sys.exit(code)

    return wrapper


@_sys_exit
def test() -> int:
    return subprocess.run(["python", "-u", "-m", "unittest", "discover"]).returncode


@_sys_exit
def lint() -> int:
    return subprocess.run(["mypy", "target_avro", "tests"]).returncode


@_sys_exit
def fmt() -> int:
    return max(
        subprocess.run(["isort", "."]).returncode,
        subprocess.run(["black", "."]).returncode,
    )
