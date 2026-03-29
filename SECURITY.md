# 安全说明

如果您发现安全问题，请直接联系我们：

- support@fit2cloud.com
- 400-052-0755

感谢您的支持！

# Security Policy

All security bugs should be reported to the contact as below:

- support@fit2cloud.com
- 400-052-0755

Thanks for your support!

## Local secret scanning

This repository uses Gitleaks for repository secret scanning.

Recommended local checks:

```bash
gitleaks git --config .gitleaks.toml
pre-commit run gitleaks --all-files
```

`gitleaks git --config .gitleaks.toml` is the default repository verification command because it matches the tracked-history scope enforced in CI.

Use `gitleaks dir --config .gitleaks.toml .` only for an explicit working-tree audit. It scans gitignored local files too, so local `.env` and `.env.local-dev` secrets may appear even when the tracked repository history is clean.

Repository-specific exclusions and reviewed placeholders are maintained in `.gitleaks.toml`.

Bootstrap and locally created system-user passwords are treated as temporary credentials and must be changed before normal continued use.

## Secret triage guidance

- **Real secret**: rotate it, remove it from the code path, and review whether git history cleanup is needed.
- **Weak default**: replace the predictable value with explicit configuration or a one-time bootstrap path.
- **False positive**: record a narrow exception in `.gitleaks.toml` or `.gitleaksignore` instead of ignoring the whole file class ad hoc.
