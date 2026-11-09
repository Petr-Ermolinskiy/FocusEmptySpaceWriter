"""
Test suite for the Focus Empty Space Writer application.

To run the tests using uv:
    uv run python -m unittest tests/test_app.py
"""

import os
import sys
import unittest

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Run Qt headlessly so the tests work in CI and on machines without a display
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from src.FocusSpace import FocusSpace


class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create a single QApplication for the whole test run."""
        cls.qapp = QApplication.instance() or QApplication([])

    def setUp(self):
        """Set up test environment"""
        self.app = FocusSpace()

    def tearDown(self):
        """Clean up after test"""
        if self.app:
            self.app.close()
            self.app.deleteLater()
            self.qapp.processEvents()
            self.app = None

    def test_app_initialization(self):
        """Test if the application can be initialized properly"""
        self.assertIsNotNone(self.app, "Application failed to initialize")
        self.assertIsNotNone(self.app.editor, "Editor was not created")

        # Check if settings were loaded
        self.assertTrue(hasattr(self.app, 'settings'), "Settings were not loaded")
        self.assertIsInstance(self.app.settings, dict, "Settings is not a dictionary")

        # Check if the default font settings were loaded
        self.assertGreater(self.app.font_size, 0, "Font size was not initialized")
        self.assertTrue(self.app.font_family, "Font family was not initialized")

    def test_headings_are_detected(self):
        """Test that the table of contents finds Markdown headings."""
        self.app.editor.setPlainText("# Title\n\nSome text\n\n## Section\n")
        headings = self.app._scan_headings()
        self.assertEqual([h[1] for h in headings], ["Title", "Section"])


if __name__ == '__main__':
    unittest.main()
