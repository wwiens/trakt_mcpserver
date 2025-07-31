"""Tests to enforce architectural decisions and prevent regression."""

import ast
from pathlib import Path


def test_no_try_except_in_client_layer():
    """Ensure client layer uses only @handle_api_errors decorator, no try/except blocks.

    Exception: auth/client.py is allowed to have try/except for file operations only.
    """
    client_dir = Path("client")
    violations: list[str] = []

    for py_file in client_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        with open(py_file) as f:
            content = f.read()

        try:
            tree = ast.parse(content)

            # Special handling for auth/client.py
            if "auth/client.py" in str(py_file):
                # Find all try blocks and check if they're in allowed functions
                allowed_funcs = [
                    "_load_auth_token",
                    "clear_auth_token",
                    "get_device_token",
                ]
                for node in ast.walk(tree):
                    if isinstance(node, ast.Try):
                        # Find the parent function of this try block
                        parent_func = None
                        for parent in ast.walk(tree):
                            if isinstance(
                                parent, ast.FunctionDef | ast.AsyncFunctionDef
                            ) and any(child is node for child in ast.walk(parent)):
                                parent_func = parent
                                break

                        # If not in an allowed function, it's a violation
                        if not parent_func or parent_func.name not in allowed_funcs:
                            violations.extend([f"{py_file}:{node.lineno}"])
            else:
                # For other files, no try/except blocks are allowed
                for node in ast.walk(tree):
                    if isinstance(node, ast.Try):
                        violations.extend([f"{py_file}:{node.lineno}"])
        except SyntaxError:
            pass

    assert not violations, f"Try/except blocks found in client layer: {violations}"


def test_centralized_logging():
    """Ensure logging is only done in utils/api/errors.py."""
    allowed_logging_files = {
        "utils/api/errors.py",
        "server.py",  # Main server file is allowed to have logging
        "server/main.py",  # Main server module
    }

    violations: list[str] = []

    # Check all Python files in key directories
    for directory in ["client", "server", "models", "config"]:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue

        for py_file in dir_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            relative_path = str(py_file)
            if relative_path in allowed_logging_files:
                continue

            with open(py_file) as f:
                content = f.read()

            # Check for logging imports or usage
            if any(
                pattern in content
                for pattern in [
                    "import logging",
                    "from logging import",
                    "logger.",
                    "logging.",
                ]
            ):
                # Parse to check if it's actually used (not just imported)
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        # Check for logger attribute access
                        if isinstance(node, ast.Attribute) and isinstance(
                            node.value, ast.Name
                        ):
                            if node.value.id == "logger" or node.value.id == "logging":
                                violations.extend([f"{relative_path}:{node.lineno}"])
                        # Check for logging function calls
                        elif (
                            isinstance(node, ast.Call)
                            and isinstance(node.func, ast.Attribute)
                            and isinstance(node.func.value, ast.Name)
                            and node.func.value.id == "logging"
                        ):
                            violations.extend([f"{relative_path}:{node.lineno}"])
                except SyntaxError:
                    pass

    assert not violations, f"Logging found outside of allowed files: {violations}"


def test_handle_api_errors_decorator_exists():
    """Ensure @handle_api_errors decorator is defined and available."""
    errors_file = Path("utils/api/errors.py")
    assert errors_file.exists(), "utils/api/errors.py not found"

    with open(errors_file) as f:
        content = f.read()

    assert "def handle_api_errors" in content, "@handle_api_errors decorator not found"
    assert "@functools.wraps(func)" in content or "@wraps(func)" in content, (
        "Decorator doesn't properly wrap functions"
    )
