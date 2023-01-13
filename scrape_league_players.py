from scrape_league.scrape_league_players import ScrapeSingleLeague
from app import manage_database

def get_league_player_data(league_id: int) -> None:
    league_data = ScrapeSingleLeague(league_id)
    player_data = manage_database.select_player_details('players', league_data.players_selected)
    return player_data

if __name__ == "__main__":
    print(get_league_player_data(38838))