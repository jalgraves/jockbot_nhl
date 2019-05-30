import unittest
import types

from jockbot_nhl import nhl


class TestNHL(unittest.TestCase):
    """Test nhl.py"""
    def setUp(self):
        self.league = nhl.NHL()
        self.team = nhl.NHLTeam('boston')

    def test_nhl(self):
        self.assertEqual(self.league.current_season, '20182019', 'Incorrect Seasson')
        self.assertEqual(self.team.name, 'Boston Bruins', 'Incorrect team')

    def test_team_id(self):
        team_id = nhl._team_id('boston')
        self.assertEqual(team_id, 6, 'Incorrect Team ID')

    def test_divisions(self):
        """Test _divisions function"""
        divisions = nhl._divisions()
        message = f"divisions returned {type(divisions)} not generator"
        self.assertTrue(isinstance(divisions, types.GeneratorType), message)

    def test_games_on_date(self):
        """Test _games_on_date function"""
        games = nhl._games_on_date('2019-05-27')
        message = f"Games: {games}"
        self.assertTrue(isinstance(games, dict), message)

    def test_get_team_info(self):
        """Test NHL.get_team_info function"""
        info = self.league.get_team_info(team_id=6)
        self.assertTrue(isinstance(info, dict), 'No team info')

    def test_get_team_stats(self):
        """Test NHL.get_team_stats function"""
        stats = self.league.get_team_stats(team_id=6)
        self.assertTrue(isinstance(stats, dict), 'No team info')

    def test_get_team_roster(self):
        """Test NHL.get_team_roster function"""
        roster = self.league.get_team_roster(team_id=6)
        self.assertTrue(isinstance(roster, list), 'Unable to get roster')

    def test_get_team_schedule(self):
        """Test NHL.get_team_schedule function"""
        schedule = self.league.get_team_schedule(team_id=6)
        message = f"schedule returned {type(schedule)} not generator"
        self.assertTrue(isinstance(schedule, types.GeneratorType), message)


if __name__ == '__main__':
    unittest.main()
