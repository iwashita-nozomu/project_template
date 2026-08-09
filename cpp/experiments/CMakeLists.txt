# @dependency-start
# contract configuration
# responsibility Defines native experiment consumers and the cpp-experiments aggregate target.
# upstream design ../../vendor/agent-canon/documents/design/cpp-build-layout.md experiment graph and result contract
# upstream implementation ../CMakeLists.txt provides cpp-core and the root result anchor
# @dependency-end

file(
  GLOB PROJECT_TEMPLATE_CPP_EXPERIMENT_SOURCES
  CONFIGURE_DEPENDS
  "${CMAKE_CURRENT_SOURCE_DIR}/*.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/*.cc"
  "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/*.cxx"
)

add_custom_target(cpp-experiments)

foreach(experiment_source IN LISTS PROJECT_TEMPLATE_CPP_EXPERIMENT_SOURCES)
  get_filename_component(experiment_name "${experiment_source}" NAME_WE)
  string(MAKE_C_IDENTIFIER "${experiment_name}" experiment_identifier)
  set(experiment_target "cpp-experiment-${experiment_identifier}")
  add_executable("${experiment_target}" "${experiment_source}")
  target_link_libraries("${experiment_target}" PRIVATE cpp-core)
  target_compile_definitions(
    "${experiment_target}"
    PRIVATE
      PROJECT_TEMPLATE_EXPERIMENT_RESULT_ROOT="${PROJECT_TEMPLATE_EXPERIMENT_RESULT_ROOT}"
  )
  add_dependencies(cpp-experiments "${experiment_target}")
endforeach()
