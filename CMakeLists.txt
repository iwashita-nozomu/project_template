# @dependency-start
# contract configuration
# responsibility Defines the reusable C++ library, dependencies, and install surface.
# upstream design documents/design/cpp-build-layout.md library build ownership
# downstream implementation include/project/version.hpp public header
# downstream implementation src/version.cpp production implementation
# @dependency-end

cmake_minimum_required(VERSION 3.22)

project(project_template VERSION 0.1.0 LANGUAGES CXX)

if(PROJECT_IS_TOP_LEVEL)
  set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
  set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
  set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
endif()

# Declare library dependencies here so every consumer gets the same build graph.
# Replace the placeholders and uncomment only when a dependency is needed:
# include(FetchContent)
# FetchContent_Declare(
#   example_dependency
#   GIT_REPOSITORY https://example.com/owner/dependency.git
#   GIT_TAG <full-commit-sha>
# )
# FetchContent_MakeAvailable(example_dependency)
# Link its target to project-core below with the appropriate PUBLIC/PRIVATE scope.

add_library(project-core STATIC src/version.cpp)
add_library(project::core ALIAS project-core)
set_target_properties(project-core PROPERTIES EXPORT_NAME core CXX_EXTENSIONS OFF)
target_include_directories(
  project-core
  PUBLIC
    "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
    "$<INSTALL_INTERFACE:include>"
)
target_compile_features(project-core PUBLIC cxx_std_20)

install(
  TARGETS project-core
  EXPORT projectTargets
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
  INCLUDES DESTINATION include
)
install(DIRECTORY include/ DESTINATION include)
install(
  EXPORT projectTargets
  FILE projectTargets.cmake
  NAMESPACE project::
  DESTINATION lib/cmake/project
)
