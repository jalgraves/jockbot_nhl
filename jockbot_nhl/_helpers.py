import datetime
import json
import logging
import os
import requests
import socket
import time

from collections import OrderedDict, namedtuple
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


def _api_request(endpoint, base_url=None, verify=True):
    """
    GET request to NHL API
    """
    if not base_url:
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


def _wild_card_standings(conference):
    """Get current wild card standings"""
    endpoint = "standings/wildCard"
    if conference == 'eastern':
        data = _api_request(endpoint)['records'][0]
    elif conference == 'western':
        data = _api_request(endpoint)['records'][1]
    else:
        error_message = f"Invalid Conference: {conference}"
        raise JockBotNHLException(error_message)
    wildcard = OrderedDict()
    standings = {'conference': data['conference']['name']}
    teams = data['teamRecords']
    for team in teams:
        team_name = team['team']['name']
        wildcard_rank = team['wildCardRank']
        wildcard[team_name] = [wildcard_rank]
    standings['standings'] = wildcard
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


def _fetch_league_leaders(stat, player_type, season=None, season_type='2', num_players=10, reverse=True, time_filter=0):
    """Fetch stat leaders
    VALID SKATER STATS:
    points, assists, goals, penaltyMinutes, faceoffWinPctg, gameWinningGoals, gamesPlayed
    otGoals (overtime goals), plusMinus, pointsPerGame, ppGoals (power play goals)
    ppPoints (power play points), shGoals (short handed goals) shPoints (short handed points)
    shiftsPerGame, shots, shootingPctg, timeOnIcePerGame

    VALID GOALIE STATS:
    assists, gamesPlayed, gamesStarted, goals, goalsAgainst, goalsAgainstAverage,
    losses, otLosses, penaltyMinutes, points, savePctg, saves, shotsAgainst,
    shutouts, ties, timeOnIce, wins

    PARAMS
    :stat: stat to retrieve leaders for
    :season: str ex. '20182019'  (defaults to current season)
    :player_type: skater or goalie
    :season_type: 2 for regular season (default) 3 for playoffs
    :num_players: int of amount of players to return (default is 10)
    """
    if player_type != 'skater' and player_type != 'goalie':
        raise JockBotNHLException(f"Invalid player_type: {player_type}")
    base_url = f"http://www.nhl.com/stats/rest/{player_type}s"
    season = _current_season() if not season else season
    query = [
        f"?reportType=season&reportName={player_type}summary",
        f"cayenneExp=seasonId={season}%20and%20gameTypeId={season_type}%20and%20timeOnIce%3E{time_filter}&sort={stat}"
    ]
    endpoint = "&".join(query)
    leaders = _api_request(endpoint, base_url=base_url, verify=False)['data']
    if reverse:
        leaders.reverse()
    return leaders[:num_players]


def _parse_leaders(stat, player_type, **kwargs):
    """Parse stats for league leaders"""
    leaders = OrderedDict()
    leaders_list = _fetch_league_leaders(stat, player_type, **kwargs)
    for leader in leaders_list:
        player_data = {}
        name = leader['playerName']
        player_data['team'] = leader['playerTeamsPlayedFor']
        player_data['value'] = leader[stat]
        leaders[name] = player_data
    return leaders


def _current_season():
    """Return the current NHL season"""
    endpoint = "seasons/current"
    data = _api_request(endpoint)
    if data:
        season = data['seasons'][0]['seasonId']
        return season
    else:
        raise JockBotNHLException('Unable to retrieve current NHL season')


def _current_season_start_date():
    """Return the current NHL season"""
    endpoint = "seasons/current"
    data = _api_request(endpoint)
    if data:
        season = data['seasons'][0]['regularSeasonStartDate']
        return season
    else:
        raise JockBotNHLException('Unable to retrieve current NHL start date')


def _filter_stats_check():
    """Check if the regular season is over 30 days old
    if True stats should be filtered based players time on ice
    """
    season_start = datetime.datetime.strptime(_current_season_start_date(), '%Y-%m-%d')
    filter_date = (season_start + datetime.timedelta(30))
    date = datetime.datetime.now()
    if date > filter_date:
        return True


def _get_team_roster(team_id=None, team_name=None):
    """Get team roster. Return list of player objects"""
    if not team_id:
        team_id = _team_id(team_name)
    endpoint = f"teams/{team_id}/roster"
    data = _api_request(endpoint)
    player_list = data['roster']
    return player_list


def _player_ids_by_team(team):
    """Build dict containing player name and their NHL API player ID
    Iterate through roster and get player names and API IDs
    """
    players = {}
    team = _get_team_roster(team_name=team)
    for player in team:
        name = player['person']['fullName'].lower()
        players[name] = player['person']['id']
    return players


def _all_active_player_ids():
    """Return a dict containing all active players in the NHL with their
    names and NHL API player ID
    """
    players = {}
    teams = CONFIG['full_team_names'].keys()
    for team in teams:
        ids = _player_ids_by_team(team)
        for k, v in ids.items():
            players[k] = v
    return players


def _all_player_ids():
    """Return a dict containing all players in the NHL with their
    names and NHL API player ID
    """
    player_ids = {}
    base_url = 'https://records.nhl.com/site/api/'
    endpoint = 'player'
    players = _api_request(endpoint, base_url=base_url)['data']
    for player in players:
        if player['yearsPro']:
            name = player['prName'].lower()
            player_id = player['id']
            player_ids[name] = player_id
    return player_ids


def _player_id(player):
    """Lookup and return the NHL API player ID for an idividual player"""
    players = _all_player_ids()
    player_id = players.get(player)
    if not player:
        raise JockBotNHLException(f"Player Not Found {player}")
    return player_id


def _pprint(obj):
    if isinstance(obj, dict):
        print(json.dumps(obj, indent=2))
    elif isinstance(obj, list):
        for i in obj:
            if isinstance(i, dict):
                print(json.dumps(i, indent=2))
    else:
        print(obj)
