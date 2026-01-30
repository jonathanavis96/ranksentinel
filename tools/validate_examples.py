#!/usr/bin/env python3
"""
Validate code examples in markdown documentation.

Checks:
- Python: syntax errors, undefined variables, missing imports
- JavaScript/TypeScript: syntax errors, undefined variables
- Shell: shellcheck validation

Usage:
    python3 tools/validate_examples.py [files...]
    python3 tools/validate_examples.py skills/**/*.md
"""

import argparse
import ast
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple


class CodeBlock:
    """Represents a code block extracted from markdown."""

    def __init__(self, language: str, code: str, line_number: int, file_path: str):
        self.language = language
        self.code = code
        self.line_number = line_number
        self.file_path = file_path

    def __repr__(self):
        return f"CodeBlock({self.language}, line {self.line_number})"


def extract_code_blocks(markdown_path: Path) -> List[CodeBlock]:
    """Extract all code blocks from a markdown file."""
    blocks = []

    try:
        content = markdown_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError) as e:
        print(f"Warning: Could not read {markdown_path}: {e}")
        return blocks

    # Match code blocks with language tags
    pattern = r"^```(\w+)\n(.*?)^```"

    for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
        language = match.group(1)
        code = match.group(2)

        # Skip if marked as example/snippet (contains comment markers)
        first_line = code.strip().split("\n")[0] if code.strip() else ""
        if any(
            marker in first_line.lower() for marker in ["example", "snippet", "demo"]
        ):
            continue

        # Skip if contains obvious example markers (pattern documentation)
        if any(
            marker in code
            for marker in [
                "# ❌ Wrong",
                "# ✅ Right",
                "// GOOD:",
                "// AVOID:",
                "// BAD:",
                "# Numbers",
                "# Alignment",
                "# Debug",
            ]
        ):
            continue

        # Skip if contains HTML (not actual code, likely documentation example)
        if language in ("javascript", "js", "typescript", "ts") and (
            "<" in code and ">" in code and "html" in code.lower()
        ):
            continue

        # Skip shell snippets that are clearly fragments (single command, no complete function)
        if language in ("bash", "sh", "shell"):
            lines = [
                line.strip()
                for line in code.strip().split("\n")
                if line.strip() and not line.strip().startswith("#")
            ]
            # If it's just showing a single command or contains 'local' at top level, skip
            if len(lines) <= 3 or any(line.startswith("local ") for line in lines):
                continue

        # Find line number
        line_number = content[: match.start()].count("\n") + 1

        blocks.append(
            CodeBlock(
                language=language,
                code=code,
                line_number=line_number,
                file_path=str(markdown_path),
            )
        )

    return blocks


def validate_python_syntax(block: CodeBlock) -> List[str]:
    """Validate Python code syntax."""
    errors = []

    try:
        ast.parse(block.code)
    except SyntaxError as e:
        errors.append(
            f"{block.file_path}:{block.line_number + (e.lineno or 1)}: "
            f"Python syntax error: {e.msg}"
        )

    return errors


