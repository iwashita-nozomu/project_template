# Project dependencies

Place external dependency installation definitions here, grouped by language.
The [Docker example](../docker/README.md) consumes these definitions alongside
its OS package setup. Derived projects may also use them outside Docker.

| Path | Responsibility |
| --- | --- |
| [cpp/CMakeLists.txt](cpp/CMakeLists.txt) | Independent C++ dependency build and installation entrypoint |
| [python/requirements.txt](python/requirements.txt) | Hash-pinned Python dependency example |

## C++ dependencies

The C++ entrypoint is an empty template. It downloads no libraries and can be
configured and built from the repository root with CMake 3.22 or newer:

```bash
cmake -S dependencies/cpp -B workspace/dependencies/cpp \
  -DCMAKE_INSTALL_PREFIX="$PWD/workspace/dependencies/install"
cmake --build workspace/dependencies/cpp --parallel
```

Add the libraries your project needs to `cpp/CMakeLists.txt`, using a standard
CMake mechanism such as `ExternalProject_Add`. Pin each download to a commit
SHA or an archive hash, and pass the install prefix to each dependency's
configure step. Define and document its build and installation targets; the
empty template has no install rules.

Once dependencies are installed, pass their prefix to the product build:

```bash
cmake -S . -B workspace/project \
  -DCMAKE_PREFIX_PATH="$PWD/workspace/dependencies/install"
cmake --build workspace/project --parallel
```

Add `find_package()` and imported targets in the root product CMake as needed.
The current sample has no external C++ dependencies and builds directly without
running the dependency entrypoint. See the [C++ build layout](../documents/design/cpp-build-layout.md).

## Python dependencies

Replace the example packages in `python/requirements.txt` with your project's
Python dependencies, retaining exact versions and distribution hashes. In a
project virtual environment, install them from the repository root with:

```bash
python -m pip install --require-hashes -r dependencies/python/requirements.txt
```

The Dockerfile performs this installation in its image-local virtual environment.
