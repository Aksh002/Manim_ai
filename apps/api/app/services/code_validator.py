import ast
from dataclasses import dataclass, field

FORBIDDEN_IMPORTS = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "pathlib",
    "shutil",
    "requests",
    "httpx",
    "urllib",
}

FORBIDDEN_CALLS = {"eval", "exec", "open", "__import__", "compile", "input"}


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)


class CodeValidator:
    def validate(self, code: str) -> ValidationResult:
        errors: list[str] = []

        if len(code.encode("utf-8")) > 100_000:
            errors.append("Code exceeds max size 100KB")

        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            return ValidationResult(ok=False, errors=[f"Syntax error: {exc.msg} at line {exc.lineno}"])

        has_required_import = False
        has_scene = False
        has_construct = False

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == "manim":
                    has_required_import = True
                elif node.module and node.module.split(".")[0] in FORBIDDEN_IMPORTS:
                    errors.append(f"Forbidden import from: {node.module}")

            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in FORBIDDEN_IMPORTS:
                        errors.append(f"Forbidden import: {alias.name}")

            if isinstance(node, ast.Call):
                fn_name = None
                if isinstance(node.func, ast.Name):
                    fn_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    fn_name = node.func.attr
                if fn_name in FORBIDDEN_CALLS:
                    errors.append(f"Forbidden call: {fn_name}")

            if isinstance(node, ast.ClassDef) and node.name == "GeneratedScene":
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "Scene":
                        has_scene = True
                for child in node.body:
                    if isinstance(child, ast.FunctionDef) and child.name == "construct":
                        has_construct = True

        if not has_required_import:
            errors.append("Missing required import: from manim import *")
        if not has_scene:
            errors.append("Missing required class: GeneratedScene(Scene)")
        if not has_construct:
            errors.append("Missing required method: construct(self)")

        return ValidationResult(ok=not errors, errors=errors)
