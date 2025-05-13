# For a given organizer, update all VoDs and select the ones that need to be inserted into Liquipedia
# 

class MultiPlatformVODs():
    def __init__(self, list_link_channels):

        # List of ChannelWatcher objects for a given organizer
        self.link_channels = list_link_channels

        # Regroup all sources by website (to ensure unique video ids)
        self.regroup_by_website()

        # Memory is the compiled DataFrames of already handled vods, starts empty
        self.memory = ""

        # Compiled df info of all videos tracked
        self.path_fused_channels_info = self.link_channels[0].organizer_path / 'fused_channels_info.csv'

        self.load_fused_info()

    def load_fused_info(self):
        import pandas as pd
        if self.path_fused_channels_info.is_file():
            df_fused_info = pd.read_csv(self.path_fused_channels_info)
        else:
            df_fused_info = pd.DataFrame()

        self.df_fused_info = df_fused_info
        return df_fused_info
    
    def save_fused_info(self):
        self.df_fused_info.to_csv(self.path_fused_channels_info, index=False)

    def update_tracked_channels(self):
        for link_channel in self.link_channels:
            link_channel.update_latest_videos()

    def start_watching_channels(self, num_first_batch = 5):
        for link_channel in self.link_channels:
            link_channel.start_channel_watching(num_first_batch)

    def identify_all_wikis(self):
        for link_channel in self.link_channels:
            link_channel.identify_wiki_page()

    def regroup_by_website(self):
        by_website = {}
        for link_channel in self.link_channels:
            curr_website = link_channel.website

            if curr_website not in by_website:
                by_website[curr_website] = [link_channel]

            else:
                by_website[curr_website].append(link_channel)

        # Playlists are easier to identify the wiki of, so we sort the youtube sources to have playlists come first
        if 'youtube' in by_website:
            sorted_yt = sorted(by_website['youtube'], key=lambda obj: obj.api.youtube_url_type != 'playlist')
            by_website['youtube'] = sorted_yt

        self.channels_by_website = by_website

    def make_candidate_fused_info(self):
        import pandas as pd
        df_fused_info = pd.DataFrame()

        for website in self.channels_by_website:
            website_df = pd.DataFrame()
            for link_channel in self.channels_by_website[website]:
                df_to_add = link_channel.df_channel_info.copy()
                df_to_add['website'] = website

                if website_df.empty:
                    website_df = df_to_add
                    continue

                # Step 1: Identify new rows (video_id not in website_df)
                new_rows = df_to_add[~df_to_add['video_id'].isin(website_df['video_id'])]

                # Step 2: Identify rows to update (video_id exists and wiki_page is not NaN)
                rows_to_update = df_to_add[
                    df_to_add['video_id'].isin(website_df['video_id']) & df_to_add['wiki_page'].notna()
                ]

                # Step 3: Drop rows from website_df that will be updated
                website_df = website_df[~website_df['video_id'].isin(rows_to_update['video_id'])]

                # Step 4: Concatenate updated and new rows
                website_df = pd.concat([website_df, rows_to_update, new_rows], ignore_index=True)

            if df_fused_info.empty:
                df_fused_info = website_df
                continue

            df_fused_info = pd.concat([website_df, df_fused_info], ignore_index=True)

        return df_fused_info
    
    def update_fused_info(self):
        import pandas as pd

        df_candidate_fused_info = self.make_candidate_fused_info()
        if not self.path_fused_channels_info.is_file():
            df_candidate_fused_info.to_csv(self.path_fused_channels_info, index=False)
            return
        
        df_fused_info = pd.read_csv(self.path_fused_channels_info)

        df_candidate_fused_info['video_id'] = df_candidate_fused_info['video_id'].astype(str)
        df_fused_info['video_id'] = df_fused_info['video_id'].astype(str)

        new_rows = df_candidate_fused_info[~df_candidate_fused_info['video_id'].isin(df_fused_info['video_id'])]

        df_fused_info = pd.concat([df_fused_info, new_rows], ignore_index=True)

        df_fused_info.to_csv(self.path_fused_channels_info, index=False)

    def handle_single_channel_vods(self, link_channel):
        """Goes through a link_channel, updates values with memory, returns vods that haven't been linked in Liquipedia"""

        def update_channel_with_previous_work(memory, link_channel):
            """If a video_id already exists in memory, update link_channel with memory data"""
            curr_df = link_channel.df_channel_info
            curr_df.set_index('video_id', inplace=True)
            curr_df.update(memory.set_index('video_id'))
            curr_df.reset_index(inplace=True)

            link_channel.df_channel_info = curr_df
            link_channel.save_channel_info()

        update_channel_with_previous_work(self.memory, link_channel)

        return link_channel.get_vods_without_wiki()

    def assign_wiki_pages_manual(self):
        """Goes through the fused_channels_info, asks the user for the wiki page each time the field is empty (NaN)"""
        import pandas as pd
        df_fused_info = pd.read_csv(self.path_fused_channels_info)

        df_fused_info['wiki_page'] = df_fused_info['wiki_page'].astype('object')

        for idx, row in df_fused_info.iterrows():
            if pd.isna(row['wiki_page']):
                print(f"Website: {row['website']}")
                print(f"Video title: {row['video_title']}")
                user_input = input("Enter wiki info: ")
                df_fused_info.at[idx, 'wiki_page'] = user_input
                print()

        df_fused_info.to_csv(self.path_fused_channels_info, index=False)

    def select(self, selection):
        """Select from self.df_fused_info, 'selection' is a list of tuples, each tuple is a column associated with its desired value
        ex: selection = [('website', 'youtube'), ('wiki_page', 'PiG_Sty_Festival/6')]"""
        import pandas as pd

        mask = pd.Series([True] * len(self.df_fused_info))

        for column, value in selection:
            if value == 'nan':
                mask &= pd.isna(self.df_fused_info[column])

            elif value.startswith('not_'):
                mask &= (self.df_fused_info[column] != value[4:])

            else:
                mask &= (self.df_fused_info[column] == value)

        return self.df_fused_info[mask]
        
    def clean(self):
        """Cleans df_fused_info from unusable entries
        Mostly just private videos, change them into a fake entry of an inserted video
        For videos that don't have a wiki to be inserted to df['wiki_page'] = 'none', assign True to is_inserted"""
        pass

    def pp_channel_info_path(self):
        for link_channel in self.link_channels:
            print(link_channel.channel_info_path)

    def pp_channel_info_df(self):
        for link_channel in self.link_channels:
            print(link_channel.df_channel_info.head)
            print()

    def reset(self):
        for link_channel in self.link_channels:
            link_channel.reset()


