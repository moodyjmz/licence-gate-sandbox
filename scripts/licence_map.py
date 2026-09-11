#!/usr/bin/env python3
"""Decide what header a new file should carry.

The split this module exists to enforce:

  * WHICH LICENCE is a function of the path. Mechanical, decidable, testable here.
  * WHO HOLDS COPYRIGHT is a function of who wrote it. Not decidable by any machine,
    so it is asserted by a human and only recorded here.

Conflating those two is how both of the real failures happened: a rule reading
"new files get our header" would stamp a vendored third-party asset with our
copyright, and a rule reading "our files get our licence" would drop a copyleft
file into a permissively-licensed example tree that exists to be copied.

Refusal is a first-class outcome. When the licence cannot be determined the answer
is "a human decides", never a guess - a wrong header looks settled and nobody
re-examines it.
"""

import re

DEFAULT_LICENCE = "Example-1.0"
COPYRIGHT = "Example project contributors"
YEAR = "2026"

# Longest prefix wins. In the real repositories this is the exception list: most of
# the tree is the repo's own licence, with a small number of subtrees licensed
# differently by upstream.
LICENCE_MAP = [
    ("src/permissive/", "Permissive-2.0"),
]

# Paths whose licence is genuinely undetermined - vendored code, third-party trees.
# Never guessed at.
UNMAPPED = [
    re.compile(r"^vendor/"),
    re.compile(r"^third[_-]party/"),
]

ASSET_RE = re.compile(r"\.(svg|png|jpg|jpeg|gif|ico|woff2?|ttf|dat)$", re.I)
SOURCE_RE = re.compile(r"\.(js|ts|py|c|h|cpp|css|less|java|go|rb|sh|html|htm)$", re.I)

APPLY = "apply"
REFUSE = "refuse"


def licence_for(path):
    """The licence a file at this path falls under, or None if undetermined."""
    for pattern in UNMAPPED:
        if pattern.match(path):
            return None
    best = None
    for prefix, lic in LICENCE_MAP:
        if path.startswith(prefix):
            if best is None or len(prefix) > len(best[0]):
                best = (prefix, lic)
    return best[1] if best else DEFAULT_LICENCE


def classify(path, explicitly_named, has_header):
    """Decide what to do with one new file.

    `explicitly_named` is True when the human named this exact path in the command,
    rather than relying on the blanket form. Assets require that: source files a
    contributor adds are usually theirs, whereas icons and fonts are the things
    people copy, which is precisely where a false copyright claim comes from.

    Returns (action, licence_or_None, reason).
    """
    if has_header:
        return (REFUSE, None, "already carries a header; not overwriting an existing claim")

    lic = licence_for(path)
    if lic is None:
        return (REFUSE, None, "outside the licence map; determine this by hand")

    if ASSET_RE.search(path) and not explicitly_named:
        return (REFUSE, None,
                "asset - name it explicitly to assert it is ours, since assets are "
                "what tends to get copied")

    if not (SOURCE_RE.search(path) or ASSET_RE.search(path)):
        return (REFUSE, None, "not a source or asset file; decide by hand whether it needs a header")

    return (APPLY, lic, "")


def header_lines(licence, comment="//"):
    return [
        f"{comment} SPDX-FileCopyrightText: {YEAR} {COPYRIGHT}",
        f"{comment} SPDX-License-Identifier: {licence}",
    ]
