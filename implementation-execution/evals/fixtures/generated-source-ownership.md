# Generated source ownership fixture

Approved plan: add one command to the generated CLI reference and verify generation.

Repository:

- `schema/commands.yaml` is canonical.
- `docs/commands.md` begins with `Generated from schema/commands.yaml`.
- `scripts/generate_docs.py` regenerates the documentation.

Execution must change the YAML source and use the generator, not hand-edit the generated Markdown.
