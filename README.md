# Jockbot NHL

[![Total alerts](https://img.shields.io/lgtm/alerts/g/jalgraves/jockbot_nhl.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/jalgraves/jockbot_nhl/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/jalgraves/jockbot_nhl.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/jalgraves/jockbot_nhl/context:python) [![CircleCI](https://circleci.com/gh/jalgraves/jockbot_nhl.svg?style=svg)](https://circleci.com/gh/jalgraves/jockbot_nhl)

## Interact with NHL API

### Features

- **Get current or historical NHL league standings**
- **Get player stats and info for NHL players both active and retired, regualr season and playoffs**
- **Get stats and info for NHL teams both current and historical**
- **Get NHL league leaders player stats both current and historical**
- **Get NHL team stats league leaders both current and historical**
- **All data returned in JSON**

---

### Install

#### Pypi

    pip3 install jockbot_nhl

#### From Source

    git clone git@github.com:jalgraves/jockbot_nhl.git
    cd jockbot_nhl
    python3 setup.py sdist bdist_wheel
    pip3 install .

---

### Usage

#### _Output ommited for brevity, see docs/OUTPUT.md for examples with output_

    >>> from jockbot_nhl import NHL, NHLTeam
    >>> nhl = NHL()

##### Current Standings

    >>> standings = nhl.league_standings
    >>> divisions = nhl.division_standings
    >>> conferences = nhl.conference_standings
    >>> wildcard = nhl.wildcard_standings

##### NHL Games Today

    >>> todays_games = nhl.todays_games

##### NHL Games Yesterday

    >>> yesterdays_games = nhl.recent_games

##### NHL Live Scores

    >>> live_scores = nhl.live_scores

##### Get Team Schdule

    >>> current_season_schedule = nhl.get_team_schedule(team_name='boston')
    >>> other_season_schedule = nhl.get_team_schedule(team_name='boston', season='20172018')

##### Get Team Info

    >>> team_info = nhl.get_team_info(team_name='boston')

##### Get Team Stats

    >>> team_stats = nhl.get_team_stats(team_name='boston')
    >>> historical_stats = nhl.get_team_stats(team_name='boston', season='19881989')

##### Get Team Roster

    >>> team_roster = nhl.get_team_roster(team_name='boston')
    >>> historical_roster = nhl.get_team_roster(team_name='boston', season='20102011)

##### Get Player Info

    >>> player_info = nhl.get_player_info(player_name='patrice bergeron')
    >>> inactive_player_info = nhl.get_player_info(player_name='wayne gretzky')

##### Get Player Season Stats

    >>> current_season_stats = nhl.get_player_stats(player_name='patrice bergeron')
    >>> past_season_stats = nhl.get_player_stats(player_name='wayne gretzky', season='19881989')

##### Get Player Career Stats

    >>> career_stats = nhl.get_career_stats(player_name='wayne gretzky')

##### Get Goalies League Leaders

##### Goalie Stats

assists, gamesPlayed, gamesStarted, goals, goalsAgainst, goalsAgainstAverage, losses, otLosses, penaltyMinutes, points, savePctg, saves, seasonId, shotsAgainst, shutouts, ties, timeOnIce, wins

    >>> current_season_leaders = nhl.goalie_league_leaders('goalsAgainstAverage')
    >>> past_season_leaders = nhl.goalie_league_leaders('goalsAgainstAverage', season='20102011')

##### Get Skater League Leaders

##### Skater Stats

points, assists, goals, penaltyMinutes, faceoffWinPctg, gameWinningGoals, gamesPlayed,
otGoals (overtime goals), plusMinus, pointsPerGame, ppGoals (power play goals), ppPoints (power play points), shGoals (short handed goals) shPoints (short handed points),shiftsPerGame, shots, shootingPctg, timeOnIcePerGame

    >>> current_season_leaders = nhl.skater_league_leaders('points')
    >>> playoff_points_leader = nhl.skater_league_leaders('points', season_type='3')
    >>> past_season_leaders = nhl.skater_league_leaders('points', season='20102011')

##### Team Stat League Leaders

    >>> league_leaders_team_points = nhl.team_league_leaders('points')
    >>> league_leaders_team_goals_against = nhl.team_league_leaders('goalsAgainst', reverse=True)
    >>> playoff_leaders_team_goals = nhl.team_league_leaders('goalsFor', season_type='3')
