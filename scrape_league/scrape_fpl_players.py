from dataclasses import dataclass

import requests


@dataclass
class PLPlayer:
    # Not used
    # TODO: Find way to use dataclass in sql insertion
    player_id: int
    name: str
    team_name: str
    position_name: str


class FantasyFootballMetadata:
    def __init__(self) -> None:
        self.url = "https://draft.premierleague.com/api/bootstrap-static"
        self.players = []
        self.teams = {}
        self.team_names = {}
        self.position_names = {}

    def _get_data(self) -> None:
        response = requests.get(self.url)
        data = response.json()
        self.players = data.get("elements")
        self.teams = data.get("teams")
        self.positions = data.get("element_types")

    def _get_teams(self) -> None:
        for team in self.teams:
            team_id = team.get("id")
            team_name = team.get("name")
            self.team_names[team_id] = team_name

    def _get_positions(self) -> None:
        for position in self.positions:
            position_id = position.get("id")
            position_name = position.get("singular_name")
            self.position_names[position_id] = position_name

    def get_player_names(self) -> list[tuple[int, str, str, str]]:
        self._get_data()
        self._get_teams()
        self._get_positions()
        player_data = []

        for player in self.players:
            player_id = player.get("id")
            name = player.get("web_name")
            team_id = player.get("team")
            position_id = player.get("element_type")
            team_name = self.team_names[team_id]
            position_name = self.position_names[position_id]
            player_data.append((player_id, name, team_name, position_name))
        return player_data
