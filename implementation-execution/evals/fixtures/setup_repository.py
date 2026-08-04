#!/usr/bin/env python3
"""Create deterministic disposable repositories for implementation-execution evals."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

FIXTURES = {
    "complete-plan-execution": {
        "src/profile.ts": "export interface Profile {\n  firstName: string;\n  lastName: string;\n}\n",
        "src/profile.test.ts": "describe('Profile', () => {\n  it('supports required names', () => {});\n});\n",
        "test_runner.py": "from pathlib import Path\nprofile = Path('src/profile.ts').read_text()\ntests = Path('src/profile.test.ts').read_text()\nassert 'firstName: string' in profile\nassert 'lastName: string' in profile\nassert 'middleName?: string' in profile\nassert 'with middleName' in tests\nassert 'without middleName' in tests\n",
    },
    "partial-implementation-continuation": {
        "src/name.ts": "export function formatName(first: string, last: string) {\n  return `${first} ${last}`;\n}\n",
        "test_runner.py": "from pathlib import Path\nimplementation = Path('src/name.ts').read_text()\ntests = Path('src/name.test.ts').read_text()\nassert 'formatName' in implementation\nassert 'first' in tests and 'last' in tests\n",
    },
    "material-plan-drift": {
        "src/mapper.ts": "export function mapAccount(value: string) {\n  return { accountNumber: value };\n}\n",
        "contract_test.py": "from pathlib import Path\ntext = Path('src/mapper.ts').read_text()\nassert 'accountNumber' in text\nassert 'acctNo' not in text\n",
    },
    "unrelated-dirty-work": {
        "src/total.ts": "export function total(values: number[]) { return values.reduce((a, b) => a + b, 0); }\n",
        "src/total.test.ts": "// add focused tests here\n",
        "notes/private.md": "committed baseline note\n",
    },
    "generated-source-ownership": {
        "schema/commands.yaml": "commands:\n  - status\n",
        "docs/commands.md": "Generated from schema/commands.yaml\n\n- status\n",
        "generate_docs.py": "from pathlib import Path\nlines = Path('schema/commands.yaml').read_text().splitlines()\ncommands = [line.strip()[2:] for line in lines if line.strip().startswith('- ')]\nPath('docs/commands.md').write_text('Generated from schema/commands.yaml\\n\\n' + ''.join(f'- {item}\\n' for item in commands))\n",
    },
    "verification-failure": {
        "src/rules.ts": "export function allowed(value: number) { return value >= 0; }\n",
        "test_runner.py": "from pathlib import Path\ntext = Path('src/rules.ts').read_text()\nassert 'value >= 0' in text, 'new behavior violates the required rule'\n",
    },
    "dirty-plan-owned-work": {
        "src/profile.ts": "export interface Profile {\n  firstName: string;\n  lastName: string;\n}\n",
        "src/profile.test.ts": "// existing tests\n",
    },
}


def run(*args: str, cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True, stdout=subprocess.DEVNULL)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=sorted(FIXTURES))
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    destination = args.destination.resolve()
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    for relative, content in FIXTURES[args.case].items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    run("git", "init", "-q", cwd=destination)
    run("git", "config", "user.email", "eval@example.invalid", cwd=destination)
    run("git", "config", "user.name", "Eval Fixture", cwd=destination)
    run("git", "add", ".", cwd=destination)
    run("git", "commit", "-qm", "fixture baseline", cwd=destination)

    if args.case == "unrelated-dirty-work":
        (destination / "notes/private.md").write_text("unrelated user edit\n", encoding="utf-8")
        (destination / "scratch.txt").write_text("untracked user work\n", encoding="utf-8")
    elif args.case == "dirty-plan-owned-work":
        profile = destination / "src/profile.ts"
        profile.write_text(profile.read_text(encoding="utf-8") + "\n// unrelated user hunk\n", encoding="utf-8")

    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
