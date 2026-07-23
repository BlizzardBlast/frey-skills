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

Current skill examples:

- `code-review/SKILL.md`
- `implementation-plan/SKILL.md`
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
6. Verify markdown formatting (including a single trailing newline at end of file).

Run the validation commands that match the changed artifacts:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_repository.py
python3 -m unittest discover -s code-review/scripts -p 'test_*.py'
python3 -m unittest scripts.test_validate_repository
python3 -m unittest scripts.test_build_plugin
python3 scripts/build_plugin.py --force
python3 scripts/validate_plugin_bundle.py dist/frey-skills
git diff --check
```

When a `SKILL.md` description, activation boundary, output format, workflow, or
decision rule changes, also run the applicable manual behavioral evals from the
skill's `evals/evals.json` and record the evidence under ignored
`eval-workspace/`.

These checks are local repository checks. Do not claim hosted model evals or CI
unless you have separate evidence for those systems.

## Pull Request Notes

When opening a PR, include:

- What skill(s) changed
- Why the change is needed
- Any behavior changes in activation or outputs
- Before/after examples when workflow behavior changes

## Conventions Specific to This Repo

- Keep folder names lowercase kebab-case (for example: `iterative-self-review`).
- Keep the README skill list in sync when adding/removing skills.
- Keep skill instructions tool-agnostic unless a tool dependency is essential.
- Keep product-specific metadata in `agents/` instead of mixing it into the
  core skill instructions.
