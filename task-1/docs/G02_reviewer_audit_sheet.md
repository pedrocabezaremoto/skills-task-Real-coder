# Reviewer Audit Sheet

> Fuente: `guia2/gi10.md` | Proyecto: Real Coder (Outlier)

---

Reviewer Audit Sheet

PROMPT
● [ ] No impossible, conflicting, or impractical requests (1 = fail) ● [ ] No major factual errors (1 = fail). Less than 2 minor errors (2+ = fail) ● [ ] Not contrived. Constraints not stacked 3+ or overused ("keep it brief", "explain to a
child")
 ● [ ] Rewritten prompt doesn't fundamentally alter the original task's context ● [ ] Internet-dependent designs OK; external API requirements = fail
Expected Interface:
● [ ] Section exists. Every entry has: Path, Name, Type, Input, Output, Description +
language-specific

fields

where

applicable
 ● [ ] Every file/function/class the tests actually call is documented - cross-check test
imports

against

interface

list
 ● [ ] No helper functions or third-party library fields listed as interfaces ● [ ] Descriptions aren't misleading , a correct implementation following them wouldn't fail
any

test


GOLDEN PATCH
● [ ] Every explicit prompt instruction is followed (1 miss = fail) ● [ ] Compiles. No material runtime errors. Minor edge-case errors that don't impact core
functionality

=

non-fail
 ● [ ] Output correct and complete ● [ ] Readability issues ≤2 areas. No misleading variable names (e.g., even_array =
[1,3,5] = fail) ● [ ] Not grossly inefficient. Has basic modularity/abstraction ● [ ] No Unsplash, no copyrighted assets, no external API keys, no harmful content

TESTS

● [ ] Empty codebase → ALL FAILED (not ERROR). If ERROR: broken imports or missing
Dockerfile

deps
 ● [ ] Golden Patch → ALL PASSED ● [ ] Tests check prompt requirements, not Golden Patch implementation details ● [ ] Overly specific tests ≤5% - not checking things the prompt never asked for (exact
error

messages,

internal

method

names,

specific

file

names

prompt

didn't

mandate)


VERIFIER COVERAGE
● [ ] ≤5% of major backend prompt requirements uncovered by both tests AND rubrics
Don't flag: subjective UI ("elegant", "pretty") · trivial UI details · bottleneck/collective test
coverage

·

truly

optional

instructions

("you

can

also

include...")

·

requirements

already

covered

by

unit

tests

Do flag: mandatory features with optional usage ("customer can optionally add a note" →
feature

must

exist)


RUBRICS
Scan each rubric once. Tag worst issue per rubric. Don't double-count.
Common errors to catch every time:
● [ ] Not self-contained - needs the prompt to evaluate. Bad: "handles the edge case from
the

prompt."

Good:

"handles

negative

quantity

input

by

returning

a

400

error."
 ● [ ] Overfit to Golden Patch - would reject valid alternatives. Watch for: exact file names,
variable

names,

header

names

the

prompt

didn't

require
 ● [ ] Subjective without definition - "appropriate", "properly", "best practices" with no
measurable

criteria
 ● [ ] Bundles totally unrelated constraints (related features/tech stack grouped = OK) ● [ ] Negatively framed - good response would evaluate to "No" (must evaluate to
"Yes"/"True")
 ● [ ] Incorrect/factually wrong or checks something the prompt doesn't ask for ● [ ] Redundant pair - two rubrics checking the same thing ● [ ] Weight off by 2 levels (1↔5) ● [ ] Weight off by 1 level (1↔3 or 3↔5) - minor ● [ ] Miscategorized dimension - minor.

VALIDATION & FILES
● [ ] codebase.zip → files at root, NO parent folder wrapper ● [ ] tests.zip → tests/ folder at top level ● [ ] run.sh / parsing.py "DO NOT MODIFY" sections untouched (Cursor agent didn't edit
them)
 ● [ ] before.json = all FAILED, after.json = all PASSED ● [ ] File timestamps = current session ● [ ] No COPY command in Dockerfile or run.sh