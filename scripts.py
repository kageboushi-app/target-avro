import subprocess


def test():
    subprocess.run(["python", "-u", "-m", "unittest", "discover"])


def lint():
    subprocess.run(["mypy", "target_avro", "tests"])


def fmt():
    subprocess.run(["isort", "."])
    subprocess.run(["black", "."])
