import grequests
import requests
import json
import random
import time

# Teams in league & head to head results & fixtures
LEAGUE_DETAILS = 'https://draft.premierleague.com/api/league/38838/details'
# League trade status & who owns which player at current time
LEAGUE_ELEMENT_STATUS = 'https://draft.premierleague.com/api/league/1/element-status'
# League waiver & free agents for all gameweeks. Includes if waiver successful or not
LEAGUE_TRANSACTIONS = 'https://draft.premierleague.com/api/draft/league/38838/transactions'
# Initial draft picks by league
LEAGUE_DRAFT_CHOICE = 'https://draft.premierleague.com/api/draft/1/choices'
# Team per gameweek
TEAM_OWNERSHIP_PER_GW = 'https://draft.premierleague.com/api/entry/1/event/15'
# TODO: Do this dynamically with decent accuracy
TOTAL_LEAGUES = 252657



# out = requests.get('https://draft.premierleague.com/api/league/38838/details')
# league_dict = json.loads(out.content)

# league_entries = len(league_dict.get('league_entries'))
# print(f"league entries {league_entries}")
# print(len(league_dict.get('league_entries')))

def league_search(total_league, sample_n, search_size):
    league_id = random.sample(range(1, total_league), sample_n)
    success_list = []
    fail_list = []
    for _id in league_id:
        response = requests.get(f'https://draft.premierleague.com/api/league/{_id}/details')
        if response.status_code == 200:
            league_dict = json.loads(response.content)
            league_entries = len(league_dict.get('league_entries'))
            if league_entries == search_size:
                success_list.append(_id)
            # print(f"league ID {_id} entries {league_entries}")
        else:
            # print(f"league ID {_id} NOT FOUND f{response.status_code}")
            fail_list.append(response.status_code)
        # time.sleep(0.1)
    print(success_list)
    print(fail_list)

def league_search_async(total_league, sample_n, search_size):
    league_id = random.sample(range(1, total_league), sample_n)
    urls = [f'https://draft.premierleague.com/api/league/{_id}/details' for _id in league_id]
    rs = (grequests.get(u) for u in urls)
    
    res = grequests.map(rs)
    print(res)

    # success_list = []
    # fail_list = []
    # for _id in league_id:
    #     response = requests.get(f'https://draft.premierleague.com/api/league/{_id}/details')
    #     if response.status_code == 200:
    #         league_dict = json.loads(response.content)
    #         league_entries = len(league_dict.get('league_entries'))
    #         if league_entries == search_size:
    #             success_list.append(_id)
    #         # print(f"league ID {_id} entries {league_entries}")
    #     else:
    #         # print(f"league ID {_id} NOT FOUND f{response.status_code}")
    #         fail_list.append(response.status_code)
        # time.sleep(0.1)
    # print(success_list)
    # print(fail_list)

# league_search(TOTAL_LEAGUES, 50, 10)

league_search_async(TOTAL_LEAGUES, 5, 10)

# urls = [
#     'http://www.heroku.com',
#     'http://tablib.org',
#     'http://httpbin.org',
#     'http://python-requests.org',
#     'http://kennethreitz.com'
# ]

# rs = (grequests.get(u) for u in urls)
# out = grequests.map(rs)
# print(out)
