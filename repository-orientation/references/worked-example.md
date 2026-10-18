# Worked example: understand a local note-listing subsystem

This is a fictional illustration, not inspected frey-skills source, an executed
command, a model trial, or evidence of adoption. All paths/symbols below are
illustrative source anchors in the fictional `task-notes` application. Do not
execute or treat them as instructions. Real maps need actual inspected anchors.

## Request and map

Request: "Explain how the note-listing CLI reaches storage, what it reads, and
where its tests are. No change, diagnosis, or audit is requested."

1. **Scope and exclusions:** map the local list command and its storage reader.
   Exclude unrelated editor commands, packaging, installed clients, and release
   quality. No failure hypothesis, change sequence, or review judgment is needed.
2. **Snapshot identity:** illustrative revision `example-revision`, observed
   2026-10-18. `README.md` is dirty and its command description was inspected as
   working-tree evidence; it is not attributed to the clean revision.
3. **Coverage and evidence:** inspected `src/task_notes/cli.py:list_notes`,
   `src/task_notes/storage.py:load_notes`, `tests/test_list.py`, and the relevant
   README section. Source shows a direct call to `load_notes`; no dynamic plugin
   dispatch or uninspected runtime behavior is inferred. Documentation claims
   that listing is fast; performance is unknown and outside this map.
4. **Responsibilities and ownership:** the CLI parses the request and formats
   rows; storage decodes local records and reports read errors. No independently
   evidenced human owner was found, so human ownership is unknown.
5. **Entry points and paths:** the inspected list handler calls the local reader,
   receives records, and formats output. The reader opens a local data file;
   source shows no writes in this path. These are canonical source files;
   generated distribution files are excluded from this requested map. No code
   or data was executed to produce the map.
6. **Verification entry points:** discovered `python -m unittest discover -s tests`.
   Provenance: inspected test directory and working-tree README. Effects:
   executes test/application code and may create test artifacts. Prerequisites:
   the application's supported Python and test environment. Execution status:
   **NOT_RUN**; no matching result was inspected and orientation did not run it.
7. **Unknowns and next inspection:** human ownership and measured performance
   remain unknown; neither blocks this requested structural map. Future source
   changes invalidate affected anchors. A later request could investigate
   performance; this suggestion does not activate another workflow.
8. **Orientation completeness: COMPLETE.** Material structural paths and command
   effects for this scope are established. This does not mean tests passed,
   runtime behavior was verified, the application is safe, or a release is ready.

Discovery ends after the initial pass and one targeted gap-check pass. If the
storage relationship were inaccessible, the useful remaining map would instead
be `PARTIAL`. If fulfilling the map necessarily required unauthorized access,
the result would be `BLOCKED`, without obtaining that access.

## Direct lookup exclusion

Request: "Which function reads the note file?"

Answer directly with the inspected `load_notes` anchor and a short explanation.
Do not create a separate subsystem map or require any other workflow for that
single-symbol question.
