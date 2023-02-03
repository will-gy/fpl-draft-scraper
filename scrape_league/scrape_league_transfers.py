from typing import Dict, List, Tuple

from aiohttp import ClientSession, TCPConnector


class SingleGWTransfers:
    @classmethod
    async def get_league_transfers(cls, league_id: int, gameweek: int) -> Tuple[List, List]:
        """Retrieves the waivers and free transfers for a given league and game week.
        TODO: Distinguish between free transfers and waivers.
        TODO: Update to take a list of leagues

        Args:
            league_id: The ID of the league.
            gameweek: The game week number.

        Returns:
            A dictionary containing the waivers and free transfers for the given league
            and game week.
        """
        url = "https://draft.premierleague.com/api/draft/league/{}/transactions".format(league_id)

        connector = TCPConnector(limit=60)
        async with ClientSession(connector=connector) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return await cls._parse_league_transfers(data, gameweek)
                else:
                    raise Exception("Error retrieving waivers and free transfers for league {} and \
                        game week {}: {}".format(league_id, gameweek, resp.text))

    @classmethod
    async def _parse_league_transfers(cls, resp_json: Dict, gameweek: int) -> Tuple[List, List]:
        players_in = []
        players_out = []

        for event in resp_json.get('transactions', []):
            if event.get('event') == gameweek:
                if event.get('result') == 'a' and event.get('kind') == 'w':
                    # TODO: Record free transfers as well as waivers
                    players_in.append(event.get('element_in'))
                    players_out.append(event.get('element_out'))

        return players_in, players_out
