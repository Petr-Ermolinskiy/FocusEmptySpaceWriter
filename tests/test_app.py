"""
Test suite for the Focus Empty Space Writer application.

To run the tests using Poetry:
    poetry run python -m unittest tests/test_app.py

Or using pytest:
    poetry run pytest tests/test_app.py
"""

import unittest
import threading
import time
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.FocusSpace import FocusSpace
import customtkinter as ctk

class TestApp(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = None
        self.app_thread = None

    def tearDown(self):
        """Clean up after test"""
        if self.app:
            self.app.after(100, self.app.destroy)
            if self.app_thread:
                self.app_thread.join(timeout=2)

    def test_app_startup(self):
        """Test if the application can be started and run properly"""
        def run_app():
            self.app = FocusSpace()
            self.app.mainloop()

        # Start the app in a separate thread
        self.app_thread = threading.Thread(target=run_app)
        self.app_thread.daemon = True
        self.app_thread.start()

        # Wait for the app to initialize
        time.sleep(1)

        # Check if the app was created and is running
        self.assertIsNotNone(self.app, "Application failed to start")
        
        # Check if the main window exists
        self.assertTrue(self.app.winfo_exists(), "Main window does not exist")
        
        # Check if the text widget exists
        self.assertTrue(hasattr(self.app, 'text_widget'), "Text widget does not exist")
        self.assertTrue(self.app.text_widget.winfo_exists(), "Text widget is not properly initialized")
        
        # Check if the menu frame exists
        self.assertTrue(hasattr(self.app, 'menu_frame'), "Menu frame does not exist")
        self.assertTrue(self.app.menu_frame.winfo_exists(), "Menu frame is not properly initialized")
        
        # Check if settings were loaded
        self.assertTrue(hasattr(self.app, 'settings'), "Settings were not loaded")
        self.assertIsInstance(self.app.settings, dict, "Settings is not a dictionary")
        
        # Check if fonts were loaded
        self.assertTrue(hasattr(self.app, 'available_fonts'), "Available fonts were not loaded")
        self.assertIsInstance(self.app.available_fonts, list, "Available fonts is not a list")
        self.assertTrue(len(self.app.available_fonts) > 0, "No fonts were loaded")

if __name__ == '__main__':
    unittest.main() 