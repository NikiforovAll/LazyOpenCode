---
name: architecture-audit
description: Audits the project against established architectural patterns
---
# Architecture Audit Skill

Use this skill to ensure new code follows the project's layered architecture.

## Steps
1. Identify the layer of the current file.
2. Check for prohibited cross-layer imports.
3. For specific patterns, load the documentation from **references/patterns.md**.

## When to use
Invoke this during code reviews or when scaffolding new modules.
