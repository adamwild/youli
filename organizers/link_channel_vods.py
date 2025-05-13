from organizers.watch_channel import ChannelWatcher

class LinkChannelVods(ChannelWatcher):
    """Interacts with the already created database of Vods."""
    def __init__(self, organizer_name, source_video_url, source_name="", wiki_identifier_functions = []):
        super().__init__(organizer_name, source_video_url, source_name, wiki_identifier_functions)

    def get_vods_without_wiki(self):
        return self.df_channel_info[self.df_channel_info['wiki_page'].isna()]
    
    def get_ids_without_wiki(self):
        vods_without_wiki = self.get_vods_without_wiki()
        return list(vods_without_wiki['video_id'])
    
    def mark_as_inserted(self, list_video_ids):
        self.df_channel_info.loc[self.df_channel_info['video_id'].isin(list_video_ids), 'inserted_in_wiki'] = True
        self.save_channel_info()


if __name__ == "__main__":
    channel_name = "@PiGCasts"

    twitch_channel = "https://www.twitch.tv/x5_pig"    

    link_channel = LinkChannelVods("pig", twitch_channel)
    # link_channel.reset()
    # link_channel.start_channel_watching(5)

    df = link_channel.get_vods_without_wiki()
    print(df)


    