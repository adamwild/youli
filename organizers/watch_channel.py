class ChannelWatcher():
    def __init__(self, organizer_name, source_video_url, source_name = "", wiki_identifier_functions = []):
        from pathlib import Path
        
        self.organizer_name = organizer_name

        if not type(wiki_identifier_functions) is list:
            wiki_identifier_functions = [wiki_identifier_functions]
        self.wiki_identifier_functions = wiki_identifier_functions
        
        # Can be a YouTube Id, a channel, A yt playlist, a Twitch vod page
        self.source_video_url = source_video_url

        organizers_folder = Path(__file__).parent
        self.source_name = source_name
        self.source_name = self.get_source_name(source_name)

        self.organizer_path = organizers_folder / organizer_name
        self.organizer_path.mkdir(parents=True, exist_ok=True)

        self.channel_info_path = self.organizer_path / (self.source_name + ".csv")
        self.load_channel_info()

    def get_source_name(self, source_name = ""):
        if source_name:
            return source_name
        
        elif self.source_name:
            return self.source_name
        
        elif 'twitch' in self.source_video_url:
            from utils.api_twitch import TwitchAPI
            twitch_api = TwitchAPI(self.source_video_url)
            self.website = 'twitch'
            self.api = twitch_api
            return f"twitch_{self.api.channel_name}"
        
        else:
            from utils.api_youtube import YoutubeAPI
            yt_api = YoutubeAPI(self.source_video_url)
            self.website = 'youtube'
            self.api = yt_api
            if yt_api.youtube_url_type == "channel":
                return f"yt_{yt_api.youtube_url_type}_{yt_api.channel_name}"
            elif yt_api.youtube_url_type == "playlist":
                return f"yt_{yt_api.youtube_url_type}_{yt_api.playlist_title}"
            
    def start_channel_watching(self, num_first_batch):
        # Initiate a csv file containing pertaining info
        # csv should have video_title, video_id, publication_date, playlist_name (opt), wiki_page (opt), inserted_in_wiki (opt), description (opt)

        latest_videos = self.api.get_latest_videos(num_first_batch)
        df = self.videos_to_dataframe(latest_videos)

        self.df_channel_info = df

        self.save_channel_info()

    def videos_to_dataframe(self, videos):
        import pandas as pd

        dict_df = {key: [] for key in ['video_title', 'video_id', 'publication_date', 'playlist_name', 'wiki_page', 'inserted_in_wiki']}

        for video in videos:
            dict_df = self.base_update_dict_with_video_info(dict_df, video)

        df = pd.DataFrame(dict_df)
        return df

    def identify_wiki_page(self, video_title, publishedAt, description):
        """wiki_identifier_function return a wiki page if they can, an empty string if not"""
        import numpy as np

        for wiki_identifier_function in self.wiki_identifier_functions:
            wiki_page = wiki_identifier_function(video_title, publishedAt, description)
            if wiki_page:
                return wiki_page
            
        return np.nan
    
    def base_update_dict_with_video_info(self, dict_df, video):
        import numpy as np

        dict_df['video_title'].append(video['title'])
        dict_df['video_id'].append(video['videoId'])
        dict_df['publication_date'].append(video['publishedAt'])

        playlist_title = self.api.playlist_title
        if playlist_title:
            dict_df['playlist_name'].append(self.api.playlist_title)
        else:
            dict_df['playlist_name'].append(np.nan)
        
        video_title, publishedAt, description = video['title'], video['publishedAt'], video['description']
        wiki_page = self.identify_wiki_page(video_title, publishedAt, description)
        dict_df['wiki_page'].append(wiki_page)

        dict_df['inserted_in_wiki'].append(np.nan)

        # dict_df['description'].append(video['description'])

        return dict_df

    def get_latest_video_id(self):
        # Loads the video id of the latest video archived in "channel_info"
        latest_video_id = self.df_channel_info['video_id'].iloc[0]
        return latest_video_id

    def update_latest_videos(self):
        import pandas as pd

        latest_video_id = self.get_latest_video_id()
        latest_videos = self.api.get_new_videos_until(latest_video_id)

        df_latest = self.videos_to_dataframe(latest_videos)
        
        # Concatenate new videos to the old ones
        new_df_channel_info = pd.concat([df_latest, self.df_channel_info], ignore_index=True)

        self.df_channel_info = new_df_channel_info
        
        self.save_channel_info()

    def load_channel_info(self):
        import pandas as pd

        if self.channel_info_path.is_file():
            df_channel_info = pd.read_csv(self.channel_info_path)

            self.df_channel_info = df_channel_info
        else:
            self.df_channel_info = ""

    def save_channel_info(self):
        import pandas as pd
        
        if isinstance(self.df_channel_info, pd.DataFrame):
            self.df_channel_info.to_csv(self.channel_info_path, index=False)

    def reset(self):
        # Deletes the csv file containing channel_info
        self.channel_info_path.unlink()


if __name__ == "__main__":
    channel_name = "@PiGCasts"
    main_page = "https://www.youtube.com/@PiGCasts/featured"
    video_page = "https://www.youtube.com/@PiGCasts/videos"
    playlist_url = "https://www.youtube.com/watch?v=dv-UplSqjX0&list=PLKmPRMduwUyWgGWg7x-e6S_ePhIg-KWUB"

    twitch_channel = "https://www.twitch.tv/x5_pig"

    channel_watcher = ChannelWatcher("pig", twitch_channel)
    # channel_watcher.start_channel_watching(10)

    channel_watcher.update_latest_videos()

