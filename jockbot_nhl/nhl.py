import datetime
import json
import logging
import os
import requests
import socket
import sys
import time

from datetime import timedelta
from pytz import timezone
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .exceptions import NHLTeamException, NHLPlayerException, NHLRequestException


SESSION = requests.session()
DATE = datetime.datetime.now(timezone('US/Eastern'))


def get_config():
    """
    Get NHL config
    """
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config


def api_request(endpoint, verify=True):
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
        request = SESSION.get(endpoint)
    except requests.exceptions.ConnectionError:
        time.sleep(2)
        request = SESSION.get(endpoint)
    if request.status_code != 200:
        error_message = f"Error with NHL API request | status: {request.status_code}\nurl: {url}\n{request.content}"
        logging.error(error_message)
        raise NHLRequestException(error_message)
    else:
        data = request.json()
    return data


def get_team_id(team):
        """
        Get the API id for a provided team
        """
        teams = CONFIG['team_names_and_cities']
        if team.lower() not in teams.keys():
            raise NHLTeamException(f"Unrecognized team: {team}")
        team_id = teams.get(team.lower())
        if not team_id:
            raise NHLTeamException(f"Error retrieving ID for {team}")
        return team_id


def fetch_standings():
        """
        Return a list containing four dicts with stats and team info for each
        separate division in the NHL
        """
        endpoint = 'standings'
        data = api_request(endpoint)
        if data:
            standings = data['records']
            return standings


def get_todays_games():
    """
    Get NHL games being played today
    """
    date = datetime.datetime.strftime(DATE, "%Y-%m-%d")
    games = {}
    endpoint = f"schedule?date={date}"
    data = api_request(endpoint)
    if data:
        if data['totalGames'] == 0:
            return None
        games['date'] = data['dates'][0]['date']
        games_list = data['dates'][0]['games']
        games['games'] = games_list
        return games


def get_recent_games():
    """
    Get games played yesterday
    """
    date = (DATE - timedelta(1)).strftime('%Y-%m-%d')
    games = {}
    endpoint = f"schedule?date={date}"
    data = api_request(endpoint)
    if data:
        if data['totalGames'] == 0:
            return None
        games['date'] = data['dates'][0]['date']
        games_list = data['dates'][0]['games']
        games['games'] = games_list
        return games


def get_standings(records=False):
    """
    Get current NHL standings
    """
    divisions = fetch_standings()
    standings = CONFIG['standings_schema']
    for div in divisions:
        division_name = div['division']['name']
        conference_name = div['conference']['name']
        teams = div['teamRecords']
        for team in teams:
            name = team['team']['name']
            division_rank = team['divisionRank']
            conference_rank = team['conferenceRank']
            league_rank = team['leagueRank']
            record = team['leagueRecord']
            points = team['points']
            games_played = team['gamesPlayed']
            standings['conference'][conference_name][name] = conference_rank
            standings['division'][division_name][name] = division_rank
            standings['league'][name] = league_rank
            standings['records'][name] = {}
            standings['records'][name]['record'] = record
            standings['records'][name]['games_played'] = games_played
            standings['records'][name]['points'] = points
    if records:
        return standings['records']
    return standings


def parse_standings(standings, standings_type):
    """
    Parse standings return the requested standings type; division, conference, or league
    """
    standings = standings.get(standings_type)
    return standings


def parse_schedule(schedule, game_type):
    """
    Get results of completed games or the remaining unplayed games of the season
    """
    completed_games = []
    unplayed_games = []
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
    if game_type == 'completed':
        games = completed_games
    elif game_type == 'unplayed':
        games = unplayed_games
    return games


def get_game_scores(status, games=None):
    game_scores = []
    if not games:
        return
    parse_games = games['games']
    for game in parse_games:
        game_data = {'away_team': {}, 'home_team': {}}
        game_status = game['status']['abstractGameState']
        teams = game['teams']
        if game['gameType'] != 'PR' and game_status == status:
            game_data['date'] = games['date']
            game_data['away_team']['name'] = teams['away']['team']['name']
            game_data['away_team']['score'] = teams['away']['score']
            game_data['home_team']['name'] = teams['home']['team']['name']
            game_data['home_team']['score'] = teams['home']['score']
            game_scores.append(game_data)
    return game_scores


def get_current_season():
    month = DATE.month
    year = DATE.year
    if month < 10:
        season = f"{year - 1}{year}"
    else:
        season = f"{year}{year + 1}"
    return season


def get_player_ids(team):
    """
    Iterate through roster and get player names and API IDs
    """
    players = {}
    nhl = NHL()
    team = nhl.get_team_roster(team_name=team)
    for player in team:
        name = player['person']['fullName'].lower()
        players[name] = player['person']['id']
    return players


def get_all_player_ids():
    players = {}
    teams = CONFIG['full_team_names'].keys()
    for team in teams:
        ids = get_player_ids(team)
        for k, v in ids.items():
            players[k] = v
    return players


def get_player_id(player):
    player_index = os.path.join(os.path.dirname(__file__), 'players.json')
    with open(player_index, 'r') as f:
        players = json.load(f)
    player_id = players.get(player)
    if not player:
        raise NHLPlayerException(f"Player Not Found {player}")
    return player_id


