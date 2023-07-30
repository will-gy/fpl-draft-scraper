from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from aiohttp import ClientSession, TCPConnector


class ScrapeSingleLeague:
    # TODO: These methods should be static
    @classmethod
    async def get_selected_players(cls, league_id: int) -> Optional[List[int]]:
        """
        Returns a dictionary mapping team names to lists of player names for the
        league.

        TODO: Update to take a list of leagues
        """
        url = f'https://draft.premierleague.com/api/league/{league_id}/element-status'
        connector = TCPConnector(limit=60)
        async with ClientSession(connector=connector) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return await cls._parse_players(data)

    @classmethod
    async def _parse_players(cls, data: Dict) -> List:
        league_player_list = data.get('element_status', [])
        selected_player_id_list = [
            player.get('element') for player in league_player_list \
                if player.get('owner') is not None
                ]
        return selected_player_id_list

    @classmethod
    def get_league_results(cls, league_id: int) -> Tuple[Dict[str, Dict[str, str]],
    Dict[str, Dict[str, Tuple[int, str]]]]:
        """
        Returns a dictionary mapping game weeks and manager IDs for h2h leagues.
        """
        url = f'https://draft.premierleague.com/api/league/{league_id}/details'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('league', {}).get('scoring') == 'h':
                return cls._parse_h2h_results(data.get('league_entries'), data.get('matches', []))
            else:
                # TOOD: implement for regular leagues
                return {}, {}

    @classmethod
    def _parse_h2h_results(cls, teams: List, matches: List) -> Tuple[Dict[str, Dict[str, str]],
    Dict[str, Dict[str, Tuple[int, str]]]]:
        results = {}
        team_info = {}
        for team in teams:
            team_info[team.get('id')] = {
                'team_name': team.get('entry_name'),
                'player_name': team.get('player_first_name')
                }

        for match in matches:
            if match.get('finished'):
                gameweek = match.get('event')
                entry_1_points = match.get('league_entry_1_points')
                entry_2_points = match.get('league_entry_2_points')

                result_1, result_2 = cls._parse_gw_result(entry_1_points, entry_2_points)

                if str(gameweek) not in results.keys():
                    results[str(gameweek)] = {}
                results[str(gameweek)].update(
                    {match.get('league_entry_1'): (entry_1_points, result_1),
                    match.get('league_entry_2'): (entry_2_points, result_2)}
                )

        return team_info, results

    @classmethod
    def _parse_gw_result(cls, entry_1_points: int, entry_2_points: int) -> Tuple[str, str]:
        if entry_1_points > entry_2_points:
            return 'W', 'L'
        elif entry_1_points < entry_2_points:
            return 'L', 'W'
        else:
            return 'D', 'D'

    @classmethod
    def get_league_table(cls, team_info: Dict, league_results: Dict) -> pd.DataFrame:
        """
        Returns a pandas DataFrame of the league table for the given league.
        TODO: Clean up this method
        """
        league_table = {}
        for team_id, team_info in team_info.items():
            league_table[team_id] = {
                'team_name': team_info.get('team_name'),
                'player_name': team_info.get('player_name'),
                'total_points': 0,
                'points': 0,
                'xPts': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'gw_points': {}
            }

        for gw, gw_results in league_results.items():
            gw_point_list = [team[0] for team in gw_results.values()]
            for team_id, team_result in gw_results.items():
                league_table[team_id]['total_points'] += team_result[0]
                league_table[team_id]['gw_points'][gw] = team_result[0]
                xpts = cls._get_expected_points(gw_point_list, team_result[0])

                league_table[team_id]['xPts'] += xpts
                if team_result[1] == 'W':
                    league_table[team_id]['wins'] += 1
                    league_table[team_id]['points'] += 3
                elif team_result[1] == 'L':
                    league_table[team_id]['losses'] += 1
                else:
                    league_table[team_id]['draws'] += 1
                    league_table[team_id]['points'] += 1

        league_table = pd.DataFrame.from_dict(league_table, orient='index')
        league_table = league_table.sort_values(by=['points'], ascending=False)
        league_table['rank'] = range(1, len(league_table) + 1)
        league_table['xPts'] = league_table['xPts'].round(2)
        league_table = league_table[
            ['rank', 'team_name', 'player_name', 'total_points',
            'wins', 'draws', 'losses', 'points', 'xPts']
            ]
        return league_table

    @classmethod
    def _get_expected_points(cls, gw: List, points: int) -> float:
        """
        Returns the expected points for a given gameweek.
        """
        # Percentage of teams that scored less than the team or equal to a given team
        # multiplied by 3 points for a win, plus 1 point for a draw
        xpts = 3 * (sum(i < points for i in gw) / (len(gw) -1) ) + \
            1 * ((sum(i == points for i in gw) - 1) / (len(gw) -1) )
        return xpts
