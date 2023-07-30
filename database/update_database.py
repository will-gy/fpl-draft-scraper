import sqlite3
from sqlite3.dbapi2 import Connection, Cursor


class ManageDatabase:
    def __init__(self, db_name: str) -> None:
        self._db_name = db_name

    def create_db(self) -> None:
        sqlite3.connect(f"{self._db_name}.db")

    def _connect_db(self) -> tuple[Connection, Cursor]:
        connection_obj = sqlite3.connect(f"{self._db_name}.db")
        cursor = connection_obj.cursor()
        return connection_obj, cursor

    def create_league_table(self, table_name: str) -> None:
        _, cursor = self._connect_db()
        table = (
            f"CREATE TABLE {table_name}"
            f"(TIMESTAMP DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            f"LEAGUEID INT NOT NULL,"
            f"LEAGUESIZE INT,"
            f"UNIQUE(LEAGUEID))"
            )
        cursor.execute(table)

    def update_id(self, table_name: str, data: list) -> None:
        conn, cursor = self._connect_db()
        with conn:
            cursor.executemany(
                f'INSERT or IGNORE into {table_name} (LEAGUEID, LEAGUESIZE) values (?,?)', data
                )

    def select_id(self, table_name: str) -> list[int]:
        conn, cursor = self._connect_db()
        with conn:
            cursor.execute(
                f'SELECT LEAGUEID from {table_name}'
            )
        return cursor.fetchall()

    def create_fpl_players_table(self, table_name: str) -> None:
        _, cursor = self._connect_db()
        table = (
            f"""CREATE TABLE IF NOT EXISTS {table_name}
            (TIMESTAMP DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            player_id INTEGER PRIMARY KEY,
            name TEXT, 
            team_name TEXT,
            position TEXT,
            draft_rank INTEGER
            )"""
            )
        cursor.execute(table)

    def update_fpl_players(self, table_name: str, data: list) -> None:
        # TODO: Update Team name dynamically to prevent stale data
        conn, cursor = self._connect_db()
        with conn:
            cursor.executemany(
                f'INSERT or IGNORE into {table_name} (player_id, name, team_name, position, draft_rank) \
                    values (?,?,?,?,?)', data
                )

    def select_player_details(
            self, table_name: str, player_ids: list[int]
            ) -> list[tuple[int, str, str, str]]:
        conn, cursor = self._connect_db()
        with conn:
            # Query the table
            cursor.execute('''
            SELECT player_id, name, team_name, position FROM {} WHERE player_id IN ({})
            '''.format(table_name, ','.join(['?'] * len(player_ids))), player_ids)

        results = cursor.fetchall()
        return results

    def select_all_player_ids(self, table_name: str) -> list[int]:
        conn, cursor = self._connect_db()
        with conn:
            cursor.execute(
                f'SELECT player_id from {table_name}'
            )
        return [item[0] for item in cursor.fetchall()]

    def get_league_ids(self, table_name: str, league_size: int) -> list[int]:
        conn, cursor = self._connect_db()
        with conn:
            cursor.execute(
                f'SELECT LEAGUEID from {table_name} WHERE LEAGUESIZE = {league_size}'
            )

        return [item[0] for item in cursor.fetchall()]

    def get_max_league_id(self, table_name: str) -> int:
        conn, cursor = self._connect_db()
        with conn:
            cursor.execute(
                f'SELECT MAX(LEAGUEID) from {table_name}'
            )

        res = cursor.fetchone()[0]
        return res if res else 0
