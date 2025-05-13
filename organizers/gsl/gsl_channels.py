from organizers.link_channel_vods import LinkChannelVods
from organizers.prepare_insertion import InsertionPreparator

from organizers.wiki_identifers_func import *

class GlobalStarcraftLeagueVods(InsertionPreparator):
    def __init__(self):
        self.organizer_name = "gsl"

        main_yt_page = "@SOOPesports_EN"

        # wiki identifier functions
        wiki_gsl_s1_2025 = lambda x, y, z : title_to_wiki(x, y, z, '[2025 GSL S1]', 'Global_StarCraft_II_League/2025/Season_1')

        wiki_functions = [wiki_gsl_s1_2025]

        yt_channel = LinkChannelVods(self.organizer_name, main_yt_page, wiki_identifier_functions=wiki_functions)

        list_link_channels = [yt_channel]

        super().__init__(list_link_channels)

if __name__ == '__main__':
    gsl_vods = GlobalStarcraftLeagueVods()
    
    # Initialisation
    # gsl_vods.start_watching_channels(11)

    # Create / update fused info table
    # gsl_vods.update_fused_info()

    # gsl_vods.assign_wiki_pages_manual()