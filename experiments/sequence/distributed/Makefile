MAKEFLAGS += --silent

BUILD_DIR = build

all: 
	rm -rf $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)
	cp -R client.py $(BUILD_DIR)/
	cp -R router.py $(BUILD_DIR)/
	cp -R server.py $(BUILD_DIR)/
	cp -R sequence $(BUILD_DIR)/
	cp -R synchronizer $(BUILD_DIR)/
	cp -R utils $(BUILD_DIR)/

.PHONY: all
