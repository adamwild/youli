from organizers.multi_platform_vods import MultiPlatformVODs
from organizers.link_channel_vods import LinkChannelVods
from organizers.pig.pig_wiki_identifiers_func import *

from organizers.prepare_insertion import InsertionPreparator

class PigVods(InsertionPreparator):
    def __init__(self):
        self.organizer_name = "pig"

        main_yt_page = "@PiGCasts"
        pig_festival6 = "https://www.youtube.com/watch?v=dv-UplSqjX0&list=PLKmPRMduwUyWgGWg7x-e6S_ePhIg-KWUB"
        twitch = "https://www.twitch.tv/x5_pig"

        twitch_channel = LinkChannelVods(self.organizer_name, twitch)

        wiki_functions = [is_pig6]
        yt_channel = LinkChannelVods(self.organizer_name, main_yt_page, wiki_identifier_functions=wiki_functions)

        func_wiki_pig6 = lambda x, y, z : is_from_playlist(x, y, z, 'PiG_Sty_Festival/6')
        pig_festival6_playlist = LinkChannelVods(self.organizer_name, pig_festival6, wiki_identifier_functions=func_wiki_pig6)

        list_link_channels = [twitch_channel, yt_channel, pig_festival6_playlist]

        super().__init__(list_link_channels)

if __name__ == '__main__':
    pv = PigVods()
    
    pv.assign_wiki_pages_manual()