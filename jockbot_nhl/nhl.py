import datetime
import json
import logging
import os
import requests
import socket
import sys
import time

from collections import namedtuple, OrderedDict
from pytz import timezone
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class JockBotNHLException(Exception):
    """Base class for jockbot_nhl exceptions"""
    pass


def _get_config():
    """Get configuration"""
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config


SESSION = requests.session()
DATE = datetime.datetime.now(timezone('US/Eastern'))
CONFIG = _get_config()


def _api_request(endpoint, verify=True):
    """
    GET request to NHL API
    """
    base_url = 'https://statsapi.web.nhl.com/api/v1/'
    url = f"{base_url}{endpoint}"
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[x for x in range(500, 506)])
    SESSION.mount('http://', HTTPAdapter(max_retries=retries))
    try:
        request = SESSION.get(url, verify=verify)
    except socket.gaierror:
        time.sleep(1)
        request = SESSION.get(url)
    except requests.exceptions.ConnectionError:
        time.sleep(2)
        request = SESSION.get(url)
    if request.status_code != 200:
        error_message = f"Error with NHL API request | status: {request.status_code}\nurl: {url}\n{request.content}"
        logging.error(error_message)
        raise JockBotNHLException(error_message)
    else:
        data = request.json()
    return data


def _team_id(team):
    """Get the NHL API ID for a provided team"""
    teams = CONFIG['team_names_and_cities']
    if team.lower() not in teams.keys():
        raise JockBotNHLException(f"Unrecognized team: {team}")
    team_id = teams.get(team.lower())
    if not team_id:
        raise JockBotNHLException(f"Error retrieving ID for {team}")
    return team_id


def _divisions():
    """Generator that yields dicts with stats and team info for each
    separate division in the NHL
    """
    endpoint = 'standings'
    data = _api_request(endpoint)
    if data:
        divisions = data['records']
        yield from divisions


def _games_on_date(date):
    """Get NHL games being played on a given date"""
    games = {}
    endpoint = f"schedule?date={date}"
    data = _api_request(endpoint)
    if data:
        if data['totalGames'] == 0:
            return
        games['date'] = data['dates'][0]['date']
        games_list = data['dates'][0]['games']
        games['games'] = games_list
        return games


def _todays_games():
    """Get NHL games being played today"""
    date = datetime.datetime.strftime(DATE, "%Y-%m-%d")
    games = _games_on_date(date)
    return games


def _recent_games():
    """Get games played yesterday"""
    date = (DATE - datetime.timedelta(1)).strftime('%Y-%m-%d')
    games = _games_on_date(date)
    return games


def _standings(records=False):
    """Get current NHL standings"""
    standings = CONFIG['standings_schema']
    for div in _divisions():
        division_name = div['division']['name']
        conference_name = div['conference']['name']
        teams = div['teamRecords']
        for team in teams:
            name = team['team']['name']
            standings['conference'][conference_name][name] = team['conferenceRank']
            standings['division'][division_name][name] = team['divisionRank']
            standings['league'][name] = team['leagueRank']
            standings['records'][name] = {}
            standings['records'][name]['record'] = team['leagueRecord']
            standings['records'][name]['games_played'] = team['gamesPlayed']
            standings['records'][name]['points'] = team['points']
    if records:
        return standings['records']
    return standings


def _fetch_standings(standings, standings_type):
    """Return the requested standings type; division, conference, or league"""
    standings = standings.get(standings_type)
    if standings_type == 'league':
        standings = OrderedDict(sorted(standings.items(), key=lambda t: int(t[1])))
    return standings


