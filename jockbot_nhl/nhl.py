from jockbot_nhl._helpers import (
    CONFIG,
    JockBotNHLException,
    _api_request,
    _current_season,
    _fetch_standings,
    _filter_stats_check,
    _game_scores,
    _parse_leaders,
    _parse_leaders_teams,
    _parse_schedule,
    _player_id,
    _recent_games,
    _standings,
    _team_id,
    _todays_games,
    _wild_card_standings
)


class NHL:
    """Create NHL object
    ATTRIBUTES:
    current_season
    standings
    league_standings
    conference_standings
    division_standings
    team_records
    todays_games
    recent_games
    live_scores
    recent_scores

    METHODS:
    get_team_info()
    get_team_stats()
    get_team_roster()
    get_team_schedule()
    get_player_info()
    get_player_stats()
    get_career_stats()
    """
    teams = CONFIG['full_team_names']
    current_season = _current_season()
    standings = _standings()
    league_standings = _fetch_standings(standings, 'league')
    conference_standings = _fetch_standings(standings, 'conference')
    divison_standings = _fetch_standings(standings, 'division')
    wildcard_standings = {
        'Eastern': _wild_card_standings('eastern'),
        'Western': _wild_card_standings('western')
    }
    team_records = _standings(records=True)
    todays_games = _todays_games()
    recent_games = _recent_games()
    live_scores = _game_scores(status='Live', games=todays_games, linescore=True)
    recent_scores = _game_scores(status='Final', games=recent_games)

    def __repr__(self):
        return f"NHL season {self.current_season}"

    def get_team_info(self, team_id=None, team_name=None):
        """Get general team information"""
        if not team_id:
            team_id = _team_id(team_name)
        endpoint = f"teams/{team_id}"
        data = _api_request(endpoint)
        if data:
            team_info = data['teams'][0]
            return team_info

    def get_team_stats(self, team_id=None, team_name=None, season=None):
        """Get team stats. Return team stats object"""
        if not team_id:
            team_id = _team_id(team_name)
        endpoint = f"teams/{team_id}?expand=team.stats"
        data = _api_request(endpoint)
        return data['teams'][0]

    def get_team_roster(self, team_id=None, team_name=None, season=None):
        """Get team roster. Return list of player objects"""
        team_id = _team_id(team_name) if not team_id else team_id
        season = self.current_season if not season else season
        endpoint = f"teams/{team_id}/roster?season={season}"
        data = _api_request(endpoint)
        player_list = data['roster']
        return player_list

    def get_team_schedule(self, team_name=None, team_id=None, season=None):
        """Get team schedule. Return list of game objects"""
        team_id = _team_id(team_name) if not team_id else team_id
        season = self.current_season if not season else season
        endpoint = f"schedule?teamId={team_id}&season={season}"
        data = _api_request(endpoint)
        game_list = data['dates']
        yield from game_list

    def get_player_info(self, player_id=None, player_name=None):
        """Get individual stats for a player"""
        if not player_id:
            player_id = _player_id(player_name)
        endpoint = f"people/{player_id}"
        data = _api_request(endpoint)
        if data:
            info = data['people'][0]
            return info

    def get_player_stats(self, player_id=None, player_name=None, season=None):
        """Get individual stats for a player"""
        if not player_id:
            player_id = _player_id(player_name)
        player_info = self.get_player_info(player_id)
        player_active = player_info.get('active')
        team = player_info.get('currentTeam')
        if team:
            team = team['id']
        if not season and not player_active:
            raise JockBotNHLException('Season required for inactive players')
        if not season:
            season = _current_season()
        season_endpoint = f"stats?stats=statsSingleSeason&season={season}"
        endpoint = f"people/{player_id}/{season_endpoint}"
        data = _api_request(endpoint)
        if data:
            stats = data['stats'][0]['splits'][0]
            stats['team'] = team
            return stats

    def get_career_stats(self, player_id=None, player_name=None):
        """Get career stats for a player"""
        if not player_id:
            player_id = _player_id(player_name)
        stats_endpoint = "stats?stats=yearByYear"
        endpoint = f"people/{player_id}/{stats_endpoint}"
        data = _api_request(endpoint)
        if data:
            seasons = data['stats'][0]['splits']
            return seasons

    def goalie_league_leaders(self, stat, **kwargs):
        """Get league leaders for an individual goaltending stat
        OPTIONAL KEYWORD ARGS:
        season: stat leaders for a given season. ex. season='19881989'
                (default is current season)

        season_type: 2 for regular 3 for post season. ex. season_type='3'
                     (default is regular season)

        num_players: number of leaders to return. ex. num_players=5
                     (default is 10)

        time_filter: minimum number of seconds of ice time a player must
                     have to qualify as a leader. ex. time_filter=25200
        """
        if not _filter_stats_check():
            leaders = _parse_leaders(stat, 'goalie', **kwargs)
        else:
            kwargs['time_filter'] = 25200
            leaders = _parse_leaders(stat, 'goalie', **kwargs)
        return leaders

    def skater_league_leaders(self, stat, **kwargs):
        """Get league leaders for an individual skaters stat
        OPTIONAL KEYWORD ARGS:
        season: stat leaders for a given season. ex. season='19881989'
                (default is current season)

        season_type: 2 for regular 3 for post season. ex. season_type='3'
                     (default is regular season)

        num_players: number of leaders to return. ex. num_players=5
                     (default is 10)
        """
        leaders = _parse_leaders(stat, 'skater', **kwargs)
        return leaders

    def team_league_leaders(self, stat, **kwargs):
        """Get league leaders for an individual team stat
        OPTIONAL KEYWORD ARGS:
        season: team stat leaders for a given season. ex. season='19881989'
                (default is current season)

        season_type: 2 for regular 3 for post season. ex. season_type='3'
                     (default is regular season)
        """
        leaders = _parse_leaders_teams(stat, **kwargs)
        return leaders


