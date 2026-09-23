# Docker environment

`docker/Dockerfile` is a single Ubuntu 24.04 dependency-installation example.
It demonstrates OS packages, an image-local Python virtual environment, a
hash-pinned [Python dependency lock](../dependencies/python/requirements.txt),
and a non-root runtime user.

```bash
docker build -f docker/Dockerfile -t project-template:dependencies .
docker run --rm project-template:dependencies python --version
```

The image contains the reviewed project source and runs as the non-root
`project` user. Derived projects may replace the dependency lock, add build
tools, and choose their own entrypoint and validation commands.

Keep Python dependency definitions under [dependencies/](../dependencies/README.md)
and OS packages in the Dockerfile. The Python lock is copied before the source
snapshot to preserve dependency layer caching. C++ library dependencies belong
in the root CMake project and are resolved when that project is configured;
experiments and validation cases consume its targets. See the
[C++ build layout](../documents/design/cpp-build-layout.md).

This template does not preinstall scientific Python, notebook, CUDA, GPU, or
general developer-tool profiles.

## Run a source file

The root [Makefile](../Makefile) provides optional `make <file>` using the image
above. This helper is not a project bootstrap or a rule for derived projects.
The host needs GNU Make, Docker with a working local daemon, and standard Unix
shell utilities. The compiler, CMake, Ninja, and Python run inside Docker.

Each invocation builds `docker/Dockerfile` using Docker's cache, then bind-mounts
the current repository so edits and ignored source files are available. Set
`RUN_IMAGE=<tag>` to choose the image tag (default `project-template:dependencies`).
The process runs with the repository root as its working directory; relative
output paths persist in the host checkout. Place generated output in `workspace/`
or another project-owned ignored result directory.

- A path selects an existing `.py`, `.cpp`, `.cc`, or `.cxx` file inside the repository.
- A bare filename must be unique. Discovery excludes `.git`, virtual environments,
  `workspace`, `build`, `dist`, `.state`, `vendor`, and Python cache directories.
  Use an explicit path for a source under an excluded directory.
- Python runs directly using the image's virtual environment.
- C++ uses the nearest enclosing `CMakeLists.txt`, which must be a standalone
  configure entrypoint. The runner queries CMake's File API to find the executable
  target containing that source, builds that target and its dependencies, then
  runs the reported artifact. Target and source names need not match.
- Multiple matching files or executable targets are errors with matching names.
  Library-only sources cannot be run. The root library never reads experiment
  or validation projects; the selected consumer owns its configuration.

Pass arguments with `ARGS='"two words" --flag'`. The runner splits this text into
arguments without evaluating it as a shell command. Every requested file target
runs even when that file already exists. Program failures fail the Docker command
and Make recipe; GNU Make reports recipe failure with its own exit code, usually 2.
Paths containing whitespace are not supported as Make goals.

C++ build directories live under `workspace/run-file/<project-path>/` (the root
project uses `_root`). Rootless Docker runs with container UID 0, which maps to
the invoking host user; rootful Docker uses the host UID/GID. No privileged mode
is used. This keeps bind-mounted build and result files owned by the host user.
Experiment-specific source remains on its experiment branch; the runner does not
promote or merge it into `main`.
