import grequests
import random
from typing import List, Dict
from utils.fpl_constants import TOTAL_LEAGUES

class ScrapeLeagueID:
    def __init__(self, league_team_size:int, max_api_requests:int=250) -> None:
        """Init method

        Args:
            league_team_size (int): Total number of teams in league to search for in sample e.g. 
            10 team league
            league_sample_n (int): Total number of leagues to scrape
            max_api_requests (int, optional): _description_. Defaults to 250.
        """        
        self._league_team_size = league_team_size
        self._fpl_league = 'https://draft.premierleague.com/api/league/'
        # self._league_sample_n = league_sample_n
        self._max_api_requests = max_api_requests
        self._valid_ids = []
    
    def league_search_async(self, league_id:List) -> List:
        # Check sample number not over max api requests
        # sample_size = min(league_sample_n, self._max_api_requests)
        # league_id = self._random_league_id_sample(sample_size)

        urls = [f'{self._fpl_league}{_id}/details' for _id in league_id]
        rs = (grequests.get(u) for u in urls)
        for resp in grequests.imap(rs):
            if resp.status_code == 200:
                self._check_league_size(resp.json())
                
    def _check_league_size(self, resp_json:Dict) -> None:
        try:
            self._add_any_id(
                resp_json.get('league').get('id'), 
                len(resp_json.get('league_entries', []))
                )
        except:
            print("cannot add league id")

    # @staticmethod
    # def _random_league_id_sample(league_sample_n:int) -> List:
    #     return random.sample(range(1, TOTAL_LEAGUES), league_sample_n)

    def add_valid_id(self, id:int) -> None:
        # Appends tuple of valid id and leauge size to _valid_id list
        # Depreciated
        self._valid_ids.append((id, self._league_team_size))

    def _add_any_id(self, id:int, league_size:int) -> None:
        # Adds id of any size, unlike add_valid_id
        self._valid_ids.append((id, league_size))

    def clear_valid_ids(self) -> None:
        self._valid_ids = []

    @property
    def valid_ids(self) -> List:
        return self._valid_ids
    
    @property
    def max_api_requests(self):
        return self._max_api_requests
    
    @max_api_requests.setter
    def max_api_requests(self, new_max:int):
        if new_max > 0 and isinstance(new_max, int):
            self._max_api_requests = new_max
        else:
            print("Enter valid max api requests value")


# scrape_id = ScrapeLeagueID(10)
# scrape_id.league_search_async(250)
# print(scrape_id.get_valid_ids())