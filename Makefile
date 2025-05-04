.PHONY: all test build clean

# Default target
all: test build clean

# Run tests
test:
	poetry run python -m unittest tests/test_app.py

# Build for all platforms
build:
	poetry run pyinstaller --noconfirm --onefile --windowed \
		--icon=assets/icon.ico \
		--name=focus-empty-space-writer \
		--add-data="src;src" \
		--add-data="assets;assets" \
		--hidden-import=customtkinter \
		--hidden-import=markdown \
		--hidden-import=src.FocusSpace \
		--paths=. \
		src/main.py

# Clean build artifacts
clean:
	poetry run python clean.py 