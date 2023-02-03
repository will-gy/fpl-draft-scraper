from typing import Dict, List, Optional
from aiohttp import ClientSession, TCPConnector

class ScrapeSingleLeague:
    @classmethod
    async def get_selected_players(cls, league_id: int) -> Optional[List[int]]:
        """
        Returns a dictionary mapping team names to lists of player names for the
        league.

        TODO: Update to take a list of leagues
        """
        url = f'https://draft.premierleague.com/api/league/{league_id}/element-status'
        connector = TCPConnector(limit=60)
        async with ClientSession(connector=connector) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return await cls._parse_players(data)

    @classmethod
    async def _parse_players(cls, data: Dict) -> List:
        league_player_list = data.get('element_status', [])
        selected_player_id_list = [
            player.get('element') for player in league_player_list \
                if player.get('owner') is not None
                ]
        return selected_player_id_list

    # TODO: Add methods to get league name, size, rank, total, gw points, gw rank, gw total, 
    # gw transfers
