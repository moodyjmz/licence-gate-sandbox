#!/usr/bin/env python3
"""Licence gate: three checks over a PR diff.

  A  a modified file carrying a licence header must also carry a modification notice
  B  no line matching Copyright / Licensed under may be deleted or altered
  C  candidate replacement events, detected and listed for a human to disposition

A and B are mechanical and may block. C only ever prompts: it may say "this might be
a replacement", never "this isn't". A false prompt costs a reviewer seconds; a false
all-clear is a missing record nobody knows is missing - so C is tuned to over-detect,
and the reviewer's "not a replacement" is the cheap correction.

Usage:  licence-gate.py <base-sha> <head-sha>
Writes a markdown report to stdout and exits non-zero if A or B failed.
"""

import re
import subprocess
import sys

NOTICE = "Modified by the Example project."
HEADER_RE = re.compile(r"(copyright|licensed under)", re.I)
ASSET_RE = re.compile(r"\.(svg|png|jpg|jpeg|gif|ico|dat|woff2?|ttf)$", re.I)


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True).stdout


def changed_files(base, head):
    out = sh("git", "diff", "--name-status", f"{base}..{head}")
    added, modified, deleted = [], [], []
    for line in out.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        status, path = parts[0], parts[-1]
        if status.startswith("A"):
            added.append(path)
        elif status.startswith("D"):
            deleted.append(path)
        elif status.startswith("M"):
            modified.append(path)
    return added, modified, deleted


def check_b(base, head):
    """Deleted or altered licence/copyright lines. Returns [(path, line)]."""
    out = sh("git", "diff", "--unified=0", f"{base}..{head}")
    violations, path = [], None
    for line in out.split("\n"):
        if line.startswith("+++ b/"):
            path = line[6:]
        elif line.startswith("-") and not line.startswith("---"):
            if HEADER_RE.search(line[1:]):
                violations.append((path, line[1:].strip()))
    return violations


def check_a(base, head, modified):
    """Modified files that have a licence header but no notice."""
    missing = []
    for p in modified:
        content = sh("git", "show", f"{head}:{p}")
        if not content:
            continue
        head_region = "\n".join(content.split("\n")[:40])
        if HEADER_RE.search(head_region) and NOTICE not in content:
            missing.append(p)
    return missing


def check_c(added, modified, deleted):
    """Candidate replacement events. Over-detects by design."""
    cands = []
    for p in deleted:
        cands.append((p, "file deleted"))
    for p in added:
        if ASSET_RE.search(p):
            cands.append((p, "asset added"))
    for p in modified:
        if ASSET_RE.search(p):
            cands.append((p, "asset modified"))
    return cands


def main(argv):
    candidates_only = "--candidates" in argv
    argv = [a for a in argv if not a.startswith("--")]
    if len(argv) != 2:
        print(__doc__.strip())
        return 2
    base, head = argv
    added, modified, deleted = changed_files(base, head)

    if candidates_only:
        for p, _ in check_c(added, modified, deleted):
            print(p)
        return 0

    b = check_b(base, head)
    a = check_a(base, head, modified)
    c = check_c(added, modified, deleted)

    out = []
    blocking = bool(a or b)

    if b:
        out.append(f"### Blocking — {len(b)} licence line(s) removed or altered\n")
        out.append("A licence has not changed, so no existing licence text may change. "
                   "Add lines; never edit or delete them.\n")
        for p, line in b:
            out.append(f"- `{p}`\n  ```\n  - {line}\n  ```")
        out.append("")

    if a:
        out.append(f"### Blocking — {len(a)} modified file(s) missing a notice\n")
        out.append(f"Each needs `{NOTICE}` appended to its existing header block. "
                   "This is auto-fixable.\n")
        for p in a:
            out.append(f"- `{p}`")
        out.append("")

    if c:
        out.append(f"### Needs your decision — {len(c)} candidate(s)\n")
        out.append("These *may* be replacement events. Detection over-reports on "
                   "purpose; deciding is a human judgement, so every one needs an "
                   "answer, including \"no\".\n")
        for p, why in c:
            out.append(f"- `{p}` — {why}")
        out.append("\nReply with a disposition for each path:\n")
        out.append("```\nexample-log:")
        for p, _ in c:
            out.append(f"  {p} -> ")
        out.append("```")
        out.append("")

    verified = ["no licence or copyright line deleted or altered"] if not b else []
    if not a:
        verified.append("every modified file with a header carries a notice")
    if verified:
        out.append("<details><summary>✅ Verified automatically — you need not check these</summary>\n")
        for v in verified:
            out.append(f"- {v}")
        out.append("\n</details>\n")

    out.append("<details><summary>⚠️ Not checked — these need a human</summary>\n")
    out.append("- whether each candidate above is genuinely a replacement")
    out.append("- whether a stated rationale is the real one")
    out.append("- where an added asset actually came from")
    out.append("\n</details>")

    print("\n".join(out))
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
