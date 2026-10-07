@AGENTS.md

# Claude Code notes

The shared project guidance lives in `AGENTS.md` (imported above). Keep it as the
single source of truth, and add only Claude Code–specific instructions here.

## Workflow

- Run `pytest test` after any change to `src/pywib/` and report the result.
- When you change a docstring or public signature, rebuild the docs with
  `cd docs && make html` and check for Sphinx warnings.
- Run any code example you add to the docs or README before presenting it as working.
- Do not change a metric's formula, output columns, or a public function signature
  without asking first. These behaviours are research-validated and published.
- If you are unsure whether a PyWIB function or parameter exists, read the source
  in `src/pywib/` instead of guessing.

## When helping a user write code with PyWIB

Follow section 1 of `AGENTS.md`. In particular: import from `pywib` in lowercase,
pass arguments by keyword, and keep claims about metrics descriptive rather than
psychological.