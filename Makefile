.DEFAULT_GOAL := help
.SUFFIXES:
.NOTPARALLEL:

export RUN_IMAGE ?= project-template:dependencies
export RUN_ARGS = $(ARGS)
export RUN_FILE = $@

.PHONY: help $(MAKECMDGOALS)
help:
	@printf '%s\n' 'make <path-or-unique-filename> [ARGS="arguments"]' 'Runs .py or builds and runs a C++ executable inside Docker.'

$(filter-out help,$(MAKECMDGOALS)):
	@sh tools/run_file.sh