def _parse_schedule(schedule):
    """Parse results of completed games or the remaining unplayed games of the season"""
    completed_games = []
    unplayed_games = []
    Games = namedtuple('Games', ['played', 'unplayed'])
    for game in schedule:
        game_data = {'away_team': {}, 'home_team': {}}
        game_info = game['games'][0]
        status = game_info['status']['abstractGameState']
        teams = game_info['teams']
        if game_info['gameType'] != 'PR' and status == 'Final':
            game_data['date'] = game['date']
            game_data['away_team']['name'] = teams['away']['team']['name']
            game_data['away_team']['score'] = teams['away']['score']
            game_data['home_team']['name'] = teams['home']['team']['name']
            game_data['home_team']['score'] = teams['home']['score']
            completed_games.append(game_data)
        elif game_info['gameType'] != 'PR' and status == 'Preview':
            game_data['date'] = game['date']
            game_data['away_team']['name'] = teams['away']['team']['name']
            game_data['home_team']['name'] = teams['home']['team']['name']
            unplayed_games.append(game_data)
    games = Games(played=completed_games, unplayed=unplayed_games)
    return games

def _get_linescore(game_id):
    endpoint = f"game/{game_id}/linescore"
    data = _api_request(endpoint)
    return data

def _game_scores(status, games=None, linescore=False):
    """Parse game scores"""
    game_scores = []
    if not games:
        return
    parse_games = games['games']
    for game in parse_games:
        game_data = {'away_team': {}, 'home_team': {}}
        game_status = game['status']['abstractGameState']
        game_data['status'] = game_status
        teams = game['teams']
        if linescore:
            game_id = game['gamePk']
            game_data['linescore'] = _get_linescore(game_id)
            current_period = game_data['linescore'].get('currentPeriodOrdinal')
            time_left = game_data['linescore'].get('currentPeriodTimeRemaining')
            game_data['period'] = current_period
            game_data['time_left'] = time_left
        if game['gameType'] != 'PR' and game_status == status:
            game_data['date'] = games['date']
            game_data['away_team']['name'] = teams['away']['team']['name']
            game_data['away_team']['score'] = teams['away']['score']
            game_data['home_team']['name'] = teams['home']['team']['name']
            game_data['home_team']['score'] = teams['home']['score']
            game_scores.append(game_data)
    return game_scores


def _current_season():
    """Return the current NHL season"""
    month = DATE.month
    year = DATE.year
    if month < 10:
        season = f"{year - 1}{year}"
    else:
        season = f"{year}{year + 1}"
    return season


def _player_ids_by_team(team):
    """Form dict containing player name and their NHL API player ID
    Iterate through roster and get player names and API IDs
    """
    players = {}
    nhl = NHL()
    team = nhl.get_team_roster(team_name=team)
    for player in team:
        name = player['person']['fullName'].lower()
        players[name] = player['person']['id']
    return players


def _all_player_ids():
    """Return a dict containing all players in the NHL with their
    names and NHL API player ID
    """
    players = {}
    teams = CONFIG['full_team_names'].keys()
    for team in teams:
        ids = _player_ids_by_team(team)
        for k, v in ids.items():
            players[k] = v
    return players


def _player_id(player):
    """Lookup and return the NHL API player ID for an idividual player"""
    player_index = os.path.join(os.path.dirname(__file__), 'players.json')
    with open(player_index, 'r') as f:
        players = json.load(f)
    player_id = players.get(player)
    if not player:
        raise JockBotNHLException(f"Player Not Found {player}")
    return player_id


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

    def get_team_roster(self, team_id=None, team_name=None):
        """Get team roster. Return list of player objects"""
        if not team_id:
            team_id = _team_id(team_name)
        endpoint = f"teams/{team_id}/roster"
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
        team = player_info['currentTeam']['id']
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


def pprint(obj):
    if isinstance(obj, dict):
        print(json.dumps(obj, indent=2))
    elif isinstance(obj, list):
        for i in obj:
            if isinstance(i, dict):
                print(json.dumps(i, indent=2))
    else:
        print(obj)


def main():
    """Main function"""
    # profiler = Profile()

    if len(sys.argv) > 1:
        team = sys.argv[1]
        team = NHLTeam(team)
        # profiler.runcall(NHLTeam, 'boston')
        # profiler.print_stats()
        pprint(team.name)
    else:
        nhl = NHL()
        pprint(nhl.recent_scores)


if __name__ == '__main__':
    main()
