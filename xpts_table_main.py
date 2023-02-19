import pandas as pd
import plotly.graph_objects as go

from scrape_league_players import ScrapeSingleLeague


def plot_table(league_table: pd.DataFrame, gw: int) -> None:
    """
    Plots the league table for the given gameweek.
    """
    fig = go.Figure(data=[go.Table(header=dict(values=list(league_table.columns)),
                cells=dict(values=[league_table['rank'], league_table['team_name'],
                league_table['player_name'], league_table['total_points'],
                league_table['wins'], league_table['draws'], league_table['losses'],
                league_table['points'], league_table['xPts']]))
                ])
    fig.update_layout(title=f'Gameweek {gw} League Table')
    fig.update_layout(autosize=True)
    fig.show()

def main() -> None:
    team, team_results = ScrapeSingleLeague.get_league_results(38838)
    league_table = ScrapeSingleLeague.get_league_table(team, team_results)
    plot_table(league_table, 24)

if __name__ == "__main__":
    main()