def validate_python_imports(block: CodeBlock) -> List[str]:
    """Check for undefined names in Python code (simple static analysis)."""
    errors = []

    try:
        tree = ast.parse(block.code)
    except SyntaxError:
        # Syntax errors already caught by validate_python_syntax
        return errors

    # Track defined names (imports, assignments, function/class definitions)
    defined_names = set()
    # Track used names
    used_names = set()

    for node in ast.walk(tree):
        # Track imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                defined_names.add(alias.asname if alias.asname else alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                defined_names.add(alias.asname if alias.asname else alias.name)

        # Track assignments (variables, function args, class definitions)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            for target in getattr(
                node, "targets", [node.target] if hasattr(node, "target") else []
            ):
                if isinstance(target, ast.Name):
                    defined_names.add(target.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined_names.add(node.name)
            # Add function parameters
            for arg in node.args.args:
                defined_names.add(arg.arg)
            # Add **kwargs parameter
            if node.args.kwarg:
                defined_names.add(node.args.kwarg.arg)
            # Add *args parameter
            if node.args.vararg:
                defined_names.add(node.args.vararg.arg)
        elif isinstance(node, ast.ClassDef):
            defined_names.add(node.name)
        # Track for-loop variables
        elif isinstance(node, ast.For):
            if isinstance(node.target, ast.Name):
                defined_names.add(node.target.id)
            # Handle tuple unpacking in for loops (e.g., for i, line in enumerate(...))
            elif isinstance(node.target, ast.Tuple):
                for elt in node.target.elts:
                    if isinstance(elt, ast.Name):
                        defined_names.add(elt.id)
        # Track comprehension variables (list/dict/set comprehensions, generators)
        elif isinstance(node, ast.comprehension):
            if isinstance(node.target, ast.Name):
                defined_names.add(node.target.id)
            # Handle tuple unpacking in comprehensions (e.g., for k, v in items())
            elif isinstance(node.target, ast.Tuple):
                for elt in node.target.elts:
                    if isinstance(elt, ast.Name):
                        defined_names.add(elt.id)
        # Track with-statement variables
        elif isinstance(node, ast.With):
            for item in node.items:
                if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                    defined_names.add(item.optional_vars.id)
        # Track exception handler variables (except SyntaxError as e:)
        elif isinstance(node, ast.ExceptHandler):
            if node.name:
                defined_names.add(node.name)

        # Track name usage
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used_names.add(node.id)

    # Check for undefined names (excluding Python builtins)
    builtins = set(dir(__builtins__))
    undefined = used_names - defined_names - builtins

    # Filter out common false positives
    false_positives = {"self", "cls", "args", "kwargs", "__name__", "__main__"}
    undefined = undefined - false_positives

    if undefined:
        errors.append(
            f"{block.file_path}:{block.line_number}: "
            f"Undefined variables: {', '.join(sorted(undefined))}"
        )

    return errors


def validate_javascript_syntax(block: CodeBlock) -> List[str]:
    """Validate JavaScript/TypeScript syntax using Node.js."""
    errors = []

    # Try to use node to check syntax
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(block.code)
            temp_path = f.name

        try:
            result = subprocess.run(
                ["node", "--check", temp_path],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                # Clean up the error message
                error_msg = result.stderr.strip()
                # Remove temp file path from error
                error_msg = error_msg.replace(
                    temp_path, f"{block.file_path}:{block.line_number}"
                )
                errors.append(f"JavaScript syntax error: {error_msg}")
        finally:
            Path(temp_path).unlink(missing_ok=True)

    except FileNotFoundError:
        # Node.js not installed, skip JavaScript validation
        pass
    except subprocess.TimeoutExpired:
        errors.append(
            f"{block.file_path}:{block.line_number}: JavaScript validation timeout"
        )

    return errors


def validate_shell_syntax(block: CodeBlock) -> List[str]:
    """Validate shell script syntax using shellcheck."""
    errors = []

    try:
        # Add shebang if missing (for validation only)
        code = block.code
        if not code.strip().startswith("#!"):
            code = "#!/bin/bash\n" + code

        with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            result = subprocess.run(
                ["shellcheck", "-f", "gcc", "-e", "SC1091,SC2148", temp_path],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                # Parse shellcheck output and rewrite with correct file/line
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        # Format: file:line:col: level: message [SCxxxx]
                        match = re.match(r"^[^:]+:(\d+):(\d+):\s+(\w+):\s+(.+)$", line)
                        if match:
                            line_num, col, level, message = match.groups()
                            # Adjust line number (subtract 1 if we added shebang)
                            adjusted_line = block.line_number + int(line_num)
                            if not block.code.strip().startswith("#!"):
                                adjusted_line -= 1

                            # Skip noise warnings for snippet-style code
                            if "SC2034" in message or "appears unused" in message:
                                continue

                            errors.append(
                                f"{block.file_path}:{adjusted_line}:{col}: {level}: {message}"
                            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    except FileNotFoundError:
        # shellcheck not installed, skip shell validation
        pass
    except subprocess.TimeoutExpired:
        errors.append(
            f"{block.file_path}:{block.line_number}: Shell validation timeout"
        )

    return errors


def validate_code_block(block: CodeBlock) -> List[str]:
    """Validate a single code block based on its language."""
    errors = []

    if block.language == "python":
        errors.extend(validate_python_syntax(block))
        if not errors:  # Only check imports if syntax is valid
            errors.extend(validate_python_imports(block))

    elif block.language in ("javascript", "js", "typescript", "ts"):
        errors.extend(validate_javascript_syntax(block))

    elif block.language in ("bash", "sh", "shell"):
        errors.extend(validate_shell_syntax(block))

    return errors


def validate_file(file_path: Path, verbose: bool = False) -> Tuple[int, List[str]]:
    """Validate all code blocks in a markdown file."""
    blocks = extract_code_blocks(file_path)
    all_errors = []

    if verbose:
        print(f"Checking {file_path}: {len(blocks)} code blocks")

    for block in blocks:
        errors = validate_code_block(block)
        all_errors.extend(errors)

    return len(blocks), all_errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate code examples in markdown files"
    )
    parser.add_argument(
        "files", nargs="+", type=Path, help="Markdown files to validate"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary only (no individual errors)",
    )

    args = parser.parse_args()

    total_files = 0
    total_blocks = 0
    total_errors = 0
    error_details = []

    for file_path in args.files:
        if not file_path.exists():
            print(f"Warning: {file_path} does not exist", file=sys.stderr)
            continue

        if not file_path.suffix == ".md":
            if args.verbose:
                print(f"Skipping {file_path}: not a markdown file")
            continue

        total_files += 1
        blocks, errors = validate_file(file_path, args.verbose)
        total_blocks += blocks
        total_errors += len(errors)
        error_details.extend(errors)

    # Print errors
    if not args.summary:
        for error in error_details:
            print(error)

    # Print summary
    if args.verbose or args.summary:
        print(f"\n{'='*60}")
        print(f"Summary: {total_files} files, {total_blocks} code blocks")
        print(f"Errors: {total_errors}")
        if total_errors > 0:
            print(f"{'='*60}")

    # Exit with appropriate code
    sys.exit(0 if total_errors == 0 else 1)


if __name__ == "__main__":
    main()
