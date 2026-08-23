# @dependency-start
# contract configuration
# responsibility Defines the concrete CTest consumer for the root project library.
# upstream design ../../documents/design/cpp-build-layout.md root test ownership
# upstream implementation ../../CMakeLists.txt provides project::core
# downstream implementation version_test.cpp validates the installed public behavior
# @dependency-end

add_executable(project-version-test version_test.cpp)
target_link_libraries(project-version-test PRIVATE project::core)
add_test(NAME project-version-test COMMAND project-version-test)
