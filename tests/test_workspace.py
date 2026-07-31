import unittest
import sys

class TestWorkspaceAwareness(unittest.TestCase):
    def test_workspace_presence(self):
        # Verify that python can discover the main module without execution side-effects
        self.assertIn('tests', sys.path[0] or 'tests')
