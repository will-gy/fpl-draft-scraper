import requests
from typing import Dict

class ScrapeSingleLeague:
    def __init__(self, league_id: int):
        self.league_id = league_id
        self.players_selected = self._get_selected_players()

    def _get_selected_players(self) -> Dict[str, list]:
        """
        Returns a dictionary mapping team names to lists of player names for the
        league.
        """
        league_data = requests.get(
            f'https://draft.premierleague.com/api/league/{self.league_id}/element-status'
            ).json()
        league_player_list = league_data.get('element_status')
        selected_player_id_list = [
            player.get('element') for player in league_player_list \
                if player.get('owner') is not None
                ]
        return selected_player_id_list
