# pre-commit-buildifier

`pre-commit` hook which automatically downloads buildifier and runs it.

## Example:

```yaml
repos:
-   repo: https://github.com/warchant/pre-commit-buildifier
    rev: 0.0.2
    hooks:
    -   id: buildifier
```

run with specific buildifier version and args:
```yaml
repos:
-   repo: https://github.com/warchant/pre-commit-buildifier
    rev: 0.0.2
    hooks:
    -   id: buildifier
        args: [--version, "5.1.0", -mode=fix]
```
