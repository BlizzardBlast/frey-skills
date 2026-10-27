# Research decision: situated planning for coding agents (2026-10-26)

## Sources

- Maggie Appleton, [Planning with Agents: Divided Worlds, Boundary Objects,
  and Thicker Interfaces](https://maggieappleton.com/planning-agents)
- GitHub Next, [Chopin research prototype](https://githubnext.com/projects/chopin/)

These are thought-provoking design research and prototypes, not independent
evidence that any particular prompt improves coding-agent correctness.

## Repository fit and gaps

| Idea | Existing capability | Narrow addition |
| --- | --- | --- |
| Plans orient situated action | `implementation-execution` tracks conformance and stops on material drift | Explicit assumption-versus-observation replanning handoff |
| Human-readable boundary objects | `implementation-plan` already emits source-linked ordered steps; `architecture-decision` compares options | Optional concise decision synopsis and useful static diagrams |
| Reality-grounded choices | Planning inspects repositories; architecture decisions reject invented measurements | Specify smallest discriminating experiment, without executing in read-only skills |
| Shared, traceable decisions | Proposed ADRs preserve evidence, owners, and revisit conditions; Git and PRs preserve discussion | Reuse existing project artifacts, not a new knowledge database |

## Adopted boundaries

- Keep the established separation between read-only specification, architecture,
  planning, and separately authorized implementation/execution.
- Material conflicts discovered in execution stop before out-of-plan actions,
  identify the contradicted assumption and affected steps, and require an
  eligible revised plan with user authorization to resume. Merely finding a
  feasible alternative does not invalidate an approved, still-safe plan.
- Make the concise brief conditional on a meaningful human decision. Do not add
  approval prompts for every mechanical edit.
- Use tables or text diagrams only when they clarify relationships, label
  hypotheticals as hypothetical, and preserve precise underlying evidence.
- Propose experiments only for material uncertainty; mark them `NOT_RUN` until
  separately authorized and actually performed. Comparison requires compatible
  inputs, checks, and stated cost/safety/rollback bounds.

## Explicit non-adoptions

- No new visual planning product, interactive web UI, collaboration server, or
  always-on/VPS dependency.
- No automatic multi-branch agent swarms or unbounded token/GitHub Actions costs.
- No experimental run, benchmark, deployment, or branch creation from
  read-only planning or architectural analysis.
- No agent self-approval, silent rewriting of user decisions, or publication
  of speculative patterns to `agent-brain`.

## Future evaluation (not a verified outcome)

For a later authorized evaluation, compare plans for a synthetic workflow with
a material architecture decision and a workflow with only trivial changes.
Check if the agent (1) includes a concise evidence/ownership/revisit brief only
when useful, (2) labels hypothetical visuals and experiment results honestly,
(3) stops when a material plan assumption fails, and (4) continues for safe
minor deviations without adding unnecessary human checkpoints. Deterministic
contract tests protect instruction text, not actual agent behavior.
