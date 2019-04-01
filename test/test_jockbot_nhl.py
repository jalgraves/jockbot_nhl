import unittest
from jockbot_nhl import nhl


class TestNHL(unittest.TestCase):
    """Test nhl.py"""
    def test_nhl(self):
        team = nhl.NHLTeam('boston')
        self.assertTrue(isinstance(team.name, str))


if __name__ == '__main__':
    unittest.main()
