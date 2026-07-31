import unittest
from modules.refactor import RefactorEngine

class TestRefactor(unittest.TestCase):
    def test_engine_initialization(self):
        engine = RefactorEngine()
        self.assertIsNotNone(engine)