class NHLTeam(NHL):
    """Create NHL team object"""
    def __init__(self, team=None):
        super().__init__()
        self.team = team
        self.id = _team_id(self.team)
        self.info = self.get_team_info(team_id=self.id)
        self.name = self.info['name']
        self.venue = self.info['venue']['name']
        self.stats = self.get_team_stats(self.id)
        self.roster = self.get_team_roster(self.id)
        self.schedule = _parse_schedule(self.get_team_schedule(team_id=self.id))
        self.remaining_games = self.schedule.unplayed
        self.record = self.team_records.get(self.name)
        self.wins = self.record['record']['wins']
        self.losses = self.record['record']['losses']
        self.otl = self.record['record']['ot']
        self.games_played = self.record['games_played']
        self.points = self.record['points']
        self.division_rank = None
        self.conference_rank = None
        self.overall_rank = None
        self.year_by_year_records = None

    def __repr__(self):
        return f"Team: {self.name} | NHL API ID: {self.id}"


class NHLPlayer(NHL):
    """
    Create an NHL player object
    """
    def __init__(self, player, player_id=None):
        super().__init__()
        self._id = player_id
        self.player = player
        self.info = self.get_player_info(player_id=self.player_id)
        self.season_stats = self.get_player_stats(player_id=self.player_id)
        self.career_stats = self.get_career_stats(player_id=self.player_id)

    @property
    def player_id(self):
        if not self._id:
            self._player_id = _player_id(self.player)
        else:
            self._player_id = self._id
        return self._player_id

    def __repr__(self):
        return f"Player: {self.player} | NHL API ID: {self.player_id}"


def main():
    """Main function"""
    from _helpers import _pprint
    nhl = NHL()
    goals_against_avg_leaders = nhl.goalie_league_leaders('savePctg', season_type='3')
    _pprint(goals_against_avg_leaders)


if __name__ == '__main__':
    main()
