from scrape_league.scrape_fpl_players import FantasyFootballMetadata
from app import manage_database

def main() -> None:
    api = FantasyFootballMetadata()
    player_data = api.get_player_names()
    manage_database.create_fpl_players_table('players')
    manage_database.update_fpl_players('players', player_data)

if __name__ == "__main__":
    main()