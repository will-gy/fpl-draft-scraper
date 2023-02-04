"""
Scrapes players from the FPL API for an individual team ID in a league.
"""
from typing import List
import requests

class TeamPlayers:
    def __init__(self, league_id: int) -> None:
        self._url = f"https://draft.premierleague.com/api/league/{league_id}/element-status"
        self.players = []

    def _get_data(self) -> None:
        response = requests.get(self._url)
        data = response.json()
        self.players = data.get("element_status")

    def get_player_ids(self) -> List:
        self._get_data()
        return [player.get("element") for player in self.players \
                if player.get("owner") is not None]
