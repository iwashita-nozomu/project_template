# @dependency-start
# contract configuration
# responsibility Defines CTest consumers and the cpp-tests aggregate target.
# upstream design ../vendor/agent-canon/documents/design/cpp-build-layout.md test graph and aggregate contract
# downstream implementation ../CMakeLists.txt provides cpp-core
# @dependency-end

file(
  GLOB PROJECT_TEMPLATE_CPP_TEST_SOURCES
  CONFIGURE_DEPENDS
  "${CMAKE_CURRENT_SOURCE_DIR}/*.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/*.cc"
  "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/*.cxx"
)

add_custom_target(cpp-tests)

foreach(test_source IN LISTS PROJECT_TEMPLATE_CPP_TEST_SOURCES)
  get_filename_component(test_name "${test_source}" NAME_WE)
  string(MAKE_C_IDENTIFIER "${test_name}" test_identifier)
  set(test_target "cpp-test-${test_identifier}")
  add_executable("${test_target}" "${test_source}")
  target_link_libraries("${test_target}" PRIVATE cpp-core)
  add_dependencies(cpp-tests "${test_target}")
  add_test(NAME "${test_target}" COMMAND "${test_target}")
endforeach()
