# Focus Empty Space Writer

A minimalistic, distraction-free markdown note-taking application.

## Features

- Full-screen mode for maximum focus
- Clean, minimalistic interface
- Adjustable font size
- Cursor position highlighting
- Markdown support
- Escape key to toggle fullscreen mode

## Installation

1. Make sure you have Python 3.8+ installed
2. Install Poetry if you haven't already:
   ```bash
   pip install poetry
   ```
3. Clone this repository
4. Navigate to the project directory and install dependencies:
   ```bash
   poetry install
   ```

## Usage

To start the application, you can use either of these methods:

1. Using Poetry:
   ```bash
   poetry run focus-emty-space-writer
   ```

2. Running the Python file directly:
   ```bash
   poetry run python src/main.py
   ```

### Controls

- `+` and `-` buttons: Adjust font size
- `Escape`: Toggle fullscreen mode
- The cursor position is highlighted briefly when typing

## Development

The project uses Poetry for dependency management and follows a standard Python package structure:

```
focus-emty-space-writer/
├── src/
│   └── main.py
├── pyproject.toml
└── README.md
```

## License

MIT License
