from organizers.link_channel_vods import LinkChannelVods
from organizers.prepare_insertion import InsertionPreparator

from organizers.wiki_identifers_func import *

class WardiVods(InsertionPreparator):
    def __init__(self):
        self.organizer_name = "wardi"

        main_yt_page = "@WardiTV"

        # wiki identifier functions
        wiki_wardi_mondays = lambda x, y, z : title_number_to_wiki(x, y, z, 'WardiTV Mondays', 'WardiTV_Mondays')
        wiki_spring_championship = lambda x, y, z : title_number_to_wiki(x, y, z, 'WardiTV Spring Championship', 'WardiTV_Spring_Championship')

        wiki_functions = [wiki_wardi_mondays, wiki_spring_championship]

        yt_channel = LinkChannelVods(self.organizer_name, main_yt_page, wiki_identifier_functions=wiki_functions)

        list_link_channels = [yt_channel]

        super().__init__(list_link_channels)

if __name__ == '__main__':
    wv = WardiVods()
    
    # Initialisation
    # wv.start_watching_channels(20)

    # Create / update fused info table
    # wv.update_fused_info()

    # wv.assign_wiki_pages_manual()

    # The rest (and this too actually) is handled at the root by vods_to_wiki.py. See you there!

