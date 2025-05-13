class YoutubeAPI():
    def __init__(self, youtube_page):
        from config import YOUTUBE_API_KEY
        
        self.playlist_title = ""

        # youtube_page is either a user's page or a playlist
        self.youtube_page = youtube_page
        self.api_key = YOUTUBE_API_KEY

        # youtube_page is a channel handle
        if youtube_page.startswith('@'):
            self.youtube_url_type = "channel"
            self.channel_name = youtube_page
            self.youtube_page = f"https://www.youtube.com/{self.channel_name}/videos"
            self.id = self.get_channel_id(self.channel_name)
            return
        
        self.youtube_url_type = self.get_youtube_url_type(youtube_page)

        # youtube_page is a link to a page
        if self.youtube_url_type == 'channel':
            self.channel_name = youtube_page.split('/')[3]
            self.id = self.get_channel_id(self.channel_name)
            if not self.youtube_page.endswith("/videos"):
                self.youtube_page = "https://www.youtube.com/" + self.channel_name + "/videos"
            return
        
        # youtube_page is a link to a playlist
        channel_handle, playlist_id, playlist_title = self.get_channel_handle_from_playlist(youtube_page)
        self.id = playlist_id
        self.channel_name = channel_handle
        self.youtube_page = youtube_page
        self.playlist_title = playlist_title
        
    def get_channel_id(self, channel_name = ""):
        """"Returns the ID of the channel_name
        For example: 'UCgh4BYhUOKwDLG4t8YC7ylw' for Pigs channel"""
        from googleapiclient.discovery import build

        if not channel_name.startswith('@'):
            channel_name = "@" + channel_name

        youtube = build('youtube', 'v3', developerKey=self.api_key)

        res = youtube.search().list(q=channel_name, type='channel', part='snippet', maxResults=1).execute()
        channel_id = res['items'][0]['snippet']['channelId']

        return channel_id
    
    def get_youtube_url_type(self, url):
        """Return 'channel' or 'playlist' based on the YouTube URL."""
        
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(url)

        if 'playlist' in parsed.path:
            return 'playlist'
        qs = parse_qs(parsed.query)
        if 'list' in qs and qs['list'][0].startswith('PL'):
            return 'playlist'
        if '/channel/' in parsed.path or '/user/' in parsed.path or '/@' in parsed.path:
            return 'channel'
        return 'unknown'
    
    def get_channel_handle_from_playlist(self, playlist_url):
        from urllib.parse import urlparse, parse_qs
        from googleapiclient.discovery import build

        parsed = urlparse(playlist_url)
        playlist_id = parse_qs(parsed.query).get('list', [None])[0]

        if not playlist_id:
            return None

        youtube = build('youtube', 'v3', developerKey=self.api_key)
        res = youtube.playlists().list(part='snippet', id=playlist_id).execute()
        if not res['items']:
            return None

        playlist_snippet = res['items'][0]['snippet']
        channel_id = playlist_snippet['channelId']
        playlist_title = playlist_snippet['title']

        ch_res = youtube.channels().list(part='snippet', id=channel_id).execute()
        channel_handle = ch_res['items'][0]['snippet'].get('customUrl', None)

        return channel_handle, playlist_id, playlist_title
    
    def get_latest_videos(self, n=5):
        from googleapiclient.discovery import build
        from urllib.parse import urlparse, parse_qs
        from utils.api_youtube_utils import get_videos_from_playlist, get_first_videos_from_playlist

        youtube = build('youtube', 'v3', developerKey=self.api_key)

        if self.youtube_url_type == 'channel':
            res = youtube.channels().list(part='contentDetails', id=self.id).execute()
            if not res['items']:
                return []
            uploads_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            return get_first_videos_from_playlist(uploads_id, youtube, n)

        elif self.youtube_url_type == 'playlist':
            all_videos_playlist = get_videos_from_playlist(self.id, youtube)

            all_videos_playlist = all_videos_playlist[::-1]
            return all_videos_playlist[:n]
        
        return []
    
    def get_new_videos_until(self, stop_video_id):
        from googleapiclient.discovery import build
        from urllib.parse import urlparse, parse_qs
        from utils.api_youtube_utils import get_videos_from_playlist

        youtube = build('youtube', 'v3', developerKey=self.api_key)

        def get_videos_from_playlist_until(playlist_id):
            videos = []
            next_page_token = None
            found = False

            while not found:
                res = youtube.playlistItems().list(
                    part='snippet',
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()

                for item in res.get('items', []):
                    vid = item['snippet']['resourceId']['videoId']
                    if vid == stop_video_id:
                        found = True
                        break
                    videos.append({
                        'title': item['snippet']['title'],
                        'videoId': vid,
                        'url': f"https://www.youtube.com/watch?v={vid}",
                        'description': item['snippet'].get('description', ''),
                        'publishedAt': item['snippet'].get('publishedAt', '')
                    })

                next_page_token = res.get('nextPageToken')
                if not next_page_token:
                    break

            return videos

        if self.youtube_url_type == 'channel':
            res = youtube.channels().list(part='contentDetails', id=self.id).execute()
            if not res['items']:
                return []
            uploads_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            return get_videos_from_playlist_until(uploads_id)

        elif self.youtube_url_type == 'playlist':
            all_videos_playlist = get_videos_from_playlist(self.id, youtube)
            all_videos_playlist = all_videos_playlist[::-1]

            videos_until_id = []
            for video in all_videos_playlist:
                if video['videoId'] == stop_video_id:
                    break
                videos_until_id.append(video)

            return videos_until_id

        return []

    def __str__ (self):
        sol = f"YouTube type: {self.youtube_url_type} - id: {self.id}\n"
        sol += f"{self.channel_name} - {self.youtube_page}"

        return sol
    
if __name__ == "__main__":
    channel_name = "@PiGCasts"
    main_page = "https://www.youtube.com/@PiGCasts/featured"
    video_page = "https://www.youtube.com/@PiGCasts/videos"
    playlist_url = "https://www.youtube.com/watch?v=dv-UplSqjX0&list=PLKmPRMduwUyWgGWg7x-e6S_ePhIg-KWUB"

    video_id_stop = "QQbaCkUo0yQ"

    yt_api = YoutubeAPI(channel_name)
    # print(yt_api.get_youtube_url_type())
    
    print(len(yt_api.get_new_videos_until(video_id_stop)))
    for elt in yt_api.get_new_videos_until(video_id_stop):
        print(elt['title'])
        print()

    """for elt in yt_api.get_latest_videos(n=5):
        print(elt)
        print()"""

    """for elt in [channel_name, main_page, video_page, playlist_url]:
        print(elt)
        yt_api = YoutubeAPI(elt)
        print(yt_api.get_latest_videos())
        print()"""

