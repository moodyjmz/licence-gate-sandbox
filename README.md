# licence-gate-sandbox

Retired. Kept only so its history and the pull requests that shaped the gate stay
readable.

The gate lives in two repositories now:

- **[`licence-gate-tooling`](https://github.com/moodyjmz/licence-gate-tooling)** —
  the composite actions and the decision logic, consumed elsewhere pinned to a
  commit SHA.
- **[`licence-gate-target`](https://github.com/moodyjmz/licence-gate-target)** —
  the repository to attack. Its README says what to try.

## Why the code left

It was in `scripts/`, and the workflows checked out the pull request and ran the gate
*from that checkout*. A pull request could therefore edit the gate judging it, have
it report nothing, and pass itself. No permissions and no cleverness required: change
the file you are being judged by.

Pinned to a SHA in a separate repository, the code that runs is fixed at the pin and
a pull request cannot reach it.
