#include <cstddef>
#include <xla/ffi/api/c_api.h>
#include <xla/ffi/api/ffi.h>

int main() {
  const std::size_t api_struct_size = sizeof(XLA_FFI_Api);
  return api_struct_size > 0 ? 0 : 1;
}
