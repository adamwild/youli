def find_vod_emplacement(split_wiki, ind_end_matchup):
    """finds if a |vod= exists"""
    curr_ind = ind_end_matchup

    while not ('|vod=' in split_wiki[curr_ind] or '|map' in split_wiki[curr_ind]):
        curr_ind -= 1

    indent = split_wiki[curr_ind].split('|')[0]

    # '|map' is found before an empty '|vod=' a vod link should be inserted at the end of the matchup description
    if '|map' in split_wiki[curr_ind]:
        
        return False, ind_end_matchup, indent
        
    # '|vod=' does exist, insert in place
    else:
        return True, curr_ind, indent
    
def insert_vod(split_wiki, ind_end_matchup, vod_link):
    """Returns split_wiki with the vod inserted in the correct position"""
    is_inplace, ind_insert, indent = find_vod_emplacement(split_wiki, ind_end_matchup)

    vod_item = f"{indent}|vod={vod_link}"

    if is_inplace:
        split_wiki[ind_insert] = vod_item

    else:
        split_wiki.insert(ind_insert+1, vod_item)

    return split_wiki

def make_url(row):
    if 'youtube' in row['website']:
        return f"https://www.youtube.com/watch?v={row['video_id']}"
    
    elif 'twitch' in row['website']:
        return f"https://www.twitch.tv/videos/{row['video_id']}"