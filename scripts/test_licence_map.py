#!/usr/bin/env python3
"""Tests for the licence decision logic.

Deliberately stdlib-only so they run anywhere with no install step.

Each test names the real failure it guards against. A test whose purpose is not
obvious gets deleted by someone six months from now who cannot see why it matters.
"""

import unittest

from licence_map import APPLY, REFUSE, classify, licence_for


class TestLicenceForPath(unittest.TestCase):
    def test_default_applies_to_ordinary_paths(self):
        self.assertEqual(licence_for("src/widget.js"), "Example-1.0")

    def test_subtree_overrides_the_default(self):
        """The real case: upstream licenses an example tree permissively while the
        product is copyleft. A file added there must not inherit the repo default."""
        self.assertEqual(licence_for("src/permissive/page.html"), "Permissive-2.0")

    def test_longest_prefix_wins(self):
        self.assertEqual(licence_for("src/permissive/deep/nested/x.js"), "Permissive-2.0")

    def test_vendored_paths_are_undetermined_not_defaulted(self):
        """Guessing here is how third-party code acquires your licence."""
        self.assertIsNone(licence_for("vendor/lib/thing.js"))
        self.assertIsNone(licence_for("third_party/x.c"))


class TestClassify(unittest.TestCase):
    def test_source_file_gets_the_repo_default(self):
        action, lic, _ = classify("src/parser.js", explicitly_named=False, has_header=False)
        self.assertEqual((action, lic), (APPLY, "Example-1.0"))

    def test_source_file_in_permissive_subtree_gets_that_licence(self):
        """A single pull request can add files under two different licences; the
        decision is per path, never per pull request."""
        action, lic, _ = classify("src/permissive/banner.html",
                                  explicitly_named=False, has_header=False)
        self.assertEqual((action, lic), (APPLY, "Permissive-2.0"))

    def test_asset_is_refused_unless_named(self):
        """The real failure: two icons named as first-party work were unmodified
        third-party icons. Blanket-stamping assets asserts copyright over them."""
        action, _, reason = classify("assets/icon.svg",
                                     explicitly_named=False, has_header=False)
        self.assertEqual(action, REFUSE)
        self.assertIn("name it explicitly", reason)

    def test_asset_is_applied_when_named(self):
        action, lic, _ = classify("assets/icon.svg",
                                  explicitly_named=True, has_header=False)
        self.assertEqual((action, lic), (APPLY, "Example-1.0"))

    def test_unmapped_path_is_refused_even_when_named(self):
        """An explicit assertion of authorship does not make the licence knowable."""
        action, _, reason = classify("vendor/lib.js",
                                     explicitly_named=True, has_header=False)
        self.assertEqual(action, REFUSE)
        self.assertIn("by hand", reason)

    def test_existing_header_is_never_overwritten(self):
        action, _, reason = classify("src/widget.js",
                                     explicitly_named=True, has_header=True)
        self.assertEqual(action, REFUSE)
        self.assertIn("existing claim", reason)

    def test_unknown_file_type_is_refused(self):
        """README, config and data files mostly need no header; decide by hand
        rather than littering."""
        action, _, _ = classify("docs/notes.md", explicitly_named=False, has_header=False)
        self.assertEqual(action, REFUSE)


class TestMixedPullRequest(unittest.TestCase):
    def test_a_single_pull_request_resolves_each_file_independently(self):
        """The whole point: one pull request, several answers, no human needing to
        know which subtree is which."""
        files = [
            ("src/parser.js", False, False),
            ("src/permissive/banner.html", False, False),
            ("assets/spinner.svg", False, False),
            ("vendor/lib.js", False, False),
        ]
        got = [(p, classify(p, n, h)[0], classify(p, n, h)[1]) for p, n, h in files]
        self.assertEqual(got, [
            ("src/parser.js", APPLY, "Example-1.0"),
            ("src/permissive/banner.html", APPLY, "Permissive-2.0"),
            ("assets/spinner.svg", REFUSE, None),
            ("vendor/lib.js", REFUSE, None),
        ])


if __name__ == "__main__":
    unittest.main(verbosity=2)
