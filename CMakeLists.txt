# @dependency-start
# responsibility Defines the repository C++ build entrypoint and smoke target.
# upstream design vendor/agent-canon/documents/cpp-build-layout.md defines C++ build layout.
# downstream implementation include/project_template/jax_export_smoke.hpp provides the header smoke surface.
# downstream implementation docker/Dockerfile installs CMake and Ninja for container smoke builds.
# @dependency-end

cmake_minimum_required(VERSION 3.22)

project(project_template LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  set(
    CMAKE_INSTALL_PREFIX
    "${CMAKE_SOURCE_DIR}/.state/cpp-install/default"
    CACHE PATH "Default reusable install prefix for local C++ artifacts." FORCE
  )
endif()

set(
  PROJECT_TEMPLATE_CPP_BUILD_ROOT
  "${CMAKE_SOURCE_DIR}/build/cpp"
  CACHE PATH "Root for out-of-source C++ build trees."
)
set(
  PROJECT_TEMPLATE_CPP_INSTALL_ROOT
  "${CMAKE_SOURCE_DIR}/.state/cpp-install"
  CACHE PATH "Root for reusable local C++ install trees."
)
set(
  PROJECT_TEMPLATE_JAX_EXPORT_ROOT
  "${CMAKE_SOURCE_DIR}/.state/jax-export"
  CACHE PATH "Root for reusable local jax.export artifacts."
)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

include(CTest)

find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
include(ProjectTemplateJaxExport)
project_template_detect_jaxlib_include(PROJECT_TEMPLATE_JAXLIB_INCLUDE_DIR)

add_library(project_template_cpp INTERFACE)
target_include_directories(
  project_template_cpp
  INTERFACE
    "${CMAKE_CURRENT_SOURCE_DIR}/include"
    "${PROJECT_TEMPLATE_JAXLIB_INCLUDE_DIR}"
)
target_compile_features(project_template_cpp INTERFACE cxx_std_17)

option(PROJECT_TEMPLATE_ENABLE_CPP_SMOKE "Build the template C++ smoke target." ON)

if(PROJECT_TEMPLATE_ENABLE_CPP_SMOKE)
  add_executable(
    project_template_cpp_smoke
    tests/cpp/smoke/jax_export_header_smoke.cpp
  )
  target_link_libraries(project_template_cpp_smoke PRIVATE project_template_cpp)
  if(BUILD_TESTING)
    add_test(NAME project_template_cpp_smoke COMMAND project_template_cpp_smoke)
  endif()
  install(TARGETS project_template_cpp_smoke RUNTIME DESTINATION bin)
endif()
