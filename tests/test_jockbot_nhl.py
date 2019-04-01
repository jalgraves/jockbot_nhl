import unittest
from jockbot_nhl.nhl import NHL, NHLTeam


class TestNHL(unittest.TestCase):
    """Test nhl.py"""
    def test_nhl(self):
        nhl = NHL()
        print(nhl.current_season)
        self.assertEqual(nhl.current_season, '20182019', 'Incorrect Seasson')

    def test_nhl_team(self):
        team = NHLTeam('boston')
        self.assertTrue(isinstance(team.name, str))


if __name__ == '__main__':
    unittest.main()
