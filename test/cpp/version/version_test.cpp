#include "project/version.hpp"

int main() {
  return project::version() == "0.1.0" ? 0 : 1;
}
