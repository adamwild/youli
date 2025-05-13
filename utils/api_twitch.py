# For this Class, we mimic the same attributes and methods as YoutubeAPI so that they can be used interchangably
# This Class will mostly behave like YoutubeAPI instantiated with a user's page (and not a playlist)

class TwitchAPI():
    def __init__(self, twitch_page):
        from config import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET

        self.client_id = TWITCH_CLIENT_ID
        self.client_secret = TWITCH_CLIENT_SECRET

        # Does not apply here (Twitch has no playlists), so it will remain an empty string
        self.playlist_title = ""

        self.page = twitch_page
        self.channel_name = self.get_channel_name()

        self.get_access_token()
        self.id = self.get_channel_id(self.channel_name)

    def get_channel_id(self, channel_name = ""):
        import requests

        self.headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        }
        user_url = f'https://api.twitch.tv/helix/users?login={self.channel_name}'
        user_response = requests.get(user_url, headers=self.headers)
        user_id = user_response.json()['data'][0]['id']

        return user_id

    def get_channel_name(self):
        return self.page.split('/')[3].split('/')[0]
    
    def get_access_token(self):
        import requests

        # Get access token
        url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        self.response = requests.post(url, params=params)
        self.access_token = self.response.json()['access_token']
    
    def get_latest_videos(self, n=5):
        """Returns a list of 'videos', each video.keys() = 'title', 'videoId', 'url', 'description', 'publishedAt' """
        from utils.api_twitch_utils import vod_to_video, get_n_vods

        vods = get_n_vods(n, self.id, self.headers)

        videos = []

        # Print VOD titles and URLs
        for vod in vods:
            curr_video = vod_to_video(vod)
            videos.append(curr_video)

        return videos
    
    def get_new_videos_until(self, stop_video_id):
        from utils.api_twitch_utils import vod_to_video, get_all_vods

        vods = get_all_vods(self.id, self.headers)

        videos = []

        # Print VOD titles and URLs
        for vod in vods:
            curr_video_id = vod['url'].split('/')[-1]
            if str(curr_video_id) == str(stop_video_id):
                break
            curr_video = vod_to_video(vod)
            videos.append(curr_video)

        return videos
        


if __name__ == "__main__":
    twitch_channel = "https://www.twitch.tv/x5_pig"

    stop_video_id = '2448194309'

    twitch_api = TwitchAPI(twitch_channel)

    for elt in twitch_api.get_new_videos_until(stop_video_id):
        print(elt)
        print()