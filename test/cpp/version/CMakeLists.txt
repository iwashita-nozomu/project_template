# @dependency-start
# contract configuration
# responsibility Builds a standalone version validation consumer of project::core.
# upstream design ../../../documents/design/cpp-build-layout.md consumer build contract
# upstream implementation ../../../CMakeLists.txt provides project::core
# downstream implementation version_test.cpp validates the public version
# @dependency-end

cmake_minimum_required(VERSION 3.22)
project(project_version_validation LANGUAGES CXX)

if(PROJECT_IS_TOP_LEVEL)
  enable_testing()
endif()

if(NOT TARGET project::core)
  add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../../.." "${CMAKE_CURRENT_BINARY_DIR}/project-library")
endif()

# Declare dependencies used only by this validation case here.
add_executable(project-version-test version_test.cpp)
target_link_libraries(project-version-test PRIVATE project::core)
add_test(NAME project-version-test COMMAND project-version-test)
