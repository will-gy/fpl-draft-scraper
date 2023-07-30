import asyncio
from datetime import datetime
from time import sleep

from aiohttp import ClientSession, TCPConnector

from app import manage_database
from database.update_database import ManageDatabase


class DraftRank:
    def __init__(self) -> None:
        # TODO: Potentially look at using a generator here if memory becomes an issue
        self._draft_picks = {}
        self._valid_league_ids = []

    def __get_details_url(self, league_id: int) -> str:
        return f"https://draft.premierleague.com/api/league/{league_id}/details"

    def __get_choices_url(self, league_id: int) -> str:
        return f"https://draft.premierleague.com/api/draft/{league_id}/choices"

    async def check_valid_league_ids(self, league_ids: list[int]) -> None:
        """Searches for league ids and returns list of valid ids where the draft has taken place"""
        # Set socket limit to 60 as windows only allows max 64 in aysnc loop
        connector = TCPConnector(limit=60)

        async with ClientSession(connector=connector) as session:
            tasks = []
            for _id in league_ids:
                tasks.append(asyncio.ensure_future(self._check_league_draft(session, _id)))
            await asyncio.gather(*tasks)

    async def _check_league_draft(self, session: ClientSession, id: int) -> None:
        url = self.__get_details_url(id)
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                await self._check_draft(id, data)

    async def _check_draft(self, league_id: int, resp_json: dict) -> None:
        try:
            draft_status = resp_json.get('league', {}).get('draft_status', '')
            if draft_status == 'post':
                self._valid_league_ids.append(league_id)
        except:
            print(f"Cannot add league {league_id}")

    async def get_draft_choice(self, league_ids: list[int]) -> None:
        """Searches for league ids and returns list of valid ids"""
        # Set socket limit to 60 as windows only allows max 64 in aysnc loop 
        connector = TCPConnector(limit=60)

        async with ClientSession(connector=connector) as session:
            tasks = []
            for _id in league_ids:
                tasks.append(asyncio.ensure_future(self._get_draft_data(session, _id)))
            await asyncio.gather(*tasks)

    async def _get_draft_data(self, session: ClientSession, id: int) -> None:
        url = self.__get_choices_url(id)
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                await self._get_league_choices(id, data)

    async def _get_league_choices(self, league_id: int, resp_json: dict) -> None:
        try:
            print(f"Checking league {league_id}")
            choices = resp_json.get('choices', [])
            print(choices)
            picks = [(pick.get('index'), pick.get('element')) for pick in choices]
            await self._add_picks(league_id, picks)
        except:
            print(f"Cannot add picks {league_id}")

    async def _add_picks(self, league_id: int, league_picks: list[tuple[int, int]]) -> None:
        self._draft_picks[league_id] = league_picks

    @property
    def get_draft_picks(self) -> dict[int, list[tuple[int, int]]]:
        return self._draft_picks

    @property
    def get_valid_league_ids(self) -> list[int]:
        return self._valid_league_ids


class ManageDraftScrapeSequential:
    @staticmethod
    def _get_sequential_league_id(start_id: int, chunk_size: int, chunk_idx: int) -> list[int]:
        return list(range(start_id, start_id + (chunk_size * (chunk_idx + 1)) - 1))

    def __init__(self, manage_database: ManageDatabase, draft_rank: DraftRank) -> None:
        self._manage_database = manage_database
        self._draft_rank = draft_rank
        self._max_api_requests = 250

    def _get_request_chunks(self, league_ids: list[int]) -> list[list[int]]:
        return [
            league_ids[i * self._max_api_requests:(i + 1) * self._max_api_requests] for i in \
                range((len(league_ids) + self._max_api_requests - 1) // self._max_api_requests)
                ]

    async def manage_draft_picks(self, table_name: str) -> dict[int, list[tuple[int, int]]]:
        # Break up request_n into chunks <= max_api_requests
        league_ids = self._manage_database.get_league_ids(table_name, 10)
        request_chunk = self._get_request_chunks(league_ids)

        draft_dict = {}

        for chunk in request_chunk:
            print(f"new chunk")
            time_now = datetime.now()
            # Scrape league IDS
            await self._draft_rank.check_valid_league_ids(chunk)
            valid_ids = self._draft_rank.get_valid_league_ids
            if not valid_ids:
                print("No valid ids found")
                sleep(5)
                continue
            else:
                await self._draft_rank.get_draft_choice(valid_ids)
                draft_dict.update(self._draft_rank.get_draft_picks)
                print(f"Time taken: {datetime.now()-time_now}")
                sleep(10)
        return draft_dict

if __name__ == '__main__':
    draft_pick = DraftRank()

    manage_data = ManageDraftScrapeSequential(manage_database, draft_pick)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(manage_data.manage_draft_picks('league'))
