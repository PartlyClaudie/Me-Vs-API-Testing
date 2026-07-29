# Test Plan: Poll App

## 1. Overview
Poll App is a Flask + SQLite application for creating polls and
casting votes, with a strict one-vote-per-voter rule enforced at the
database level. This document describes the testing strategy used
to verify correctness, with particular focus on data integrity under
concurrent access — a risk category not present in earlier portfolio
projects.

## 2. Objectives
- Verify poll creation validation (required fields, minimum options)
- Verify voting correctly links a vote to the right poll and option
- Verify duplicate votes from the same voter are rejected
- Verify vote counts remain accurate under concurrent/simultaneous
  voting from multiple distinct voters
- Verify cross-poll data isolation (an option from one poll cannot
  be used to vote on a different poll)

## 3. Scope

### In scope
- Poll creation, including validation of required fields and
  minimum option count
- Vote casting, including duplicate-vote rejection and cross-poll
  option validation
- Concurrent voting behavior (race-condition safety)
- API-level error handling (400, 404, 409 responses)

### Out of scope
- User interface / frontend (this project intentionally stayed
  backend-focused — see note below)
- Poll editing or deletion after creation (deliberately excluded
  from v1 to reduce scope and avoid a class of data-integrity edge
  cases around votes referencing deleted options)
- Authentication / real user accounts (voter identity is a
  cookie-based UUID, not a verified identity)
- Performance/load testing beyond the specific concurrency test
  described below (i.e. behavior under sustained high traffic, not
  just a single burst of simultaneous requests)

### Note on scope decision
This project was deliberately kept API-only rather than repeating
the full unit/API/E2E pattern already demonstrated in an earlier
portfolio project (Sprint Board). The goal here was to go deeper on
database-specific testing concerns — particularly concurrency and
data integrity — rather than wider across the same three layers
again.

## 4. Test approach by layer

| Layer | Tool | What it tests |
|---|---|---|
| Unit | pytest | Pure validation logic (`validate_poll_creation()`) — isolated from Flask and the database entirely |
| API | pytest + Flask test client, in-memory SQLite | Real endpoint behavior: status codes, database constraint enforcement, cross-poll validation, and concurrent-request safety |

Note: unlike Sprint Board, duplicate-vote prevention is enforced by
a database-level unique constraint, not application code — this
logic cannot be meaningfully unit tested in isolation, since its
correctness depends on real database behavior. It is instead covered
at the API layer.

## 5. Risk areas

1. **Lost votes under concurrent access (highest risk)** — if two
   voters vote at nearly the same instant, a naively-implemented
   vote counter could lose one of the updates (a "lost update").
   **Mitigation**: votes are stored as individual database rows, and
   counts are computed via `COUNT()` rather than an incrementable
   field, which structurally avoids the read-modify-write gap that
   causes lost updates. **Verified by**: a dedicated test firing 20
   simultaneous votes from 20 distinct simulated voters, run
   repeatedly across multiple executions to catch non-deterministic
   failures a single passing run could hide.

2. **Duplicate voting** — if the one-vote-per-voter rule fails,
   results become meaningless. **Mitigation**: enforced via a
   database-level `UNIQUE(poll_id, voter_id)` constraint rather than
   a check-then-insert pattern in application code, which would
   itself be vulnerable to the same class of race condition as risk
   #1. **Verified by**: a direct test asserting a second vote attempt
   from the same voter returns `409`.

3. **Cross-poll data leakage** — a request could reference an option
   ID that exists but belongs to a different poll than the one being
   voted on. **Mitigation**: the vote route explicitly checks that
   the option belongs to the specified poll, not just that the
   option ID exists. **Verified by**: a test voting on poll B using
   an option ID that belongs to poll A, confirming rejection.

4. **Voter identity is not tamper-proof** — voter identity relies on
   a browser cookie, which can be cleared or spoofed to bypass the
   one-vote rule. This is a known, accepted limitation for a
   portfolio-scale project, not something mitigated in this version.

## 6. Test environments
- Local development only: Windows 11, Python 3.12, SQLite (in-memory
  for tests, file-based for manual/development use)
- No staging or production environment currently exists

## 7. Entry criteria
- Application code runs without errors
- Dependencies installed via `requirements.txt`
- Test database uses in-memory SQLite, isolated from the
  development database file

## 8. Exit criteria
- All unit and API tests passing
- Concurrency test passes consistently across multiple repeated runs
  (not just a single execution)
- No known open defects in in-scope functionality

## 9. Known limitations / accepted risks
- Voter identity can be bypassed by clearing cookies (see risk #4)
- No protection against sustained high-volume traffic (only a single
  concurrent burst has been tested, not prolonged load)
- No UI exists; all verification has been done via Postman
  (exploratory) and automated API tests

## 10. Defects found during testing
- None currently open. One edge case (voting using an option ID
  belonging to a different poll) was initially discovered through
  manual Postman exploration and was already correctly handled by
  existing validation — confirmed via a dedicated regression test
  rather than representing an actual defect.