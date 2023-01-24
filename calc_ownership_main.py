from typing import List, Dict, Tuple
import pandas as pd

from scrape_league.scrape_league_players import ScrapeSingleLeague
from scrape_league.scrape_league_transfers import SingleGWTransfers
from app import manage_database

class LeagueStats:
    def __init__(self, league_ids: List) -> None:
        # Currently gameweek is only used for transfers, not total ownership. Total ownership
        # is based on the most recent gameweek. TODO: Add ownership for previous gameweeks.
        self._league_ids = league_ids

        self._player_ids = self.get_player_ids()
        self._player_df = self._get_player_df()

        self._player_ownership: Dict = self._get_player_dict()
        self._player_transfers_in: Dict = self._get_player_dict()
        self._player_transfers_out: Dict = self._get_player_dict()

    @staticmethod
    def get_player_ids() -> List:
        return manage_database.select_all_player_ids('players')

    def _get_player_dict(self) -> Dict[int, List]:
        return {player_id: [] for player_id in self._player_ids}

    def populate_player_ownership_dict(self) -> None:
        for league_id in self._league_ids:
            selected_players: List = self._get_player_ownership(league_id)
            for player_id in selected_players:
                self._player_ownership[player_id].append(league_id)
    
    def populate_player_transfers_dict(self, gameweek: int) -> None:
        for league_id in self._league_ids:
            transfers_in, transfers_out = self._get_player_transfers(league_id, gameweek)
            for player_in, player_out in zip(transfers_in, transfers_out):
                self._player_transfers_in[player_in].append(league_id)
                self._player_transfers_out[player_out].append(league_id)
        
    def _get_player_ownership(self, league_id: int) -> List:
        ScrapeSingleLeague.league_id = league_id
        return ScrapeSingleLeague.get_selected_players()
    
    def _get_player_transfers(self, league_id: int, gameweek: int) -> Tuple[List, List]:
        SingleGWTransfers.league_id = league_id
        return SingleGWTransfers.get_league_transfers(league_id, gameweek)

    def _get_player_df(self) -> pd.DataFrame:
        player_tuple = manage_database.select_player_details('players', list(self._player_ids))
        return pd.DataFrame(player_tuple, columns=['id', 'Name', 'Club'])
    
    @staticmethod
    def _get_percentage(input_dict: Dict, league_ids: List, name: str) -> pd.Series:
        df = pd.DataFrame.from_dict(input_dict, orient='index')
        df_count = df.count(axis=1)/len(league_ids)
        df_count.name = name
        return df_count

    def total_ownership_df(self) -> pd.DataFrame:
        ownership_count = self._get_percentage(
            self._player_ownership, self._league_ids, 'ownership'
            )
        out = pd.merge(         
            self._player_df, ownership_count, right_index=True, left_on='id'
            )
        return out.sort_values('ownership', ascending=False)
    
    def transfers_df(self) -> pd.DataFrame:
        transfers_in_count = self._get_percentage(
            self._player_transfers_in, self._league_ids, 'transfers_in'
            )
        transfers_out_count = self._get_percentage(
            self._player_transfers_out, self._league_ids, 'transfers_out'
            )
        transfers_df = pd.merge(
            transfers_in_count, transfers_out_count, left_index=True, right_index=True
            )
        out = pd.merge(
            transfers_df,
            self._player_df, left_index=True, right_on='id'
            )
        return out.sort_values('transfers_in', ascending=False)
    
    @property
    def player_ownership(self) -> Dict:
        return self._player_ownership

if __name__ == "__main__":
    league_ids = manage_database.get_league_ids('league', 10)

    league_stats = LeagueStats(league_ids)
    league_stats.populate_player_ownership_dict()
    ownership_df = league_stats.total_ownership_df()
    ownership_df.to_csv('ownership.csv', index=False)

    league_stats.populate_player_transfers_dict(gameweek=21)
    transfers_df = league_stats.transfers_df()
    transfers_df.to_csv('transfers.csv', index=False)