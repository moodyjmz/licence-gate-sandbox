# licence-gate-sandbox

Development scratch for the licence gate. The gate itself now lives in
[`moodyjmz/licence-gate-tooling`](https://github.com/moodyjmz/licence-gate-tooling)
and is consumed here as SHA-pinned actions, the same way every real repository will
consume it.

**To attack the gate, go to
[`moodyjmz/licence-gate-target`](https://github.com/moodyjmz/licence-gate-target)** —
that repository exists for it and its README says what to try.

This one keeps the five scenario pull requests that were used to build the gate, so
the behaviour they pinned down stays visible.

## Why the scripts left

They were in `scripts/`, and the workflows checked out the pull request and ran them
*from that checkout* — so a pull request could edit the gate it was being judged by,
report nothing, and pass itself. Pinned to a SHA in another repository, the code that
runs is fixed at the pin and the pull request cannot reach it.
