import unittest
from modules.review import CodeReviewer

class TestReview(unittest.TestCase):
    def test_reviewer_initialization(self):
        reviewer = CodeReviewer()
        self.assertIsNotNone(reviewer)
