# URLs

## Team IDs

    {'new jersey devils': 1,
     'new york islanders': 2,
     'new york rangers': 3,
     'philadelphia flyers': 4,
     'pittsburgh penguins': 5,
     'boston bruins': 6,
     'buffalo sabres': 7,
     'montreal canadiens': 8,
     'ottawa senators': 9,
     'toronto maple leafs': 10,
     'carolina hurricanes': 12,
     'florida panthers': 13,
     'tampa bay lightning': 14,
     'washington capitals': 15,
     'chicago blackhawks': 16,
     'detroit red wings': 17,
     'nashville predators': 18,
     'st. louis blues': 19,
     'calgary flames': 20,
     'colorado avalanche': 21,
     'edmonton oilers': 22,
     'vancouver canucks': 23,
     'anaheim ducks': 24,
     'dallas stars': 25,
     'los angeles kings': 26,
     'san jose sharks': 28,
     'columbus blue jackets': 29,
     'minnesota wild': 30,
     'winnipeg jets': 52,
     'arizona coyotes': 53,
     'vegas golden knights': 54}

---

## Endpoints

    https://statsapi.web.nhl.com/api/v1/teams/<TEAM_ID>
    https://statsapi.web.nhl.com/api/v1/teams/<TEAM_ID>?expand=team.stats
    https://statsapi.web.nhl.com/api/v1/seasons/current
    https://statsapi.web.nhl.com/api/v1/standings
    https://statsapi.web.nhl.com/api/v1/standings/wildCard
    https://statsapi.web.nhl.com/api/v1/schedule?date=<YYYY-MM-DD>
    https://statsapi.web.nhl.com/api/v1/game/<GAME_ID>/linescore
    https://statsapi.web.nhl.com/api/v1/teams/<TEAM_ID>/roster?season=<SEASON>
    https://statsapi.web.nhl.com/api/v1/schedule?teamId=<TEAM_ID>&season=<SEASON>
    https://records.nhl.com/site/api/player
    https://statsapi.web.nhl.com/api/v1/people/<PLAYER_ID>/stats?stats=yearByYear
    http://www.nhl.com/stats/rest/skaters?reportType=season&reportName=skatersummary&cayenneExp=seasonId=<SEASON>%20and%20gameTypeId=2%20and%20timeOnIce%3E0&sort=<STAT>
    https://api.nhle.com/stats/rest/team?isAggregate=false&reportType=basic&isGame=falsereportName=teamsummary&sort=%7B%22property%22%3A+%22<STAT>%22%2C+%22direction%22%3A+%22DESC%22%7D&cayenneExp=leagueId%3D133+and+gameTypeId%3D2+and+seasonId%3E%3D<SEASON>+and+seasonId%3C%3D<SEASON>
    http://www.nhl.com/stats/rest/goalies?reportType=season&reportName=goaliesummary&cayenneExp=seasonId%3D<SEASON>+and+gameTypeId%3D2+and+timeOnIce%3E25200&sort=<STAT>
