from typing import List, Tuple
import requests

class SingleGWTransfers:
    @property
    def league_id(self) -> int:
        return self.league_id

    @classmethod
    def get_league_transfers(cls, league_id: int, gameweek: int) -> Tuple[List, List]:
        """Retrieves the waivers and free transfers for a given league and game week.
        
        Args:
            league_id: The ID of the league.
            gameweek: The game week number.
        
        Returns:
            A dictionary containing the waivers and free transfers for the given league 
            and game week.
        """
        url = "https://draft.premierleague.com/api/draft/league/{}/transactions".format(league_id)
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Error retrieving waivers and free transfers for league {} and \
                game week {}: {}".format(league_id, gameweek, response.text))

        players_in = []
        players_out = []

        for event in response.json().get('transactions'):
            if event.get('result') == 'a':
                if event.get('event') == gameweek:
                    # TODO: Distinguish between free transfers and waivers
                    players_in.append(event.get('element_in'))
                    players_out.append(event.get('element_out'))

        return players_in, players_out
