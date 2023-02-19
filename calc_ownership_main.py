import asyncio
from typing import Dict, List, Optional, Tuple

import pandas as pd

from app import manage_database
from scrape_league.scrape_league_players import ScrapeSingleLeague
from scrape_league.scrape_league_transfers import SingleGWTransfers
from scrape_league.scrape_team import TeamPlayers


class LeagueStats:
    def __init__(self, league_ids: List) -> None:
        # Currently gameweek is only used for transfers, not total ownership. Total ownership
        # is based on the most recent gameweek. TODO: Add ownership for previous gameweeks.
        self._league_ids = league_ids
        self._failed_ids: List = []

        self._player_ids = self.get_player_ids()
        self._player_df = self._get_player_df()

        self._player_ownership: Dict = self._get_player_dict()
        self._player_waivers_in: Dict = self._get_player_dict()
        self._player_waivers_out: Dict = self._get_player_dict()

    @staticmethod
    def get_player_ids() -> List:
        return manage_database.select_all_player_ids('players')

    def _get_player_dict(self) -> Dict[int, List]:
        return {player_id: [] for player_id in self._player_ids}

    async def populate_player_ownership_dict(self) -> None:
        for idx, league_id in enumerate(self._league_ids):
            print(f'Processing league ownership {idx+1}/{len(self._league_ids)}')
            selected_players: Optional[List[int]] = await self._get_player_ownership(league_id)
            if selected_players:
                for player_id in selected_players:
                    self._player_ownership[player_id].append(league_id)

    async def populate_player_transfers_dict(self, gameweek: int) -> None:
        for idx, league_id in enumerate(self._league_ids):
            print(f'Processing league transfers {idx+1}/{len(self._league_ids)}')
            transfers_in, transfers_out = await self._get_player_transfers(league_id, gameweek)
            if not transfers_in and not transfers_out:
                self._failed_ids.append(league_id)
                continue

            for player_in, player_out in zip(transfers_in, transfers_out):
                self._player_waivers_in[player_in].append(league_id)
                self._player_waivers_out[player_out].append(league_id)

    async def _get_player_ownership(self, league_id: int) -> Optional[List[int]]:
        return await ScrapeSingleLeague.get_selected_players(league_id)

    async def _get_player_transfers(self, league_id: int, gameweek: int) -> Tuple[List, List]:
        return await SingleGWTransfers.get_league_transfers(league_id, gameweek)

    def _get_player_df(self) -> pd.DataFrame:
        player_tuple = manage_database.select_player_details('players', list(self._player_ids))
        return pd.DataFrame(player_tuple, columns=['id', 'Name', 'Club'])

    def _get_percentage(self, input_dict: Dict, name: str) -> pd.Series:
        df = pd.DataFrame.from_dict(input_dict, orient='index')
        df_count = df.count(axis=1)/(len(self._league_ids)-len(self._failed_ids))
        df_count.name = name
        return df_count

    def get_total_ownership_df(self) -> pd.DataFrame:
        ownership_count = self._get_percentage(
            self._player_ownership, 'ownership'
            )
        out = pd.merge(
            self._player_df, ownership_count, right_index=True, left_on='id'
            )
        return out

    def get_transfers_df(self) -> pd.DataFrame:
        transfers_in_count = self._get_percentage(
            self._player_waivers_in, 'waivers_in'
            )
        transfers_out_count = self._get_percentage(
            self._player_waivers_out, 'waivers_out'
            )
        transfers_df = pd.merge(
            transfers_in_count, transfers_out_count, left_index=True, right_index=True
            )
        out = pd.merge(
            transfers_df,
            self._player_df, left_index=True, right_on='id'
            )
        return out

    @property
    def player_ownership(self) -> Dict:
        return self._player_ownership

if __name__ == "__main__":
    GAMEWEEK = 24
    db_league_ids = manage_database.get_league_ids('league', 10)

    loop = asyncio.get_event_loop()

    league_stats = LeagueStats(db_league_ids)
    loop.run_until_complete(league_stats.populate_player_ownership_dict())
    ownership_df_league = league_stats.get_total_ownership_df()

    loop.run_until_complete(league_stats.populate_player_transfers_dict(gameweek=GAMEWEEK))
    transfers_df_league = league_stats.get_transfers_df()
    total_df = pd.merge(
        ownership_df_league, transfers_df_league, on=['id', 'Name', 'Club']
        ).sort_values('waivers_in', ascending=False)

    team_players = TeamPlayers(league_id=38838)
    total_df['Available in league'] = ~total_df['id'].isin(team_players.get_player_ids())

    total_df.to_csv(f'transfers_GW{GAMEWEEK}.csv', index=False, encoding='utf-8-sig')
