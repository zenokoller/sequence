MAKEFLAGS += --silent

BUILD_DIR = build

all: 
	rm -rf $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)
	cp -R nodes $(BUILD_DIR)/
	cp -R config $(BUILD_DIR)/
	cp -R sequence $(BUILD_DIR)/
	cp -R synchronizer $(BUILD_DIR)/
	cp -R detector $(BUILD_DIR)/
	cp -R reporter $(BUILD_DIR)/
	cp -R utils $(BUILD_DIR)/

.PHONY: all