CONFIG = get_config()


class NHL:
    """
    Create NHL object
    """
    def __init__(self):
        self.teams = CONFIG['full_team_names']
        self.current_season = get_current_season()
        self.standings = get_standings()
        self.league_standings = parse_standings(self.standings, 'league')
        self.conference_standings = parse_standings(self.standings, 'conference')
        self.divison_standings = parse_standings(self.standings, 'division')
        self.records = get_standings(records=True)
        self.todays_games = get_todays_games()
        self.recent_games = get_recent_games()
        self.live_scores = get_game_scores(status='Live', games=self.todays_games)
        self.recent_scores = get_game_scores(status='Final', games=self.recent_games)

    def __repr__(self):
        return f"NHL season {self.current_season}"

    def get_team_info(self, team_id=None, team_name=None):
        """
        Get general team information
        """
        if not team_id:
            team_id = get_team_id(team_name)
        endpoint = f"teams/{team_id}"
        data = api_request(endpoint)
        if data:
            team_info = data['teams'][0]
            return team_info

    def get_team_stats(self, team_id=None, team_name=None, season=None):
        """
        Get team stats. Return team stats object
        """
        if not team_id:
            team_id = get_team_id(team_name)
        endpoint = f"teams/{team_id}?expand=team.stats"
        data = api_request(endpoint)
        return data['teams'][0]

    def get_team_roster(self, team_id=None, team_name=None):
        """
        Get team roster. Return list of player objects
        """
        if not team_id:
            team_id = get_team_id(team_name)
        endpoint = f"teams/{team_id}/roster"
        data = api_request(endpoint)
        player_list = data['roster']
        return player_list

    def get_team_schedule(self, team_id=None, team_name=None, season=None):
        """
        Get team schedule. Return list of game objects
        """
        if not team_id:
            team_id = get_team_id(team_name)
        if not season:
            season = self.current_season
        endpoint = f"schedule?teamId={team_id}&season={season}"
        data = api_request(endpoint)
        game_list = data['dates']
        return game_list

    def get_player_info(self, player_id=None, player_name=None):
        """
        Get individual stats for a player
        """
        if not player_id:
            player_id = get_player_id(player_name)
        endpoint = f"people/{player_id}"
        data = api_request(endpoint)
        if data:
            info = data['people'][0]
            return info

    def get_player_stats(self, player_id=None, player_name=None, season=None):
        """
        Get individual stats for a player
        """
        if not player_id:
            player_id = self.get_player_id(player_name)
        player_info = self.get_player_info(player_id)
        team = player_info['currentTeam']['id']
        if not season:
            season = get_current_season()
        season_endpoint = f"stats?stats=statsSingleSeason&season={season}"
        endpoint = f"people/{player_id}/{season_endpoint}"
        data = api_request(endpoint)
        if data:
            stats = data['stats'][0]['splits'][0]
            stats['team'] = team
            return stats

    def get_career_stats(self, player_id=None, player_name=None):
        """
        Get career stats for a player
        """
        if not player_id:
            player_id = get_player_id(player_name)
        stats_endpoint = "stats?stats=yearByYear"
        endpoint = f"people/{player_id}/{stats_endpoint}"
        data = api_request(endpoint)
        if data:
            seasons = data['stats'][0]['splits']
            return seasons


class NHLTeam(NHL):
    """
    Create NHL team object
    """
    def __init__(self, team=None):
        super().__init__()
        self.team = team
        self.id = get_team_id(self.team)
        self.info = self.get_team_info(team_id=self.id)
        self.name = self.info['name']
        self.venue = self.info['venue']['name']
        self.stats = self.get_team_stats(self.id)
        self.roster = self.get_team_roster(self.id)
        self.schedule = self.get_team_schedule(self.id)
        self.game_results = parse_schedule(self.schedule, 'completed')
        self.remaining_games = parse_schedule(self.schedule, 'unplayed')
        self.record = self.records.get(self.name)
        self.wins = self.record['record']['wins']
        self.losses = self.record['record']['losses']
        self.otl = self.record['record']['ot']
        self.games_played = self.record['games_played']
        self.points = self.record['points']
        self.division_rank = None
        self.conference_rank = None
        self.overall_rank = None
        self.year_by_year_records = None


class NHLPlayer(NHL):
    """
    Create an NHL player object
    """
    def __init__(self, player=None, player_id=None):
        super().__init__()
        self.player = player
        if not player_id:
            self.player_id = get_player_id(self.player)
        self.info = self.get_player_info(player_id=self.player_id)
        self.season_stats = self.get_player_stats(player_id=self.player_id)
        self.career_stats = self.get_career_stats(player_id=self.player_id)


def main():
    """
    Main function
    """
    if len(sys.argv) > 1:
        team = sys.argv[1]
        team = NHLTeam(team)
        print(json.dumps(team.info, indent=2))
    else:
        nhl = NHL()
        print(repr(nhl))


if __name__ == '__main__':
    main()
