#!/usr/bin/env python3

from os import environ, getcwd
from os.path import isdir
from subprocess import run


def call(prog: str, *args: str, cwd: str = getcwd()) -> None:
    ret = run((prog, *args), cwd=cwd)
    if ret.returncode != 0:
        exit(ret.returncode)


def get_branch() -> str:
    ref = environ["GITHUB_REF"]
    return ref.replace("refs/heads/", "")


def git_clone(name: str) -> None:
    if not isdir(name):
        token = environ["CI_TOKEN"]
        uri = f"https://ms-jpq:{token}@github.com/ms-jpq/chadtree.git"
        email = "ci@ci.ci"
        username = "ci-bot"
        branch = get_branch()
        call("git", "clone", "--single-branch", "--branch", branch, uri, name)
        call("git", "config", "user.email", email, cwd=name)
        call("git", "config", "user.name", username, cwd=name)


def build() -> None:
    call("./temp/ci/build.py")


def main() -> None:
    git_clone("temp")
    build()


main()
