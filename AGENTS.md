# Project Guidelines

## Scope

This repository stores reusable **agent skills** for the Agent Skills ecosystem.

- Each top-level skill folder should represent one focused workflow.
- Keep instructions practical, deterministic where possible, and safe by default.

## Instruction File Strategy

- Use this root `AGENTS.md` as the workspace-wide instruction source.
- Do not add a parallel `.github/copilot-instructions.md` unless intentionally migrating and removing `AGENTS.md` in the same change.

## Repository Layout

Follow this structure for each skill:

- `SKILL.md` (required): metadata + usage rules
- `agents/` (optional): client-specific metadata such as `openai.yaml`
- `scripts/` (optional): helper scripts used by the skill
- `references/` (optional): supporting docs/examples
- `assets/` (optional): templates or static resources
- `evals/` (optional): behavioral fixtures and accepted scorecards

Current skill examples:

- `debug/SKILL.md`
- `implementation-plan/SKILL.md`
- `test-strategy/SKILL.md`
- `implementation-execution/SKILL.md`
- `code-review/SKILL.md`
- `iterative-self-review/SKILL.md`

## SKILL.md Requirements

Every skill must include YAML frontmatter and clear activation guidance.

Required metadata:

- `name`
- `description`

Recommended metadata:

- `license`
- `metadata.author`
- `metadata.version`

Authoring expectations:

- The `description` should include concrete trigger language (for example: "Use when…").
- Define explicit stop/completion conditions.
- For iterative workflows, define anti-loop safeguards.
- Keep steps short, ordered, and actionable.

## Writing Style

- Prefer imperative instructions ("Do X", "Avoid Y").
- Avoid vague guidance; prefer concrete checks and outputs.
- Keep `SKILL.md` concise; move long detail to `references/`.
- Preserve backwards-compatible behavior when refining existing skills unless the change is intentional and documented.

## Validation Before Commit

For any skill changes:

1. Verify frontmatter is valid YAML.
2. Verify `name` matches the skill folder name.
3. Ensure `description` is specific enough for discovery.
4. Confirm examples/prompts still match actual behavior.
5. Re-read the full `SKILL.md` for contradictions or missing stop conditions.
6. Verify markdown formatting, including one trailing newline.

Run the validation commands that match the changed artifacts:

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pip install -r requirements-spec.txt
python3 scripts/validate_repository.py
for skill_file in */SKILL.md; do skills-ref validate "$(dirname "${skill_file}")"; done
python3 -m unittest discover -s code-review/scripts -p 'test_*.py'
python3 -m unittest scripts.test_validate_repository
python3 -m unittest scripts.test_build_plugin scripts.test_implementation_execution_contract scripts.test_test_strategy_contract
python3 scripts/build_plugin.py --force
python3 scripts/validate_plugin_bundle.py dist/frey-skills
git diff --check
```

Behavioral evals are required only when the affected skill owns an
`evals/evals.json` suite whose playbook makes those trials a release gate. A new
skill may intentionally ship without evals. Such a PR must say so explicitly,
use deterministic contract/specification/package validation, and must not claim
that model behavior was certified.

For an applicable existing suite, keep raw evidence under ignored
`eval-workspace/`, commit the accepted scorecard, never reconstruct missing
trials, and run mutation-oriented cases only in disposable repositories.

`test-strategy` intentionally ships without an `evals/` directory.

## Pull Request Notes

When opening a PR, include:

- What skill(s), docs, scripts, or metadata changed.
- Why the change is needed.
- Behavior changes in activation or outputs.
- Exact deterministic validation evidence.
- Applicable behavioral scorecards, or explicit confirmation that the new skill intentionally has no eval suite.

## Conventions Specific to This Repo

- Keep folder names lowercase kebab-case.
- Keep the README skill list in sync when adding or removing skills.
- Keep skill instructions tool-agnostic unless a tool dependency is essential.
- Keep product-specific metadata in `agents/` instead of the core skill instructions.
