.PHONY: all test clean build_win build_mac all_win all_mac

# Default target - show help
all:
	@echo "Available targets:"
	@echo "  build_win    - Build Windows executable"
	@echo "  build_mac    - Build macOS application"
	@echo "  all_win      - Test + Build Windows + Clean"
	@echo "  all_mac      - Test + Build macOS + Clean"
	@echo "  test         - Run unit tests"
	@echo "  clean        - Clean build artifacts"

# Run tests
test:
	poetry run python -m unittest tests/test_app.py

# Windows-specific build
build_win:
	poetry run pyinstaller --noconfirm --onefile --windowed \
		--icon=assets/icon.ico \
		--name="focus-empty-space-writer" \
		--add-data="src;src" \
		--add-data="assets;assets" \
		--hidden-import=customtkinter \
		--hidden-import=markdown \
		--hidden-import=src.FocusSpace \
		--paths=. \
		src/main.py

# macOS-specific build
build_mac:
	poetry run pyinstaller --noconfirm --onedir --windowed \
		--icon=assets/icon.icns \
		--name="focus-empty-space-writer" \
		--add-data="src:src" \
		--add-data="assets:assets" \
		--hidden-import=customtkinter \
		--hidden-import=markdown \
		--hidden-import=src.FocusSpace \
		--osx-bundle-identifier="com.yourdomain.focus-empty-space-writer" \
		--paths=. \
		src/main.py

# Complete Windows workflow
all_win: test build_win clean

# Complete macOS workflow
all_mac: test build_mac clean

# Clean build artifacts
clean:
	poetry run python clean.py