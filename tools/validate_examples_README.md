# Code Example Validator

Validates code examples in markdown documentation to catch common issues before PR review.

## What It Checks

### Python

- **Syntax errors**: Invalid Python code that won't parse
- **Undefined variables**: Variables used before definition
- **Missing imports**: Modules/functions used without importing

### JavaScript/TypeScript

- **Syntax errors**: Invalid JavaScript code (uses Node.js `--check`)

### Shell (bash/sh)

- **Shellcheck violations**: Common shell script errors (uses shellcheck)
- **Auto-adds shebang**: Snippets without `#!/bin/bash` get it added for validation

## Usage

```bash
# Validate single file
python3 tools/validate_examples.py skills/domains/languages/python/python-patterns.md

# Validate multiple files
python3 tools/validate_examples.py skills/**/*.md

# Verbose mode (shows file and block counts)
python3 tools/validate_examples.py skills/**/*.md --verbose

# Summary only (no individual errors)
python3 tools/validate_examples.py skills/**/*.md --summary
```

## Smart Filtering

The tool automatically **skips** code blocks that are clearly examples/snippets:

- Blocks with `# ❌ Wrong` / `# ✅ Right` markers
- Blocks with `// GOOD:` / `// AVOID:` / `// BAD:` comments
- Blocks with `# Numbers`, `# Alignment`, `# Debug` headers (common in pattern docs)

This reduces false positives for documentation that intentionally shows incomplete or wrong examples.

## Exit Codes

- `0` - All code examples valid
- `1` - One or more code examples have errors

## Integration

This tool is integrated into `.pre-commit-config.yaml` as the `validate-code-examples` hook.

It runs automatically on:

- Skill documentation (`skills/**/*.md`)
- Domain documentation
- Playbook files

It **excludes**:

- Templates (`templates/*`)
- Root docs (`README.md`, `CONTRIBUTING.md`)
- Generated files (`workers/ralph/THUNK.md`, `workers/IMPLEMENTATION_PLAN.md`)

## Dependencies

- **Python 3**: Required (uses `ast` module for Python parsing)
- **Node.js**: Optional (for JavaScript validation with `node --check`)
- **shellcheck**: Optional (for shell script validation)

If optional dependencies are missing, those language validations are silently skipped.

## Known Limitations

### False Positives

**Python:**

- Variables defined in outer scope (file-level) may trigger "undefined" warnings
- Magic variables like `self`, `cls`, `args`, `kwargs` are whitelisted
- Python builtins are automatically excluded

**JavaScript:**

- Each code block is validated independently, so variables from previous blocks may show as undefined
- This is by design - each example should be self-contained

**Shell:**

- Snippets showing single commands may trigger warnings about unused variables
- SC2034 warnings (unused variables) are suppressed for snippet-style code

### True Positives You Should Fix

- **Missing imports**: `import time` before using `time.sleep()`
- **Undefined variables**: Define all variables before use
- **Syntax errors**: Fix broken code in examples

## Examples

### Good Example (Python)

```python
# ✅ Right - All imports and variables defined
import json
from pathlib import Path

def load_config(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
```

### Bad Example (Would Fail Validation)

```python
# ❌ Wrong - Missing imports!
import json

def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)
```

## See Also

- [validate_links.sh](validate_links.sh) - Validates markdown links
- [validate_protected_hashes.sh](validate_protected_hashes.sh) - Validates SHA256 hashes
- [.pre-commit-config.yaml](../.pre-commit-config.yaml) - Pre-commit hook configuration
