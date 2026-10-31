import sys

from PySide6.QtWidgets import (
    QApplication,
)

from src.FocusSpace import FocusSpace


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FocusSpace")
    app.setApplicationDisplayName("Focus Empty Space Writer")
    w = FocusSpace()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
