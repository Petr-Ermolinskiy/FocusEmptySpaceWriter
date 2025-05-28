"""
Test suite for the Focus Empty Space Writer application.

To run the tests using Poetry:
    poetry run python -m unittest tests/test_app.py
"""

import unittest
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

    def tearDown(self):
        """Clean up after test"""
        if self.app:
            self.app.destroy()
            self.app = None

    def test_app_initialization(self):
        """Test if the application can be initialized properly"""
        # Create the app instance
        self.app = FocusSpace()
        
        # Check if the app was created
        self.assertIsNotNone(self.app, "Application failed to initialize")
        
        # Check if the main container exists
        self.assertTrue(hasattr(self.app, 'main_container'), "Main container not found")
        self.assertTrue(self.app.main_container.winfo_exists(), "Main container is not properly initialized")
        
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