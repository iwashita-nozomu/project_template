function(project_template_detect_jaxlib_include out_var)
  if(NOT Python3_EXECUTABLE)
    find_package(Python3 REQUIRED COMPONENTS Interpreter)
  endif()

  execute_process(
    COMMAND
      "${Python3_EXECUTABLE}" -c
      "import pathlib; import jaxlib; include_dir = pathlib.Path(jaxlib.__file__).resolve().parent / 'include'; header = include_dir / 'xla' / 'ffi' / 'api' / 'c_api.h'; assert header.is_file(), header; print(include_dir)"
    RESULT_VARIABLE _jaxlib_include_status
    OUTPUT_VARIABLE _jaxlib_include_dir
    ERROR_VARIABLE _jaxlib_include_error
    OUTPUT_STRIP_TRAILING_WHITESPACE
  )

  if(NOT _jaxlib_include_status EQUAL 0)
    message(FATAL_ERROR "failed to detect jaxlib include directory: ${_jaxlib_include_error}")
  endif()

  set(${out_var} "${_jaxlib_include_dir}" PARENT_SCOPE)
endfunction()
