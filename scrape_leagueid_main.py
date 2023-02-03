"""
Main script to scrape league ids

Manages the scraping of league ids and updating the database
"""
import asyncio
import random
from datetime import datetime
from time import sleep
from typing import List

from app import manage_database
from database.update_database import ManageDatabase
from scrape_league.scrape_league_id import ScrapeLeagueID
from utils.fpl_constants import TOTAL_LEAGUES


class ManageLeagueIDScrape:
    def __init__(self, mange_database: ManageDatabase, scrape_league_id: ScrapeLeagueID) -> None:
        """Injecting ManageDatabase and ScrapeLeagueID instances

        Args:
            mange_database (ManageDatabase): _description_
            scrape_league_id (ScrapeLeagueID): _description_
        """
        self._manage_database = mange_database
        self._scrape_league_id = scrape_league_id

    def db_setup(self, table_name: str) -> None:
        try:
            self._manage_database.create_db()
        except Exception as e:
            print(e)
        try:
            self._manage_database.create_league_table(table_name)
        except Exception as e:
            print(e)

    async def manage_update_league_id(self, request_n: int, table_name: str) -> None:
        # Break up request_n into chunks <= max_api_requests
        request_chunk = self._get_request_chunks(request_n)
        for idx, chunk in enumerate(request_chunk):
            print(f"new chunk {idx}")
            # Get list of leauge IDS in db
            time_now = datetime.now()
            id_search_list = self._random_league_id_sample(chunk)
            # Scrape league IDS
            await self._scrape_league_id.league_search_async(id_search_list)
            # Get valid ids just scraped
            id_list = self._scrape_league_id.valid_ids
            # Update league_id table
            self._manage_database.update_id(table_name, id_list)
            # Once added clear valid_id list
            self._scrape_league_id.clear_valid_ids()
            print(f"Time taken: {datetime.now()-time_now}")
            sleep(5)

    def _get_request_chunks(self, request_total: int) -> List:
        """Splits total request into chunks of size scrape_league_id.max_api_requests

        Args:
            request_total (int): Total request number

        Returns:
            List: List of chunk sizes
        """
        max_api = self._scrape_league_id.max_api_requests
        if request_total <= max_api: return [request_total]

        chunk_list = [max_api for _ in range(request_total // max_api)]

        if request_total % max_api !=0:
            chunk_list.append(request_total%max_api)
        return chunk_list

    def _random_league_id_sample(self, league_sample_n: int) -> List:
        # existing_ids = self._manage_database.select_id(table_name)
        return random.sample(range(1, TOTAL_LEAGUES), league_sample_n)


if __name__ == '__main__':
    scrape_league = ScrapeLeagueID()

    manage_data = ManageLeagueIDScrape(manage_database, scrape_league)
    # Create fpldraft db and league table if not existing
    manage_data.db_setup('league')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(manage_data.manage_update_league_id(25000, 'league'))
