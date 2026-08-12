import unittest

from modules.engineering_simulator import EngineeringSimulator


class MockScore:
    def __init__(self, score):
        self.score = score


class MockRisk:
    def __init__(self, risk):
        self.risk = risk


class MockForecast:
    def __init__(self, health):
        self.predicted_health = health


class MockScoreEngine:
    def calculate(self, module):
        return MockScore(4.5)


class MockRiskEngine:
    def analyze(self, module):
        return MockRisk("HIGH")


class MockForecastEngine:
    def generate(self, limit=1):
        return [MockForecast(90.3)]


class TestEngineeringSimulator(unittest.TestCase):

    def setUp(self):
        self.simulator = EngineeringSimulator(
            MockScoreEngine(),
            MockRiskEngine(),
            MockForecastEngine(),
        )

    def test_simulation_returns_current_score(self):
        result = self.simulator.simulate(
            "modules.dependency_analyzer"
        )

        self.assertEqual(result.current_score, 4.5)

    def test_simulation_returns_current_risk(self):
        result = self.simulator.simulate(
            "modules.dependency_analyzer"
        )

        self.assertEqual(result.current_risk, "HIGH")

    def test_predicted_score_is_higher_than_current(self):
        result = self.simulator.simulate(
            "modules.dependency_analyzer"
        )

        self.assertGreater(
            result.predicted_score,
            result.current_score,
        )

    def test_predicted_score_does_not_exceed_ten(self):
        result = self.simulator.simulate(
            "modules.dependency_analyzer"
        )

        self.assertLessEqual(
            result.predicted_score,
            10.0,
        )

    def test_prediction_is_not_hard_coded_plus_three(self):
        result = self.simulator.simulate(
            "modules.dependency_analyzer"
        )

        self.assertNotEqual(
            result.predicted_score,
            result.current_score + 3.0,
        )

    def test_confidence_is_not_hard_coded_85(self):
        result = self.simulator.simulate(
            "modules.dependency_analyzer"
        )

        self.assertNotEqual(
            result.confidence,
            85,
        )

    def test_confidence_is_valid_percentage(self):
        result = self.simulator.simulate(
            "modules.dependency_analyzer"
        )

        self.assertGreaterEqual(result.confidence, 0)
        self.assertLessEqual(result.confidence, 100)


if __name__ == "__main__":
    unittest.main()