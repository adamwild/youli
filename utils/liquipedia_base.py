def get_date(row):
    if "|date=" in row:
        return row[row.index("|date=")+6:row.index("|date=")+16]
    return ""

def get_map(row):
    if "Map|map=" in row:
        map_name = row.split('Map|map=')[1].split("|")[0].lower()

        # Fix for Pylon map, Liquipedia name is 'Pylon (map)'
        map_name = map_name.split('(')[0]
        
        return map_name
    return ""

def get_opponent_old(row):
    if "|opponent" in row:
        oppo = row.split('=')[-1].split("}")[0]
        oppo = oppo.lower().strip()
        return oppo
    return ""


def get_opponent(row):
    import re

    if "|opponent" in row:
        row = row[row.index("="):]
        match = re.search(r'1=([^|}]+)', row)
        if match:
            return match.group(1).lower().strip()
        else:
            return row.split('1v1Opponent|')[1].split('}')[0]
    return ""

def make_vod_link(vod_link, time_seconds):
    if type(time_seconds) is str:
        time_seconds = int(time_seconds)

    if "youtube" in vod_link:
        return f"{vod_link}&t={time_seconds}s"
    
    if "twitch" in vod_link:
        h, m, s = time_seconds // 3600, (time_seconds % 3600) // 60, time_seconds % 60
        return f"{vod_link}?t={h}h{m}m{s}s"
    
    return vod_link

def has_same_players_map(game, opponent1, opponent2, map_played):

    from utils.config_utils import wiki_to_game_name

    def get_all_names(opponent, wiki_to_game_name):
        
        if opponent in wiki_to_game_name:

            game_names = wiki_to_game_name[opponent]
            if type(game_names) is str:
                all_opponent_names = list(game_names)
            else:
                all_opponent_names = game_names

            all_opponent_names.append(opponent)
            return all_opponent_names
        
        return [opponent]

    all_opponent1_names = get_all_names(opponent1, wiki_to_game_name)
    all_opponent2_names = get_all_names(opponent2, wiki_to_game_name)

    players = [player.lower().strip() for player in game['players']]
    for opponent_names in [all_opponent1_names, all_opponent2_names]:
        for opponent in opponent_names:
            opponent = opponent.lower().strip()
            if any([opponent in player for player in players]):
                break
            return False
    
    map_played = map_played.lower().strip()
    map_names = [map_name.lower().strip() for map_name in game['map_names']]
    if not any([map_played in map_name for map_name in map_names]):
        return False
    
    return True



def add_vod_to_map(row, vod_link):
    return row[:-2] + "|vod=" + vod_link + '}}'

def liquipedia_to_game_name(liquipedia_name):
    from utils.config_utils import wiki_to_game_name

    if liquipedia_name in wiki_to_game_name:
        return wiki_to_game_name[liquipedia_name]
    return liquipedia_name

def extended_fusion_test(fused_vod_matchup, opponent1, opponent2, map_played):
    from utils.config_utils import wiki_to_game_name

    def get_all_names(opponent, wiki_to_game_name):
        
        if opponent in wiki_to_game_name:

            game_names = wiki_to_game_name[opponent]
            if type(game_names) is str:
                all_opponent_names = list(game_names)
            else:
                all_opponent_names = game_names

            all_opponent_names.append(opponent)
            return all_opponent_names
        
        return [opponent]

    all_opponent1_names = get_all_names(opponent1, wiki_to_game_name)
    all_opponent2_names = get_all_names(opponent2, wiki_to_game_name)

    # print(all_opponent1_names)
    # print(all_opponent2_names)

    is_map_in_fused = map_played in fused_vod_matchup
    is_opponent1_in_fused = any(keyword in fused_vod_matchup for keyword in all_opponent1_names)
    is_opponent2_in_fused = any(keyword in fused_vod_matchup for keyword in all_opponent2_names)

    return all([is_map_in_fused, is_opponent1_in_fused, is_opponent2_in_fused])

