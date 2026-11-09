# Focus Empty Space Writer

A distraction-free writing environment built with Python and PySide6.

![The window of app](images/window.png)

## Features

- Clean, minimalist interface
- Customizable margins
- Font size and family controls
- Fullscreen mode
- Keyboard shortcuts for quick access to features

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open File | `Ctrl + O` |
| Save File | `Ctrl + S` |
| Toggle Fullscreen | `Escape` |
| Increase Font Size | `Ctrl + ]` |
| Decrease Font Size | `Ctrl + [` |
| Increase Top Margin | `Ctrl + J` |
| Decrease Top Margin | `Ctrl + K` |
| Increase Left Margin | `Ctrl + L` |
| Decrease Left Margin | `Ctrl + H` |

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   uv sync
   ```

## Usage

You can run the application in two ways:

1. Using uv:
   ```bash
   uv run focus-emty-space-writer
   ```

2. Running the Python file directly:
   ```bash
   uv run python src/main.py
   ```

## Building

To build the application for your platform:

  ```bash
  make build_mac   # macOS
  make build_win   # Windows
  ```


## Development

The project uses uv for dependency management. Make sure you have uv installed before contributing.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