if __name__ == "__main__":
    from organizers.watch_channel import ChannelWatcher
    from organizers.link_channel_vods import LinkChannelVods

    video_page = "https://www.youtube.com/@PiGCasts/videos"
    playlist_url = "https://www.youtube.com/watch?v=dv-UplSqjX0&list=PLKmPRMduwUyWgGWg7x-e6S_ePhIg-KWUB"
    twitch_channel = "https://www.twitch.tv/x5_pig"

    vod_source1 = LinkChannelVods("pig", twitch_channel)
    vod_source2 = LinkChannelVods("pig", video_page)
    vod_source3 = LinkChannelVods("pig", playlist_url)

    list_sources = [vod_source1, vod_source2, vod_source3]

    mpv = MultiPlatformVODs(list_sources)

    # selection = [('website', 'youtube'), ('wiki_page', 'PiG_Sty_Festival/6'), ('inserted_in_wiki', 'nan'), ('video_title', 'not_Private video')]
    # selection = [('website', 'youtube'), ('wiki_page', 'PiG_Sty_Festival/6'), ('inserted_in_wiki', 'not_nan'), ('video_title', 'not_Private video')]
    # print(mpv.select(selection))

    # mpv.assign_wiki_pages_manual()
    # mpv.update_fused_info()

    df_fused_info = mpv.make_candidate_fused_info()

    print(df_fused_info)

    """by_website = mpv.regroup_by_website()

    for link_channel in by_website['youtube']:
        print(link_channel.api.youtube_url_type)"""




