#!/usr/bin/env python3
"""
manage_slides.py

Insert or delete slide files in the `sections/` directory, maintaining
sequential numeric prefixes (NNN-*.md).

Usage (from repo root):

  # Insert:
  ./manage_slides.py insert <position> "Title or slug"

  # Delete:
  ./manage_slides.py delete <position>

Examples:

  ./manage_slides.py insert 3 "Multi-arch builds"
  ./manage_slides.py delete 5

Assumptions:
  - Slide files are named like: NNN-something.md (NNN = 3 digits)
  - All slide files are under ./sections
"""

import sys
import re
from pathlib import Path
from typing import NoReturn

SLIDES_DIR = Path("sections")
PATTERN = re.compile(r"^(\d{3})-(.+)\.md$")  # 3 digits now


def usage_and_exit(msg: str | None = None) -> NoReturn:
    prog = sys.argv[0] or "manage_slides.py"
    if msg:
        print(f"Error: {msg}", file=sys.stderr)
        print(file=sys.stderr)
    print("Usage:", file=sys.stderr)
    print(f"  {prog} insert <position> \"Title or slug\"", file=sys.stderr)
    print(f"  {prog} delete <position>", file=sys.stderr)
    print(file=sys.stderr)
    print("Examples:", file=sys.stderr)
    print(f"  {prog} insert 3 \"Multi-arch builds\"", file=sys.stderr)
    print(f"  {prog} delete 5", file=sys.stderr)
    sys.exit(1)


def slugify(text: str) -> str:
    text = text.strip().lower().replace(" ", "-")
    return re.sub(r"[^a-z0-9._-]", "", text)


def load_slides() -> list[tuple[int, str, Path]]:
    if not SLIDES_DIR.is_dir():
        sys.exit(
            f"Error: sections directory not found at '{SLIDES_DIR}'.\n"
            "manage_slides.py must be run from the repository root."
        )

    files: list[tuple[int, str, Path]] = []
    for path in SLIDES_DIR.iterdir():
        if not path.is_file():
            continue
        m = PATTERN.match(path.name)
        if not m:
            continue
        idx = int(m.group(1))
        rest = m.group(2)
        files.append((idx, rest, path))

    files.sort(key=lambda t: t[0])
    return files


def cmd_insert(position: int, title_or_slug: str) -> None:
    files = load_slides()
    slug = slugify(title_or_slug or f"slide-{position:03d}")  # 3 digits

    if position < 1:
        usage_and_exit("<position> must be >= 1")

    # No slides yet: just create this one
    if not files:
        new_file = SLIDES_DIR / f"{position:03d}-{slug}.md"    # 3 digits
        if new_file.exists():
            usage_and_exit(f"target file already exists: {new_file}")
        new_file.write_text(f"## {title_or_slug}\n\nNew slide.\n")
        print(f"Created {new_file}")
        return

    max_idx = max(idx for idx, _, _ in files)
    if position > max_idx + 1:
        print(
            f"Warning: inserting at position {position}, but highest existing index is "
            f"{max_idx:03d}. New slide will create a gap."
        )

    # Shift files with index >= position upward by 1, in descending order
    for idx, rest, path in sorted(files, key=lambda t: t[0], reverse=True):
        if idx < position:
            continue
        new_idx = idx + 1
        new_name = SLIDES_DIR / f"{new_idx:03d}-{rest}.md"     # 3 digits
        if new_name.exists():
            usage_and_exit(f"cannot rename {path} -> {new_name}, target already exists")
        print(f"Renaming {path.name} -> {new_name.name}")
        path.rename(new_name)

    # Create the new slide file at the desired position
    new_file = SLIDES_DIR / f"{position:03d}-{slug}.md"        # 3 digits
    if new_file.exists():
        usage_and_exit(f"new slide target already exists: {new_file}")

    content_lines = [
        f"## {title_or_slug}",
        "",
        "New slide.",
        ""
    ]
    new_file.write_text("\n".join(content_lines))
    print(f"Created {new_file}")


def cmd_delete(position: int) -> None:
    files = load_slides()
    if not files:
        usage_and_exit("no slides to delete")

    if position < 1:
        usage_and_exit("<position> must be >= 1")

    idxs = [idx for idx, _, _ in files]
    max_idx = max(idxs)

    if position > max_idx:
        usage_and_exit(
            f"requested delete position {position}, but highest existing index is "
            f"{max_idx:03d}"
        )

    # Find the file to delete
    to_delete = None
    for idx, rest, path in files:
        if idx == position:
            to_delete = (idx, rest, path)
            break

    if not to_delete:
        usage_and_exit(f"no slide found at position {position}")

    _, _, del_path = to_delete

    # Show the file that will be deleted and confirm
    print(f"About to delete: {del_path.name}")
    print("--- content preview ---")
    content = del_path.read_text()
    preview = content[:400] + ("..." if len(content) > 400 else "")
    print(preview)
    print("-----------------------")
    answer = input("Delete this slide? [y/N] ").strip().lower()
    if answer != "y":
        print("Aborted.")
        sys.exit(0)

    print(f"Deleting {del_path.name}")
    del_path.unlink()

    # Shift files with index > position downward by 1, in ascending order
    for idx, rest, path in sorted(files, key=lambda t: t[0]):
        if idx <= position:
            continue
        new_idx = idx - 1
        new_name = SLIDES_DIR / f"{new_idx:03d}-{rest}.md"     # 3 digits
        if new_name.exists():
            usage_and_exit(f"cannot rename {path} -> {new_name}, target already exists")
        print(f"Renaming {path.name} -> {new_name.name}")
        path.rename(new_name)


def main() -> None:
    if len(sys.argv) < 3:
        usage_and_exit()

    command = sys.argv[1]

    if command not in ("insert", "delete"):
        usage_and_exit(f"unknown command: {command!r}")

    try:
        position = int(sys.argv[2])
    except ValueError:
        usage_and_exit("<position> must be an integer (1-based index)")

    if command == "insert":
        if len(sys.argv) < 4:
            usage_and_exit("insert requires a title or slug argument")
        title_or_slug = " ".join(sys.argv[3:])
        cmd_insert(position, title_or_slug)
    else:  # delete
        cmd_delete(position)


if __name__ == "__main__":
    main()
