"""
ScrapeLeagueID class. Scrapes chunks of league ids and ids as well as league size
"""
import asyncio
from typing import Dict, List

from aiohttp import ClientSession, TCPConnector


class ScrapeLeagueID:
    def __init__(self, max_api_requests:int=250) -> None:
        """Init method

        Args:
            max_api_requests (int, optional): _description_. Defaults to 250.
        """
        self._fpl_league = 'https://draft.premierleague.com/api/league/'
        self._max_api_requests = max_api_requests
        self._valid_ids = []
    
    async def league_search_async(self, league_id:List) -> None:
        """Searches for league ids and returns list of valid ids"""
        # Set socket limit to 60 as windows only allows max 64 in aysnc loop 
        connector = TCPConnector(limit=60)

        async with ClientSession(connector=connector) as session:
            tasks = []
            for _id in league_id:
                tasks.append(asyncio.ensure_future(self._fetch(session, _id)))
            await asyncio.gather(*tasks)
    
    async def _fetch(self, session: ClientSession, _id) -> None:
        url = f'{self._fpl_league}{_id}/details'
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                await self._check_league_size(data)

    async def _check_league_size(self, resp_json: Dict) -> None:
        try:
            await self._add_id(
                resp_json.get('league').get('id'), 
                len(resp_json.get('league_entries', []))
                )
        except:
            print("cannot add league id")

    async def _add_id(self, id: int, league_size: int) -> None:
        # Adds id of any size, unlike add_valid_id
        self._valid_ids.append((id, league_size))

    def clear_valid_ids(self) -> None:
        self._valid_ids = []

    @property
    def valid_ids(self) -> List:
        return self._valid_ids
    
    @property
    def max_api_requests(self) -> int:
        return self._max_api_requests

    @max_api_requests.setter
    def max_api_requests(self, new_max: int) -> None:
        if new_max > 0 and isinstance(new_max, int):
            self._max_api_requests = new_max
        else:
            print("Enter valid max api requests value")
