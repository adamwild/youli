def vod_to_video(vod):
    curr_video = {}
    curr_video['title'] = vod['title']
    curr_video['videoId'] = vod['url'].split('/')[-1]
    curr_video['url'] = vod['url']
    curr_video['description'] = vod['description']
    curr_video['publishedAt'] = vod['published_at']

    return curr_video

def get_n_vods(n, id, headers):
    import requests

    vods_url = f'https://api.twitch.tv/helix/videos?user_id={id}&type=archive&first={n}'
    vods_response = requests.get(vods_url, headers=headers)
    vods = vods_response.json()['data']

    return vods

def get_all_vods(id, headers):
    import requests

    vods_url = f'https://api.twitch.tv/helix/videos?user_id={id}&type=archive'
    vods_response = requests.get(vods_url, headers=headers)
    vods = vods_response.json()['data']

    return vods