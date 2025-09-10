#!/usr/bin/env python3
import os
import re
import sys

# Adjust these if your layout is different
SRC = os.path.join("prometheus", "files", "base.alerts")
DST_DIR = os.path.join("prometheus", "files", "alerts")

def sanitize(name: str) -> str:
    """
    Turn a group name like '1. Solarwinds' into '1_Solarwinds'
    by replacing dots/spaces with underscores and stripping bad chars.
    """
    s = name.strip()
    s = s.replace(".", "_")
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^\w\-]+", "", s)
    return s

def main():
    if not os.path.exists(SRC):
        print(f"ERROR: source file not found: {SRC}", file=sys.stderr)
        return 1

    with open(SRC, "r", encoding="utf-8") as f:
        lines = f.readlines()

    groups = []
    current = None

    for line in lines:
        # skip the top-level "groups:" line
        if line.strip().startswith("groups:") and current is None:
            continue

        # start of a new group?
        if line.startswith("- name:"):
            if current:
                groups.append(current)
            current = [line]
        # if we're inside a group block, collect indented lines
        elif current and (line.startswith(" ") or line.strip() == ""):
            current.append(line)
        # otherwise ignore

    # don't forget the last one
    if current:
        groups.append(current)

    if not groups:
        print("ERROR: no groups found in the source file", file=sys.stderr)
        return 1

    os.makedirs(DST_DIR, exist_ok=True)

    for grp in groups:
        # first line is like "- name: 1. Solarwinds"
        m = re.match(r"-\s*name:\s*(.+)", grp[0])
        if not m:
            continue
        name = m.group(1)
        slug = sanitize(name)
        out_path = os.path.join(DST_DIR, f"{slug}.alerts")

        with open(out_path, "w", encoding="utf-8") as wf:
            wf.write("groups:\n")
            wf.writelines(grp)

        print(f"WROTE → {out_path}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
