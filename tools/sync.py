"""
Git synchronization tool.

This script provides utilities for staging, committing, and pushing changes to the repository.
It also includes a pre-commit hook for running repository validation.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], cwd: Path = None) -> tuple[int, str, str]:
    """Runs a command and returns the exit code, stdout, and stderr."""
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
        )
        return process.returncode, process.stdout, process.stderr
    except FileNotFoundError:
        return -1, "", f"Command not found: {command[0]}"


def get_git_root() -> Path | None:
    """Returns the root directory of the Git repository."""
    exit_code, stdout, _ = run_command(["git", "rev-parse", "--show-toplevel"])
    if exit_code == 0:
        return Path(stdout.strip())
    return None


class GitSync:
    """Manages Git synchronization."""

    def __init__(self, git_root: Path):
        self.git_root = git_root

    def stage_changes(self, files: list[str] = None):
        """Stages the given files, or all changes if no files are given."""
        print("Staging changes...")
        command = ["git", "add"]
        if files:
            command.extend(files)
        else:
            command.append(".")
        exit_code, stdout, stderr = run_command(command, self.git_root)
        if exit_code != 0:
            print(f"Error staging changes: {stderr}", file=sys.stderr)
            sys.exit(1)
        print("Changes staged successfully.")

    def commit_changes(self, message: str):
        """Commits the staged changes with the given message."""
        print("Committing changes...")
        command = ["git", "commit", "-m", message]
        exit_code, stdout, stderr = run_command(command, self.git_root)
        if exit_code != 0:
            print(f"Error committing changes: {stderr}", file=sys.stderr)
            sys.exit(1)
        print("Changes committed successfully.")

    def push_changes(self, remote: str = "origin", branch: str = "main"):
        """Pushes the committed changes to the remote repository."""
        print("Pushing changes...")
        command = ["git", "push", remote, branch]
        exit_code, stdout, stderr = run_command(command, self.git_root)
        if exit_code != 0:
            print(f"Error pushing changes: {stderr}", file=sys.stderr)
            sys.exit(1)
        print("Changes pushed successfully.")


def pre_commit_hook():
    """Pre-commit hook to run repository validation."""
    print("Running pre-commit hook...")
    git_root = get_git_root()
    if not git_root:
        print("Not a Git repository. Skipping pre-commit hook.", file=sys.stderr)
        sys.exit(1)

    validator_path = git_root / "tools" / "validate_repo.py"
    if not validator_path.exists():
        print(f"Validator script not found at {validator_path}", file=sys.stderr)
        sys.exit(1)

    exit_code, stdout, stderr = run_command([sys.executable, str(validator_path)], git_root)
    if exit_code != 0:
        print("Repository validation failed:", file=sys.stderr)
        print(stdout, file=sys.stdout)
        print(stderr, file=sys.stderr)
        sys.exit(1)

    print("Repository validation passed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Git synchronization tool.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Staging command
    stage_parser = subparsers.add_parser("stage", help="Stage changes.")
    stage_parser.add_argument("files", nargs="*", help="Files to stage.")

    # Commit command
    commit_parser = subparsers.add_parser("commit", help="Commit changes.")
    commit_parser.add_argument("-m", "--message", required=True, help="Commit message.")

    # Push command
    push_parser = subparsers.add_parser("push", help="Push changes.")
    push_parser.add_argument("--remote", default="origin", help="Remote to push to.")
    push_parser.add_argument("--branch", default="main", help="Branch to push to.")

    # Pre-commit hook command
    pre_commit_parser = subparsers.add_parser(
        "pre-commit", help="Run pre-commit hook."
    )

    args = parser.parse_args()

    git_root = get_git_root()
    if not git_root:
        print("Not a Git repository.", file=sys.stderr)
        sys.exit(1)

    sync = GitSync(git_root)

    if args.command == "stage":
        sync.stage_changes(args.files)
    elif args.command == "commit":
        sync.commit_changes(args.message)
    elif args.command == "push":
        sync.push_changes(args.remote, args.branch)
    elif args.command == "pre-commit":
        pre_commit_hook()
