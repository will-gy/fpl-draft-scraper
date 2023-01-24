import aiohttp
import asyncio
from typing import List, Dict

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
        self._max_api_requests = max_api_requests
        self._valid_ids = []
    
    async def league_search_async(self, league_id:List) -> List:
        """Searches for league ids and returns list of valid ids"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for _id in league_id:
                tasks.append(asyncio.ensure_future(self._fetch(session, _id)))
            await asyncio.gather(*tasks)
    
    async def _fetch(self, session, _id):
        url = f'{self._fpl_league}{_id}/details'
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                self._check_league_size(data)

    def _check_league_size(self, resp_json:Dict) -> None:
        try:
            self._add_any_id(
                resp_json.get('league').get('id'), 
                len(resp_json.get('league_entries', []))
                )
        except:
            print("cannot add league id")

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
