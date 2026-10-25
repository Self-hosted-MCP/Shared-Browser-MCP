"""The docs stay true: every link and anchor works, every setting and tool is documented, no em dashes.
Runs with pytest alone (no project packages needed): tools and settings are read from the source files."""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = sorted([*ROOT.glob("*.md"), *(ROOT / "docs").glob("*.md")])
LINK = re.compile(r"\]\(([^)\s]+)\)|href=\"([^\"]+)\"|src=\"([^\"]+)\"")
EM = chr(0x2014)  # the em dash character


def slug(heading: str) -> str:
    """GitHub's anchor for a heading."""
    text = re.sub(r"[`*_]|<[^>]+>", "", heading.strip().lower())
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def anchors(path: Path) -> set[str]:
    seen: dict[str, int] = {}
    out = set()
    in_code = False
    for line in path.read_text("utf-8").splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if in_code or not line.startswith("#"):
            continue
        s = slug(line.lstrip("#"))
        n = seen.get(s, 0)
        seen[s] = n + 1
        out.add(s if n == 0 else f"{s}-{n}")
    return out


def tool_names() -> list[str]:
    """Every function in server.py decorated with @tool(...)."""
    tree = ast.parse((ROOT / "mcp" / "src" / "sbmcp" / "server.py").read_text("utf-8"))
    return [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and any(isinstance(d, ast.Call) and getattr(d.func, "id", "") == "tool" for d in n.decorator_list)]


def env_example_names() -> list[str]:
    text = (ROOT / ".env.example").read_text("utf-8")
    return re.findall(r"^([A-Z][A-Z0-9_]+)=", text, flags=re.M)


def test_links_and_anchors_work():
    broken = []
    for doc in DOCS:
        text = re.sub(r"```.*?```", "", doc.read_text("utf-8"), flags=re.S)
        for m in LINK.finditer(text):
            target = next(g for g in m.groups() if g)
            if re.match(r"[a-z]+:", target) or target.startswith("//"):
                continue
            path, _, anchor = target.partition("#")
            dest = (doc.parent / path).resolve() if path else doc
            if not dest.exists():
                broken.append(f"{doc.name}: {target}")
            elif anchor and dest.suffix == ".md" and anchor not in anchors(dest):
                broken.append(f"{doc.name}: {target} (no such heading)")
    assert not broken, "\n".join(broken)


def test_every_setting_is_documented():
    settings = (ROOT / "docs" / "settings.md").read_text("utf-8")
    missing = [n for n in env_example_names() if f"`{n}`" not in settings]
    assert not missing, f"not in docs/settings.md: {missing}"


def test_every_compose_setting_is_in_env_example():
    used = set()
    for f in ROOT.glob("docker-compose*.yml"):
        used |= set(re.findall(r"\$\{([A-Z][A-Z0-9_]+)", f.read_text("utf-8")))
    missing = sorted(used - set(env_example_names()))
    assert not missing, f"not in .env.example: {missing}"


def test_every_tool_is_documented():
    names = tool_names()
    assert len(names) > 20, names
    tools = (ROOT / "docs" / "tools.md").read_text("utf-8")
    missing = [n for n in names if f"`{n}`" not in tools]
    assert not missing, f"not in docs/tools.md: {missing}"


def test_no_em_dashes():
    found = [f"{d.name}:{i}" for d in DOCS for i, line in enumerate(d.read_text("utf-8").splitlines(), 1)
             if EM in line or (" " + chr(0x2013) + " ") in line]
    assert not found, found
