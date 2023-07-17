# DEPRECATE THIS FILE

from typing import List

from scrape_league.scrape_league_players import ScrapeSingleLeague
from app import manage_database

def get_league_player_data(league_id: int) -> List:
    ScrapeSingleLeague.league_id = league_id
    player_data = manage_database.select_player_details(
        'players', ScrapeSingleLeague.get_selected_players()
        )
    return player_data
