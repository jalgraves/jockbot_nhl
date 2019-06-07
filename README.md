# Jockbot NHL


[![Total alerts](https://img.shields.io/lgtm/alerts/g/jalgraves/jockbot_nhl.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/jalgraves/jockbot_nhl/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/jalgraves/jockbot_nhl.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/jalgraves/jockbot_nhl/context:python) [![CircleCI](https://circleci.com/gh/jalgraves/jockbot_nhl.svg?style=svg)](https://circleci.com/gh/jalgraves/jockbot_nhl)

### Interact with NHL API
#### Features
- **Get current or historical NHL league standings**
- **Get player stats and info for NHL players both active and retired, regualr season and playoffs**
- **Get stats and info for NHL teams both current and historical**
- **Get NHL league leaders both current and historical**
- **All data returned in JSON**

### Install
#### Pypi
    pip3 install jockbot_nhl
#### From Source
    $ git clone git@github.com:jalgraves/jockbot_nhl.git
    $ cd jockbot_nhl
    $ python3 setup.py sdist bdist_wheel
    $ pip3 install .

##### ATTRIBUTES:
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
    
##### METHODS:
    get_team_info()
    get_team_stats()
    get_team_roster()
    get_team_schedule()
    get_player_info()
    get_player_stats()
    get_career_stats()
    skater_league_leaders()
    goalie_league_leaders()

### Usage
    >>> from jockbot_nhl import NHL, NHLTeam
    >>> import json
    >>> nhl = NHL()
    >>> standings = nhl.league_standings
    >>> divisions = nhl.division_standings
    >>> conferences = nhl.conference_standings
    >>> print(json.dumps(standings, indent=2))
    {
      "Tampa Bay Lightning": "1",
      "Calgary Flames": "2",
      "Boston Bruins": "3",
      "Washington Capitals": "4",
      "New York Islanders": "5",
      "San Jose Sharks": "6",
      "Toronto Maple Leafs": "7",
      "Nashville Predators": "8",
      "Pittsburgh Penguins": "9",
      "Winnipeg Jets": "10",
      "Carolina Hurricanes": "11",
      "St. Louis Blues": "12",
      "Columbus Blue Jackets": "13",
      "Montr\u00e9al Canadiens": "14",
      "Dallas Stars": "15",
      "Vegas Golden Knights": "16",
      "Colorado Avalanche": "17",
      "Arizona Coyotes": "18",
      "Florida Panthers": "19",
      "Chicago Blackhawks": "20",
      "Minnesota Wild": "21",
      "Philadelphia Flyers": "22",
      "Vancouver Canucks": "23",
      "Anaheim Ducks": "24",
      "Edmonton Oilers": "25",
      "New York Rangers": "26",
      "Buffalo Sabres": "27",
      "Detroit Red Wings": "28",
      "New Jersey Devils": "29",
      "Los Angeles Kings": "30",
      "Ottawa Senators": "31"
    }
    >>> bruins = NHLTeam('boston')
    >>> record = bruins.record
    >>> roster = bruins.roster
    >>> info = bruins.info
    >>> stats = bruins.stats
    >>> bruins
    Team: Boston Bruins | NHL API ID: 6
    >>> stats = bruins.stats
    >>> print(json.dumps(stats, indent=2))
    {
      "id": 6,
      "name": "Boston Bruins",
      "link": "/api/v1/teams/6",
      "venue": {
        "id": 5085,
        "name": "TD Garden",
        "link": "/api/v1/venues/5085",
        "city": "Boston",
        "timeZone": {
          "id": "America/New_York",
          "offset": -4,
          "tz": "EDT"
        }
      },
      "abbreviation": "BOS",
      "teamName": "Bruins",
      "locationName": "Boston",
      "firstYearOfPlay": "1924",
      "division": {
        "id": 17,
        "name": "Atlantic",
        "nameShort": "ATL",
        "link": "/api/v1/divisions/17",
        "abbreviation": "A"
      },
      "conference": {
        "id": 6,
        "name": "Eastern",
        "link": "/api/v1/conferences/6"
      },
      "franchise": {
        "franchiseId": 6,
        "teamName": "Bruins",
        "link": "/api/v1/franchises/6"
      },
      "teamStats": [
        {
          "type": {
            "displayName": "statsSingleSeason"
          },
          "splits": [
            {
              "stat": {
                "gamesPlayed": 82,
                "wins": 49,
                "losses": 24,
                "ot": 9,
                "pts": 107,
                "ptPctg": "65.2",
                "goalsPerGame": 3.134,
                "goalsAgainstPerGame": 2.585,
                "evGGARatio": 1.2266,
                "powerPlayPercentage": "25.9",
                "powerPlayGoals": 65.0,
                "powerPlayGoalsAgainst": 49.0,
                "powerPlayOpportunities": 251.0,
                "penaltyKillPercentage": "79.9",
                "shotsPerGame": 32.6829,
                "shotsAllowed": 29.4634,
                "winScoreFirst": 0.739,
                "winOppScoreFirst": 0.417,
                "winLeadFirstPer": 0.806,
                "winLeadSecondPer": 0.838,
                "winOutshootOpp": 0.563,
                "winOutshotByOpp": 0.625,
                "faceOffsTaken": 4840.0,
                "faceOffsWon": 2455.0,
                "faceOffsLost": 2385.0,
                "faceOffWinPercentage": "50.7",
                "shootingPctg": 9.6,
                "savePctg": 0.912
              },
              "team": {
                "id": 6,
                "name": "Boston Bruins",
                "link": "/api/v1/teams/6"
              }
            },
            {
              "stat": {
                "wins": "3rd",
                "losses": "2nd",
                "ot": "11th",
                "pts": "2nd",
                "ptPctg": "2nd",
                "goalsPerGame": "11th",
                "goalsAgainstPerGame": "3rd",
                "evGGARatio": "4th",
                "powerPlayPercentage": "3rd",
                "powerPlayGoals": "3rd",
                "powerPlayGoalsAgainst": "20th",
                "powerPlayOpportunities": "8th",
                "penaltyKillOpportunities": "19th",
                "penaltyKillPercentage": "16th",
                "shotsPerGame": "9th",
                "shotsAllowed": "6th",
                "winScoreFirst": "5th",
                "winOppScoreFirst": "10th",
                "winLeadFirstPer": "10th",
                "winLeadSecondPer": "18th",
                "winOutshootOpp": "11th",
                "winOutshotByOpp": "11th",
                "faceOffsTaken": "18th",
                "faceOffsWon": "12th",
                "faceOffsLost": "10th",
                "faceOffWinPercentage": "10th",
                "savePctRank": "7th",
                "shootingPctRank": "12th"
              },
              "team": {
                "id": 6,
                "name": "Boston Bruins",
                "link": "/api/v1/teams/6"
              }
            }
          ]
        }
      ],
      "shortName": "Boston",
      "officialSiteUrl": "http://www.bostonbruins.com/",
      "franchiseId": 6,
      "active": true
    }
