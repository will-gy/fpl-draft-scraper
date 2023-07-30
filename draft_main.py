import asyncio
from datetime import datetime
from time import sleep
import pandas as pd

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
            choices = resp_json.get('choices', [])
            picks = {pick.get('index'): pick.get('element') for pick in choices}
            await self._add_picks(league_id, picks)
        except:
            print(f"Cannot add picks {league_id}")

    async def _add_picks(self, league_id: int, league_picks: dict[int, int]) -> None:
        self._draft_picks[league_id] = league_picks

    @property
    def get_draft_picks(self) -> dict[int, dict[int, int]]:
        return self._draft_picks

    @property
    def get_valid_league_ids(self) -> list[int]:
        return self._valid_league_ids

    @get_valid_league_ids.setter
    def get_valid_league_ids(self, league_ids: list[int]) -> None:
        self._valid_league_ids = league_ids


class ManageDraftScrapeSequential:
    def __init__(
            self, manage_db: ManageDatabase, draft_rank: DraftRank, league_ids: list[int],
            max_api_req: int=250
            ) -> None:
        self._manage_database: ManageDatabase = manage_db
        self._draft_rank: DraftRank = draft_rank
        self._player_ids: list[int] = self.get_player_ids()
        self._player_picks: dict = self._get_player_dict()
        self._player_df: pd.DataFrame = self._get_player_df()
        self._league_ids: list[int] = league_ids
        self._max_api_requests: int = max_api_req

    @staticmethod
    def get_player_ids() -> list[int]:
        return manage_database.select_all_player_ids('players')

    def _get_player_dict(self) -> dict[int, list[int]]:
        return {player_id: [] for player_id in self._player_ids}

    async def populate_player_draft_dict(self, league_id: dict[int, dict[int, int]]) -> None:
        for picks in league_id.values():
            for idx, player_id in picks.items():
                self._player_picks[player_id].append(idx)

    def _get_request_chunks(self) -> list[list[int]]:
        return [
            self._league_ids[i * self._max_api_requests:(i + 1) * self._max_api_requests] for i in \
                range(
                    (len(self._league_ids) + self._max_api_requests - 1) // self._max_api_requests
                    )
                ]

    async def manage_draft_picks(self) -> None:
        # Break up request_n into chunks <= max_api_requests
        request_chunk = self._get_request_chunks()

        for idx, chunk in enumerate(request_chunk):
            print(f"new chunk {idx + 1}")
            time_now = datetime.now()
            # Reset valid league ids
            self._draft_rank.get_valid_league_ids = []
            # Scrape league IDS
            await self._draft_rank.check_valid_league_ids(chunk)
            valid_ids = self._draft_rank.get_valid_league_ids

            if not valid_ids:
                print("No valid ids found")
                sleep(5)
                continue
            else:
                await self._draft_rank.get_draft_choice(valid_ids)
                await self.populate_player_draft_dict(self._draft_rank.get_draft_picks)
                print(f"Time taken: {datetime.now()-time_now}")
                sleep(10)

    def _get_player_df(self) -> pd.DataFrame:
        player_tuple = manage_database.select_player_details('players', list(self._player_ids))
        return pd.DataFrame(player_tuple, columns=['id', 'Name', 'Club', 'Position', 'Drank Rank'])

    def get_pick_df(self) -> pd.DataFrame:
        pick_avg = self._get_mean(
            self._player_picks, 'Average Pick'
            )
        out = pd.merge(
            self._player_df, pick_avg, right_index=True, left_on='id'
            ).sort_values('Average Pick')
        # TODO: Calculate true average by position, rather than ranking on average
        out['Rank By Position'] = out.groupby('Position')['Average Pick'].rank(ascending=True)
        return out

    @staticmethod
    def _get_mean(input_dict: dict[int, list[int]], name: str) -> pd.Series:
        # TODO: Make this more efficient, currently very slow due to number of columns
        df = pd.DataFrame.from_dict(input_dict, orient='index')
        draft_total = len(df.columns)
        df['Count'] = df.count(axis=1)
        # Remove players who were drafted in less than 1/4 of drafts
        df = df[df['Count'] > draft_total // 4]
        average_pick = df.mean(axis=1)
        average_pick.name = name
        return average_pick


if __name__ == '__main__':
    draft_pick = DraftRank()
    # db_league_ids = manage_database.get_league_ids('league', 10)
    db_league_ids = manage_database.get_league_ids_all('league')

    manage_data = ManageDraftScrapeSequential(manage_database, draft_pick, db_league_ids)

    loop = asyncio.get_event_loop()
    # Scrape draft picks
    loop.run_until_complete(manage_data.manage_draft_picks())
    # Calculate pick averages
    pick_df = manage_data.get_pick_df()

    pick_df.to_csv(f'Pick Average All.csv', index=False, encoding='utf-8-sig')
