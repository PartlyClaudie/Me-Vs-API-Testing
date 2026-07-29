# Poll App

[![Poll App Tests](https://github.com/PartlyClaudie/Me-Vs-API-Testing/actions/workflows/tests.yml/badge.svg)](https://github.com/PartlyClaudie/Me-Vs-API-Testing/actions/workflows/tests.yml)

A poll/voting application built with Flask and SQLite — the third
project in my testing portfolio, built specifically to practice
database-level testing concerns (data integrity, concurrency) that
weren't present in earlier, simpler projects.

## Why this project
My previous full-stack project (Sprint Board) used in-memory storage
and already demonstrated the full unit/API/E2E testing pyramid.
Rather than repeat that structure, this project intentionally stays
backend/API-focused, going deeper on a real database and a genuinely
harder problem: **guaranteeing accurate vote counts even when
multiple people vote at the exact same time.**

## Tech stack
- Python, Flask
- SQLite via Flask-SQLAlchemy
- pytest, Flask test client (in-memory SQLite for tests)

## Core design decision: how race conditions are avoided
Vote counts are never stored as an incrementable number. Instead,
every vote is its own row in a `votes` table, and counts are
computed on demand via `COUNT()`. This structurally avoids the
classic "lost update" problem — where two simultaneous requests
both read a stale count and each write back the same (wrong,
too-low) incremented value.

Duplicate voting is prevented the same way: not by application code
checking "has this person already voted?" before inserting (which
has the identical race-condition gap), but by a database-level
`UNIQUE(poll_id, voter_id)` constraint. The database itself rejects
a second vote attempt from the same voter, atomically, regardless of
timing.

## Verifying it actually works
A dedicated test fires 20 simultaneous vote requests from 20
distinct simulated voters (using Python's `threading`) and asserts
the final count is exactly 20 — no votes lost, none double-counted.
This test was run repeatedly (not just once) during development,
since race conditions are non-deterministic and can pass by chance
on a single run.

## Test coverage
- **Unit tests** — poll creation validation, tested as pure functions
  with no Flask or database involved
- **API tests** — full CRUD + voting behavior via Flask's test
  client and an in-memory SQLite database, including:
  - Duplicate-vote rejection (409)
  - Cross-poll option validation (voting on poll B using an option
    that belongs to poll A is correctly rejected)
  - The concurrency test described above

See [test_plan.md](test_plan.md) for the full test strategy,
including risk analysis and known limitations.

## Setup
\`\`\`bash
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
\`\`\`

## Run the app
\`\`\`bash
python app.py
\`\`\`

## Run tests
\`\`\`bash
pytest tests/ -v
\`\`\`

## Lessons learned
- Learned to distinguish which logic is genuinely unit-testable
  (pure validation functions) versus logic that only makes sense to
  test against a real database (duplicate-vote enforcement via a
  unique constraint) — not everything belongs at the same layer.
- Learned the mechanics of `threading.Thread`, `start()`, and
  `join()` to deliberately construct a genuine race condition in a
  test, rather than just testing sequential behavior.
- Wrote a test plan grounded in real, already-implemented mitigations
  rather than hypothetical risks — each identified risk maps to a
  specific design decision and a specific test that verifies it.

## Related portfolio projects
- [Manual test cases & bug reports](https://github.com/PartlyClaudie/Me-Vs-the-internet)
- [API automation (restful-booker)](https://github.com/PartlyClaudie/Me-Vs-restful-booker)
- [UI automation (Playwright)](https://github.com/PartlyClaudie/Me-Vs-Playwright)
- [Sprint Board (full-stack, 3-layer testing pyramid)](https://github.com/PartlyClaudie/Me-Vs-A-Sprint-Board)