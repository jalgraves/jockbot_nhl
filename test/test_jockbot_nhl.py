import unittest
import types

from jockbot_nhl import nhl
from jockbot_nhl import _helpers


class TestNHL(unittest.TestCase):
    """Test nhl.py"""
    def setUp(self):
        self.team_city = 'boston'
        self.conference = 'eastern'
        self.league = nhl.NHL()
        self.team = nhl.NHLTeam(self.team_city)
        self.player = 'patrice bergeron'
        self.inactive_player = 'wayne gretzky'
        self.inactive_player_id = 8447400
        self.team_id = 6
        self.player_id = 8470638
        self.config = _helpers._get_config()
        self.stat_keys = self.config['stat_keys']
        self.goalie_stat = 'goalsAgainstAverage'
        self.skater_stat = 'points'
        self.past_season = '20102011'

    def test_nhl(self):
        self.assertEqual(len(self.league.current_season), 8, 'Incorrect Seasson')
        self.assertEqual(self.team.name, 'Boston Bruins', 'Incorrect Team')
        self.assertEqual(self.team.venue, 'TD Garden', 'Incorrect Venue')
        self.assertTrue(isinstance(self.league.standings, dict), 'No Standings')
        self.assertTrue(isinstance(self.league.team_records, dict), 'No Team Records')
        self.assertTrue(isinstance(self.league.wildcard_standings, dict), 'No Wildcard Standings')

    def test_team_id(self):
        team_id = _helpers._team_id(self.team_city)
        self.assertEqual(team_id, 6, 'Incorrect Team ID')

    def test_divisions(self):
        """Test _divisions function"""
        divisions = _helpers._divisions()
        message = f"divisions returned {type(divisions)} not generator"
        self.assertTrue(isinstance(divisions, types.GeneratorType), message)

    def test_games_on_date(self):
        """Test _games_on_date function"""
        games = _helpers._games_on_date('2019-05-27')
        message = f"Games: {games}"
        self.assertTrue(isinstance(games, dict), message)

    def test_player_id(self):
        player_id = _helpers._player_id(self.player)
        inactive_player_id = _helpers._player_id(self.inactive_player)
        self.assertEqual(player_id, self.player_id, 'Incorrect Player ID')
        self.assertEqual(inactive_player_id, self.inactive_player_id, 'Incorrect Inactive Player ID')

    def test_wild_card_standings(self):
        """Test nhl._wild_card_standings"""
        wildcard = nhl._wild_card_standings(self.conference)
        self.assertEqual(wildcard['conference'], 'Eastern', 'Incorrect Conference')
        self.assertTrue(isinstance(wildcard['standings'], dict), 'Incorrect Standings Type')

    def test_fetch_league_leaders_skaters(self):
        """Test nhl._league_leaders function for skater stats"""
        stat_keys = self.stat_keys['skaters']
        leaders = _helpers._fetch_league_leaders('points', 'skater')
        self.assertTrue(isinstance(leaders, list), 'Incorrect skater Type')
        self.assertEqual(len(leaders), 10, f"Incorrect number of players: {len(leaders)}")
        message = f"Skater Stat Keys Do Not Match\n{leaders[0].keys()}"
        self.assertEqual(list(leaders[0].keys()), stat_keys, message)

    def test_fetch_league_leaders_goalies(self):
        """Test nhl._league_leaders function for goalie stats"""
        stat_keys = self.stat_keys['goalies']
        leaders = _helpers._fetch_league_leaders('saves', 'goalie')
        message = f"Skater Stat Keys Do Not Match\n{leaders[0].keys()}"
        self.assertTrue(isinstance(leaders, list), 'Incorrect goalie Type')
        self.assertEqual(len(leaders), 10, f"Incorrect number of players: {len(leaders)}")
        message = f"Skater Stat Keys Do Not Match\n{leaders[0].keys()}"
        self.assertEqual(list(leaders[0].keys()), stat_keys, message)

    def test_parse_leaders(self):
        """Test nhl._parse_leaders function"""
        leaders = nhl._parse_leaders('points', 'skater')
        print(leaders)
        self.assertTrue(isinstance(leaders, dict), 'Incorrect leaders Type')

    def test_all_player_ids(self):
        players = _helpers._all_player_ids()
        self.assertTrue(isinstance(players, dict), 'Incorrect players Type')
        self.assertEqual(players[self.player], self.player_id, 'Incorrect Player ID')

    def test_get_team_info(self):
        """Test NHL.get_team_info function"""
        info = self.league.get_team_info(team_id=self.team_id)
        self.assertTrue(isinstance(info, dict), 'No Team Info')

    def test_get_team_stats(self):
        """Test NHL.get_team_stats function"""
        stats = self.league.get_team_stats(team_id=self.team_id)
        self.assertTrue(isinstance(stats, dict), 'No Team Stats')

    def test_get_team_roster(self):
        """Test NHL.get_team_roster function"""
        roster = self.league.get_team_roster(team_id=self.team_id)
        historical_roster = self.league.get_team_roster(team_id=self.team_id, season=self.past_season)
        self.assertTrue(isinstance(roster, list), 'No Roster')
        self.assertTrue(isinstance(historical_roster, list), 'No historical roster')

    def test_get_team_schedule(self):
        """Test NHL.get_team_schedule function"""
        schedule = self.league.get_team_schedule(team_id=self.team_id)
        message = f"schedule returned {type(schedule)} not generator"
        self.assertTrue(isinstance(schedule, types.GeneratorType), message)

    def test_get_player_info(self):
        """Test NHL.get_player_info function"""
        info = self.league.get_player_info(player_name=self.player)
        self.assertTrue(isinstance(info, dict), 'No Player Info')

    def test_get_player_stats(self):
        """Test NHL.get_player_stats function"""
        player_stats = self.league.get_player_stats(player_name=self.player)
        inactive_player_stats = self.league.get_player_stats(player_name=self.inactive_player, season='19871988')
        self.assertTrue(isinstance(player_stats, dict), 'No Player Stats')
        self.assertTrue(isinstance(inactive_player_stats, dict), 'No Inactive Player Stats')

    def test_get_career_stats(self):
        """Test NHL.get_career_stats function"""
        stats = self.league.get_career_stats(player_name=self.player)
        self.assertTrue(isinstance(stats, list), 'No Career Stats')

    def test_goalie_league_leaders(self):
        """Test NHL.goalie_league_leaders function"""
        leaders = self.league.goalie_league_leaders(self.goalie_stat)
        self.assertEqual(len(leaders), 10, f"Incorrect number of players: {len(leaders)}")

    def test_skater_league_leaders(self):
        """Test NHL.skater_league_leaders function"""
        leaders = self.league.skater_league_leaders(self.skater_stat)
        self.assertEqual(len(leaders), 10, f"Incorrect number of players: {len(leaders)}")

    def test_filter_stats_check(self):
        """Test nhl._filter_stats_check function"""
        self.assertTrue(nhl._filter_stats_check(), 'Filter should be True')

    def test_player_ids_by_team(self):
        """test _helpers._player_ids_by_team function"""
        team_ids = _helpers._player_ids_by_team(self.team_city)
        self.assertTrue(isinstance(team_ids, dict), 'No team player IDs')


if __name__ == '__main__':
    unittest.main()
