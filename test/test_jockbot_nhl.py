import unittest
import types

from jockbot_nhl import nhl


class TestNHL(unittest.TestCase):
    """Test nhl.py"""
    def setUp(self):
        self.league = nhl.NHL()
        self.team = nhl.NHLTeam('boston')
        self.player = 'patrice bergeron'

    def test_nhl(self):
        self.assertEqual(self.league.current_season, '20182019', 'Incorrect Seasson')
        self.assertEqual(self.team.name, 'Boston Bruins', 'Incorrect Team')
        self.assertEqual(self.team.venue, 'TD Garden', 'Incorrect Venue')
        self.assertTrue(isinstance(self.league.standings, dict), 'No Standings')
        self.assertTrue(isinstance(self.league.team_records, dict), 'No Team Records')

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

    def test_player_id(self):
        player_id = nhl._player_id(self.player)
        self.assertEqual(player_id, 8470638, 'Incorrerct Player ID')

    def test_get_team_info(self):
        """Test NHL.get_team_info function"""
        info = self.league.get_team_info(team_id=6)
        self.assertTrue(isinstance(info, dict), 'No Team Info')

    def test_get_team_stats(self):
        """Test NHL.get_team_stats function"""
        stats = self.league.get_team_stats(team_id=6)
        self.assertTrue(isinstance(stats, dict), 'No Team Stats')

    def test_get_team_roster(self):
        """Test NHL.get_team_roster function"""
        roster = self.league.get_team_roster(team_id=6)
        self.assertTrue(isinstance(roster, list), 'No Roster')

    def test_get_team_schedule(self):
        """Test NHL.get_team_schedule function"""
        schedule = self.league.get_team_schedule(team_id=6)
        message = f"schedule returned {type(schedule)} not generator"
        self.assertTrue(isinstance(schedule, types.GeneratorType), message)

    def test_get_player_info(self):
        """Test NHL.get_player_info function"""
        info = self.league.get_player_info(player_name=self.player)
        self.assertTrue(isinstance(info, dict), 'No Player Info')

    def test_get_player_stats(self):
        """Test NHL.get_player_stats function"""
        stats = self.league.get_player_stats(player_name=self.player)
        self.assertTrue(isinstance(stats, dict), 'No Player Stats')

    def test_get_career_stats(self):
        """Test NHL.get_career_stats function"""
        stats = self.league.get_career_stats(player_name=self.player)
        self.assertTrue(isinstance(stats, list), 'No Career Stats')


if __name__ == '__main__':
    unittest.main()
