# licence-gate-sandbox

Disposable testbed for the licence-header CI gates and the reviewer
acknowledgement flow. **Synthetic fixtures only** — nothing here is real
content, and "Example Corp" and "Example License 1.0" are invented.

Exists because the gates cannot be tested where they are actually needed:
those repos are private on a plan with no branch protection, so nothing can
be made to block. This repo is public, so required checks, required reviews
and the last-pusher rule all work.

## What is under test

| Check | Asks |
|---|---|
| A | a modified file with a licence header gains a modification notice |
| B | no line matching `Copyright` or `Licensed under` is deleted or altered |
| C | candidate replacements are detected and listed for a human |
| D | a reviewer, not the author, has dispositioned every candidate |

A and B are mechanical and can block. C only ever prompts — it may say
"this might be a replacement", never "this isn't". D is the human's
signature, and is the only thing that carries liability.
