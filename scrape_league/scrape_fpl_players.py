from typing import List
import requests

class FantasyFootballMetadata:
    def __init__(self) -> None:
        self.url = "https://draft.premierleague.com/api/bootstrap-static"
        self.players = []
        self.teams = {}
        self.team_names = {}

    def _get_data(self) -> None:
        response = requests.get(self.url)
        data = response.json()
        self.players = data.get("elements")
        self.teams = data.get("teams")
    
    def _get_teams(self) -> None:
        for team in self.teams:
            team_id = team.get("id")
            team_name = team.get("name")
            self.team_names[team_id] = team_name
    
    def get_player_names(self) -> List:
        self._get_data()
        self._get_teams()
        player_data = []
        for player in self.players:
            player_id = player.get("id")
            name = player.get("web_name")
            team_id = player.get("team")
            team_name = self.team_names[team_id]
            player_data.append((player_id, name, team_name))
        return player_data
