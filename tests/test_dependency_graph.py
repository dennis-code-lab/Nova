import unittest
from modules.dependency_graph import DependencyGraphEngine

class TestDependencyGraph(unittest.TestCase):
    def test_engine_initialization(self):
        engine = DependencyGraphEngine()
        self.assertIsNotNone(engine)
