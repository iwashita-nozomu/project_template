# @dependency-start
# contract configuration
# responsibility Defines the root C++ project, install surface, and CTest entrypoint.
# upstream design documents/design/cpp-build-layout.md root source and test layout
# downstream implementation include/project/version.hpp public header
# downstream implementation src/version.cpp production implementation
# downstream implementation test/cpp/CMakeLists.txt CTest consumer
# @dependency-end

cmake_minimum_required(VERSION 3.22)

project(project_template VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

add_library(project-core STATIC src/version.cpp)
add_library(project::core ALIAS project-core)
set_target_properties(project-core PROPERTIES EXPORT_NAME core)
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

include(CTest)
if(BUILD_TESTING)
  add_subdirectory(test/cpp)
endif()
