# Project dependencies

[python/requirements.txt](python/requirements.txt) holds the hash-pinned Python
dependency example consumed by the [Dockerfile](../docker/Dockerfile). Replace
its packages with the derived project's dependencies, retaining exact versions
and distribution hashes. From a project virtual environment:

```bash
python -m pip install --require-hashes -r dependencies/python/requirements.txt
```

C++ library dependencies belong in the root [CMakeLists.txt](../CMakeLists.txt),
next to the targets that use them. Declare them with `FetchContent_Declare()`,
pin `GIT_TAG` to a full commit SHA, and make their targets available with
`FetchContent_MakeAvailable()`. Each experiment or validation project declares
only its own additional dependencies; it consumes the library target to obtain
the library's dependency graph. The template has no external C++ dependency
and performs no downloads. See the [C++ build layout](../documents/design/cpp-build-layout.md).
