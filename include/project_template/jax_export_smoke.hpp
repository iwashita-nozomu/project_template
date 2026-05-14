// @dependency-start
// responsibility Provides a minimal XLA FFI header smoke surface.
// upstream design ../../vendor/agent-canon/documents/cpp-build-layout.md defines C++ header placement.
// @dependency-end

#pragma once

#include <cstddef>
#include <xla/ffi/api/c_api.h>
#include <xla/ffi/api/ffi.h>

namespace project_template {

inline constexpr bool xla_ffi_headers_available() noexcept {
  return sizeof(XLA_FFI_Api) > 0;
}

inline constexpr std::size_t xla_ffi_api_size() noexcept {
  return sizeof(XLA_FFI_Api);
}

}  // namespace project_template
