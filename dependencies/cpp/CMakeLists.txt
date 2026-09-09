# @dependency-start
# contract configuration
# responsibility Provides an independent entrypoint for C++ dependency installation.
# upstream design ../../documents/design/cpp-build-layout.md dependency and product build boundary
# upstream design ../README.md dependency addition and usage guide
# @dependency-end

cmake_minimum_required(VERSION 3.22)

project(project_dependencies LANGUAGES NONE)

# Add only the C++ libraries required by the derived project here.
# For example, use ExternalProject_Add with a fixed commit or URL_HASH,
# and pass CMAKE_INSTALL_PREFIX to each dependency's configure step.
# Enable C/CXX here if the chosen integration needs a compiler in this project.
# Keep dependency build/install steps independent of the root product build.
# This empty template downloads nothing and defines no install rules.
