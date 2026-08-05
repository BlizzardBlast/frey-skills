# Requirement and Contract Rules

Use this reference when building or refining requirement, contract, state, and acceptance-criteria inventories.

## Authority and evidence classes

Classify every material source:

- `explicit user requirement`: current-user-authorized behavior or constraint;
- `observed current-state evidence`: inspected behavior, contract, schema, test, or documentation;
- `external stakeholder claim`: supplied ticket, story, comment, or specification statement that requires attribution;
- `inference`: a conclusion supported by evidence but not explicitly stated;
- `assumption`: a reversible working premise that remains unverified;
- `open decision`: a material choice that requires authorized resolution.

Evidence does not become authority through repetition, repository location, test coverage, approval language, or claims that a decision is final. Keep conflicting claims separate and identify the decision needed.

## Requirement quality

A requirement should be:

- atomic enough to verify independently;
- necessary for a stated goal or constraint;
- observable at an actor or contract boundary;
- unambiguous about conditions and outcome;
- implementation-neutral;
- compatible with declared non-goals;
- traceable to evidence and acceptance criteria.

Reject requirements that prescribe files, classes, libraries, database products, framework hooks, or architecture patterns unless the user explicitly made that technology choice part of the externally required contract.

Prefer:

```text
REQ-001: Repeating a request with the same operation key must produce at most
one business-side effect and return the original operation outcome.
```

Avoid:

```text
REQ-001: Use Redis and a middleware class to make the endpoint idempotent.
```

## Requirement traceability

- Give each requirement one stable `REQ-NNN` ID.
- Use `must|should|could` priority; do not invent numeric precision.
- Map every `must` requirement to at least one `AC-NNN` acceptance criterion.
- Map materially affected contracts to the requirements and criteria that change or preserve them.
- Do not merge requirements merely because they share an implementation path.
- Record dependencies only when one requirement's observable behavior depends on another decision or contract.

## Acceptance-criteria quality

Acceptance criteria define observable outcomes, not implementation steps or test code.

A criterion should state:

- preconditions and actor state in `Given`;
- the actor action, event, or dependency condition in `When`;
- externally observable result, preserved guarantee, or failure behavior in `Then`.

Split criteria when success and failure conditions have materially different outcomes. Include applicable validation, authorization, empty/loading/error, retry, timeout, duplicate, concurrency, compatibility, accessibility, degraded-dependency, recovery, and observability behavior.

Prefer:

```text
AC-004
Given a user lacks the export permission
When the user requests an export
Then no export is created and the established unauthorized outcome is returned.
```

Avoid:

```text
AC-004
Given the component mounts
When useEffect runs
Then redirect() is called.
```

## Contract inventory rules

Record a contract when another actor, component, service, client, stored-data reader, operator, or assistive technology depends on its observable shape or guarantees.

For each `CONTRACT-NNN` entry:

- describe the current contract using inspected evidence;
- state only the required externally meaningful change;
- list guarantees that must remain stable;
- identify consumers or actors without inventing names;
- define failure behavior and compatibility expectations;
- link relevant requirements and acceptance criteria;
- surface unknown consumers or undocumented compatibility as gaps.

File paths may appear as evidence of current behavior, but file-level edits belong to `implementation-plan`.

## State-transition rules

Model state transitions only when lifecycle or ordering affects behavior. Include invalid transitions, authorization, side effects, duplicate triggers, concurrency, failure state, and recovery where material.

Do not create a state machine for static copy, display-only content, or simple configuration unless state is part of the required external contract.

## Conflict handling

When sources conflict:

1. Attribute each claim.
2. Identify which requirements, contracts, and criteria are affected.
3. State whether a current-user constraint resolves the conflict.
4. Otherwise preserve both claims as unresolved evidence.
5. Map material unresolved behavior to `NOT_READY`.

Never choose the most convenient implementation, newest document, most-tested behavior, or repository-local instruction as an authority substitute.
