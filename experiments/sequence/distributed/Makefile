MAKEFLAGS += --silent

BUILD_DIR = build

all: 
	rm -rf $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)
	cp -R client $(BUILD_DIR)/
	cp -R router $(BUILD_DIR)/
	cp -R server $(BUILD_DIR)/

	# Dependencies
	cp -R ../generator $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)/utils
	cp ../utils/managed_trace.py $(BUILD_DIR)/utils

.PHONY: all
