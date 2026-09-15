"""Resolve a source file and execute it using the container's toolchain."""

import json
import os
from pathlib import Path
import shlex
import subprocess
import sys


SKIP_DIRECTORIES = {
    ".git", ".venv", "venv", "workspace", "build", "dist", ".state", "vendor", "__pycache__"
}
CPP_SUFFIXES = {".cpp", ".cc", ".cxx"}


def resolve_source(root: Path, requested: str) -> Path:
    candidate = Path(requested)
    if candidate.is_absolute() or "/" in requested:
        matches = [root / candidate] if (root / candidate).is_file() else []
    else:
        matches = []
        for directory, children, files in os.walk(root):
            children[:] = sorted(name for name in children if name not in SKIP_DIRECTORIES)
            if requested in files:
                matches.append(Path(directory) / requested)
    if len(matches) != 1:
        details = "\n".join(f"  {path.relative_to(root)}" for path in sorted(matches))
        message = f"Expected one source file for {requested!r}; found {len(matches)}."
        if details:
            message += f"\n{details}\nUse a repository-relative path."
        raise ValueError(message)
    source = matches[0].resolve()
    if not source.is_relative_to(root):
        raise ValueError("The source file must be inside this repository.")
    if source.suffix not in CPP_SUFFIXES | {".py"}:
        raise ValueError("Supported source extensions: .cpp, .cc, .cxx, .py")
    return source


def executable_for_source(root: Path, source: Path) -> Path:
    project = source.parent
    while not (project / "CMakeLists.txt").is_file():
        if project == root:
            raise ValueError(f"No enclosing CMakeLists.txt for {source.relative_to(root)}")
        project = project.parent
    relative_project = project.relative_to(root)
    build = root / "workspace/run-file" / (str(relative_project) if relative_project.parts else "_root")
    query = build / ".cmake/api/v1/query"
    query.mkdir(parents=True, exist_ok=True)
    (query / "codemodel-v2").touch()
    subprocess.run(["cmake", "-S", str(project), "-B", str(build), "-G", "Ninja"], check=True)
    reply = build / ".cmake/api/v1/reply"
    index_path = max(reply.glob("index-*.json"), key=lambda path: path.stat().st_mtime_ns)
    index = json.loads(index_path.read_text())
    model = json.loads((reply / index["reply"]["codemodel-v2"]["jsonFile"]).read_text())
    source_root = Path(model["paths"]["source"])
    build_root = Path(model["paths"]["build"])
    matches = []
    for target_reference in model["configurations"][0]["targets"]:
        target = json.loads((reply / target_reference["jsonFile"]).read_text())
        if target["type"] == "EXECUTABLE" and any(
            (source_root / item["path"]).resolve() == source
            for item in target.get("sources", [])
        ):
            matches.append(target)
    if len(matches) != 1:
        names = ", ".join(sorted(target["name"] for target in matches))
        message = f"Expected one executable target containing {source.relative_to(root)}; found {len(matches)}"
        message += f": {names}" if names else ". Library-only sources cannot be run."
        raise ValueError(message)
    target = matches[0]
    artifacts = target.get("artifacts", [])
    if len(artifacts) != 1:
        raise ValueError(f"Expected one executable artifact for target {target['name']!r}.")
    subprocess.run(["cmake", "--build", str(build), "--target", target["name"], "--parallel"], check=True)
    return (build_root / artifacts[0]["path"]).resolve()


def main() -> None:
    root = Path.cwd().resolve()
    try:
        source = resolve_source(root, sys.argv[1])
        args = shlex.split(os.environ.get("RUN_ARGS", ""))
        if source.suffix == ".py":
            command = [sys.executable, str(source)]
        else:
            command = [str(executable_for_source(root, source))]
    except (ValueError, KeyError, OSError) as error:
        print(f"run-file: {error}", file=sys.stderr)
        raise SystemExit(2) from error
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from error
    os.execv(command[0], command + args)


if __name__ == "__main__":
    main()
