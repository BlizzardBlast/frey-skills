# Dependency-upgrade regression fixture

User intent: investigate why generated client output changed after a dependency upgrade.

Evidence:

- The generator was upgraded from v4 to v5.
- v5 changed its default field ordering from schema order to alphabetical order.
- The repository previously relied on the default and has no explicit `fieldOrder` setting.
- Generated snapshots now differ only in property order.
- The generator supports `fieldOrder: schema` in the existing config file.
- Downgrading restores the old output but does not explain the behavioral divergence.
