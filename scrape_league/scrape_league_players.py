import requests
from typing import Dict, List

class ScrapeSingleLeague:
    @property
    def league_id(self) -> int:
        return self.league_id

    @classmethod
    def get_selected_players(cls) -> List:
        """
        Returns a dictionary mapping team names to lists of player names for the
        league.
        """
        league_data = requests.get(
            f'https://draft.premierleague.com/api/league/{cls.league_id}/element-status'
            ).json()
        league_player_list = league_data.get('element_status')
        selected_player_id_list = [
            player.get('element') for player in league_player_list \
                if player.get('owner') is not None
                ]
        return selected_player_id_list

    
    # TODO: Add methods to get league name, size, rank, total, gw points, gw rank, gw total, 
    # gw transfers
