"""Every version place agrees (see CONTRIBUTING.md, Releases), and the tool count in the docs is the real one."""
import ast
import re
import tomllib
from pathlib import Path

MCP = Path(__file__).resolve().parent.parent
ROOT = MCP.parent


def test_every_version_place_agrees():
    pyproject = tomllib.loads((MCP / "pyproject.toml").read_text("utf-8"))["project"]["version"]
    init = re.search(r'__version__ = "([^"]+)"', (MCP / "src" / "sbmcp" / "__init__.py").read_text("utf-8")).group(1)
    citation = re.search(r"^version: \"?([^\"\n]+)\"?", (ROOT / "CITATION.cff").read_text("utf-8"), re.M).group(1)
    changelog = re.search(r"^## (\d+\.\d+\.\d+)", (ROOT / "CHANGELOG.md").read_text("utf-8"), re.M).group(1)
    assert pyproject == init == citation == changelog, (pyproject, init, citation, changelog)


def test_the_readme_names_the_real_number_of_tools():
    tree = ast.parse((MCP / "src" / "sbmcp" / "server.py").read_text("utf-8"))
    count = sum(1 for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and any(isinstance(d, ast.Call) and getattr(d.func, "id", "") == "tool" for d in n.decorator_list))
    assert f"{count} tools" in (ROOT / "README.md").read_text("utf-8")
