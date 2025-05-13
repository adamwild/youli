
def get_videos_from_playlist(playlist_id, youtube):
    """Returns all the videos of a playlist"""
    videos = []
    next_page_token = None

    while True:
        res = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        videos.extend([
            {
                'title': item['snippet']['title'],
                'videoId': item['snippet']['resourceId']['videoId'],
                'url': f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}",
                'description': item['snippet'].get('description', ''),
                'publishedAt': item['snippet'].get('publishedAt', '')
            }
            for item in res.get('items', [])
        ])

        next_page_token = res.get('nextPageToken')
        if not next_page_token:
            break

    return videos

def get_first_videos_from_playlist(playlist_id, youtube, n):
    res = youtube.playlistItems().list(part='snippet', playlistId=playlist_id, maxResults=n).execute()
    return [
        {
            'title': item['snippet']['title'],
            'videoId': item['snippet']['resourceId']['videoId'],
            'url': f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}",
            'description': item['snippet'].get('description', ''),
            'publishedAt': item['snippet'].get('publishedAt', '')
        }
        for item in res.get('items', [])
    ]