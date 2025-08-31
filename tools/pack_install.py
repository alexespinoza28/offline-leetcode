"""
Problem pack installation and validation tool.

This script provides functionality for installing and validating problem packs.
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, Any

# Add orchestrator to path to import modules
sys.path.append(str(Path(__file__).parent.parent / "orchestrator"))

from orchestrator.db import ProgressDB


from packaging.version import parse as parse_version


class PackInstaller:
    """Installs and validates problem packs."""

    def __init__(self, problems_dir: str = "problems", packs_dir: str = "packs"):
        self.problems_dir = Path(problems_dir)
        self.packs_dir = Path(packs_dir)
        self.db = ProgressDB()

    def install_pack(self, pack_path: Path) -> bool:
        """Installs a problem pack."""
        print(f"Installing pack: {pack_path.name}")

        if not pack_path.exists() or not pack_path.is_dir():
            print(f"Error: Pack path does not exist or is not a directory: {pack_path}", file=sys.stderr)
            return False

        pack_json_path = pack_path / "pack.json"
        if not pack_json_path.exists():
            print(f"Error: pack.json not found in {pack_path}", file=sys.stderr)
            return False

        with open(pack_json_path, "r") as f:
            try:
                pack_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in pack.json: {e}", file=sys.stderr)
                return False

        if not self._validate_pack_schema(pack_data):
            return False

        packs = self.db.get_user_setting("packs", {})
        if pack_data["name"] in packs:
            installed_version = parse_version(packs[pack_data["name"]]["version"])
            new_version = parse_version(pack_data["version"])
            if new_version <= installed_version:
                print(
                    f"Error: A newer or equal version of pack '{pack_data['name']}' is already installed.",
                    file=sys.stderr,
                )
                return False

        if not self._install_problems(pack_path, pack_data):
            return False

        self._register_pack(pack_data)

        print(f"Pack '{pack_data['name']}' installed successfully.")
        return True

    def _validate_pack_schema(self, pack_data: Dict[str, Any]) -> bool:
        """Validates the pack.json schema."""
        required_keys = ["name", "version", "description", "author", "problems"]
        for key in required_keys:
            if key not in pack_data:
                print(f"Error: Missing required key in pack.json: {key}", file=sys.stderr)
                return False
        return True

    def _install_problems(self, pack_path: Path, pack_data: Dict[str, Any]) -> bool:
        """Installs the problems from a pack."""
        for problem_slug in pack_data["problems"]:
            problem_src_dir = pack_path / problem_slug
            problem_dest_dir = self.problems_dir / problem_slug

            if not problem_src_dir.exists() or not problem_src_dir.is_dir():
                print(f"Error: Problem directory not found in pack: {problem_slug}", file=sys.stderr)
                return False

            if problem_dest_dir.exists():
                print(f"Warning: Problem already exists: {problem_slug}. Overwriting.")
                shutil.rmtree(problem_dest_dir)

            shutil.copytree(problem_src_dir, problem_dest_dir)
            print(f"  - Installed problem: {problem_slug}")

        return True

    def _register_pack(self, pack_data: Dict[str, Any]):
        """Registers the installed pack in the database."""
        packs = self.db.get_user_setting("packs", {})
        packs[pack_data["name"]] = pack_data
        self.db.set_user_setting("packs", packs)

    def remove_pack(self, pack_name: str) -> bool:
        """Removes an installed problem pack."""
        print(f"Removing pack: {pack_name}")

        packs = self.db.get_user_setting("packs", {})
        if pack_name not in packs:
            print(f"Error: Pack not found: {pack_name}", file=sys.stderr)
            return False

        pack_data = packs[pack_name]

        if not self._remove_problems(pack_data):
            return False

        del packs[pack_name]
        self.db.set_user_setting("packs", packs)

        print(f"Pack '{pack_name}' removed successfully.")
        return True

    def _remove_problems(self, pack_data: Dict[str, Any]) -> bool:
        """Removes the problems from a pack."""
        for problem_slug in pack_data["problems"]:
            problem_dest_dir = self.problems_dir / problem_slug
            if problem_dest_dir.exists():
                shutil.rmtree(problem_dest_dir)
                print(f"  - Removed problem: {problem_slug}")
        return True

    def list_packs(self):
        """Lists all installed packs."""
        print("Installed packs:")
        packs = self.db.get_user_setting("packs", {})
        if not packs:
            print("  No packs installed.")
            return

        for pack_name, pack_data in packs.items():
            print(f"  - {pack_name} (version {pack_data['version']})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Problem pack installation tool.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Install command
    install_parser = subparsers.add_parser("install", help="Install a problem pack.")
    install_parser.add_argument("pack_path", help="Path to the problem pack directory.")

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove an installed pack.")
    remove_parser.add_argument("pack_name", help="Name of the pack to remove.")

    # List command
    list_parser = subparsers.add_parser("list", help="List installed packs.")

    parser.add_argument(
        "--problems-dir",
        default="problems",
        help="Path to the problems directory.",
    )
    parser.add_argument(
        "--packs-dir",
        default="packs",
        help="Path to the packs directory.",
    )
    args = parser.parse_args()

    installer = PackInstaller(args.problems_dir, args.packs_dir)

    if args.command == "install":
        if not installer.install_pack(Path(args.pack_path)):
            sys.exit(1)
    elif args.command == "list":
        installer.list_packs()
    elif args.command == "remove":
        if not installer.remove_pack(args.pack_name):
            sys.exit(1)
