import unittest
from modules.memory import load_memory, save_memory

class TestSemanticMemory(unittest.TestCase):
    def test_memory_functions(self):
        self.assertIsNotNone(load_memory)
        self.assertIsNotNone(save_memory)
