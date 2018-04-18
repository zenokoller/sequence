MAKEFLAGS += --silent

BUILD_DIR = build

all: 
	rm -rf $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)
	cp -R nodes $(BUILD_DIR)/
	cp -R process_flows $(BUILD_DIR)/
	cp -R sequence $(BUILD_DIR)/
	cp -R utils $(BUILD_DIR)/

.PHONY: all
