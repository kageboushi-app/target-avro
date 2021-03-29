import subprocess
import sys


def test():
    p = subprocess.run(["python", "-u", "-m", "unittest", "discover"])
    if p.returncode != 0:
        sys.exit(p.returncode)


def lint():
    subprocess.run(["mypy", "target_avro", "tests"])


def fmt():
    subprocess.run(["isort", "."])
    subprocess.run(["black", "."])
