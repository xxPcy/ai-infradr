# Security Policy

AI InfraDr inspects local environment metadata and does not modify packages, drivers, or system configuration.

## Reporting a security issue

Please avoid publishing exploit details in a public issue. Use GitHub's private vulnerability reporting feature when it is enabled for this repository.

## Safety principles

- No automatic `sudo` operations.
- No silent package installation/uninstallation.
- No environment mutation during diagnosis.
- Future fix functionality must default to dry-run and require explicit confirmation before applying changes.
