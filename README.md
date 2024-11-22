# pre-commit-buildifier

`pre-commit` hook which automatically downloads buildifier and runs it.

## Example:

```yaml
repos:
-   repo: https://github.com/warchant/pre-commit-buildifier
    rev: 0.1.2
    hooks:
    -   id: buildifier
```

run with specific buildifier version and args:
```yaml
repos:
-   repo: https://github.com/warchant/pre-commit-buildifier
    rev: 0.1.2
    hooks:
    -   id: buildifier
        args: [--version, "v6.3.2", -mode=fix]
```
