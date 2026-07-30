# @dependency-start
# contract configuration
# responsibility Defines the single C++ project entrypoint and shared target/artifact contract.
# upstream design ../vendor/agent-canon/documents/design/cpp-build-layout.md C++ project boundary and migration map
# downstream implementation tests/CMakeLists.txt test consumers of cpp-core
# downstream implementation experiments/CMakeLists.txt native experiment consumers of cpp-core
# @dependency-end

cmake_minimum_required(VERSION 3.22)

project(project_template LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

get_filename_component(
  PROJECT_TEMPLATE_ROOT_DIR
  "${CMAKE_CURRENT_SOURCE_DIR}/.."
  REALPATH
)
get_filename_component(PROJECT_TEMPLATE_CPP_PROFILE "${CMAKE_BINARY_DIR}" NAME)

set(
  PROJECT_TEMPLATE_CPP_BUILD_ROOT
  "${PROJECT_TEMPLATE_ROOT_DIR}/build/cpp"
  CACHE PATH "Root for out-of-source C++ build trees."
)
set(
  PROJECT_TEMPLATE_CPP_BUILD_DIR
  "${PROJECT_TEMPLATE_CPP_BUILD_ROOT}/${PROJECT_TEMPLATE_CPP_PROFILE}"
  CACHE PATH "Canonical build tree for the configured C++ profile."
)
set(
  PROJECT_TEMPLATE_CPP_INSTALL_ROOT
  "${PROJECT_TEMPLATE_ROOT_DIR}/.state/cpp-install"
  CACHE PATH "Root for reusable local C++ install trees."
)
set(
  PROJECT_TEMPLATE_EXPERIMENT_RESULT_ROOT
  "${PROJECT_TEMPLATE_ROOT_DIR}/experiments"
  CACHE PATH "Root for experiment lifecycle result directories."
)

if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  set(
    CMAKE_INSTALL_PREFIX
    "${PROJECT_TEMPLATE_CPP_INSTALL_ROOT}/${PROJECT_TEMPLATE_CPP_PROFILE}"
    CACHE PATH "Default reusable install prefix for the configured C++ profile."
    FORCE
  )
endif()

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${PROJECT_TEMPLATE_CPP_BUILD_DIR}/lib")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${PROJECT_TEMPLATE_CPP_BUILD_DIR}/lib")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${PROJECT_TEMPLATE_CPP_BUILD_DIR}/bin")

include(CTest)

set(PROJECT_TEMPLATE_CPP_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")
set(PROJECT_TEMPLATE_CPP_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src")
file(
  GLOB PROJECT_TEMPLATE_CPP_CORE_SOURCES
  CONFIGURE_DEPENDS
  "${PROJECT_TEMPLATE_CPP_SOURCE_DIR}/*.c"
  "${PROJECT_TEMPLATE_CPP_SOURCE_DIR}/*.cc"
  "${PROJECT_TEMPLATE_CPP_SOURCE_DIR}/*.cpp"
  "${PROJECT_TEMPLATE_CPP_SOURCE_DIR}/*.cxx"
)

if(PROJECT_TEMPLATE_CPP_CORE_SOURCES)
  add_library(cpp-core STATIC ${PROJECT_TEMPLATE_CPP_CORE_SOURCES})
  set(PROJECT_TEMPLATE_CPP_CORE_USAGE_SCOPE PUBLIC)
else()
  add_library(cpp-core INTERFACE)
  set(PROJECT_TEMPLATE_CPP_CORE_USAGE_SCOPE INTERFACE)
endif()

target_include_directories(
  cpp-core
  ${PROJECT_TEMPLATE_CPP_CORE_USAGE_SCOPE}
    "$<BUILD_INTERFACE:${PROJECT_TEMPLATE_CPP_INCLUDE_DIR}>"
    "$<INSTALL_INTERFACE:include>"
)
target_compile_features(
  cpp-core
  ${PROJECT_TEMPLATE_CPP_CORE_USAGE_SCOPE}
    cxx_std_17
)

include(CMakePackageConfigHelpers)
configure_package_config_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/cmake/project_templateConfig.cmake.in"
  "${CMAKE_CURRENT_BINARY_DIR}/project_templateConfig.cmake"
  INSTALL_DESTINATION "lib/cmake/project_template"
  NO_CHECK_REQUIRED_COMPONENTS_MACRO
)

install(
  TARGETS cpp-core
  EXPORT project_templateTargets
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
  INCLUDES DESTINATION include
)
install(
  DIRECTORY "${PROJECT_TEMPLATE_CPP_INCLUDE_DIR}/"
  DESTINATION include
  FILES_MATCHING
    PATTERN "*.h"
    PATTERN "*.hh"
    PATTERN "*.hpp"
    PATTERN "*.hxx"
)
install(
  EXPORT project_templateTargets
  FILE project_templateTargets.cmake
  NAMESPACE project_template::
  DESTINATION lib/cmake/project_template
)
install(
  FILES "${CMAKE_CURRENT_BINARY_DIR}/project_templateConfig.cmake"
  DESTINATION lib/cmake/project_template
)

add_subdirectory(tests)
add_subdirectory(experiments)
