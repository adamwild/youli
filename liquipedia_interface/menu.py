from liquipedia_interface.navigator import Navigator
from liquipedia_interface.menu_utils import *
from liquipedia_interface.link_insertion_utils import *

class Menu(Navigator):
    def __init__(self, wiki_page):
        super().__init__(wiki_page)

        self.games = self.gather_games()

        # Sleep time between keystrokes
        self.time_to_wait = 1

    def options_menu(self):
        import keyboard
        import time
        print('Delete previous VoDs ?\n1. Yes\n2. No\n')
        time.sleep(self.time_to_wait)
        key = keyboard.read_event().name
        if key == '1':
            self.delete_previous = True
        elif key == '2':
            self.delete_previous = False
            

    def select_groupstage(self):
        import time
        import keyboard

        # Not optimal but low cost, since the indexes are all changed after an insertion, re-parse the raw_wiki
        self.gather_games()

        for ind, groupstage in enumerate(self.games.keys()):
            print(f'{number_to_key(ind+1)}. {groupstage} - {self.games[groupstage]}')

        print()
        
        groupstages = list(self.games.keys())

        time.sleep(self.time_to_wait)
        key = keyboard.read_event().name
        num_key = key_to_number(key)
        

        if num_key == 0:
            return

        return self.select_matchup(self.games[groupstages[num_key-1]])

    def select_matchup(self, matchups):
        import keyboard
        import time
        for ind, matchup in enumerate(matchups):
            print(f'{number_to_key(ind+1)}. {matchup[0]}')

            if ind > 0 and ind % 4 == 0:
                print()

        print()

        time.sleep(self.time_to_wait)
        key = keyboard.read_event().name
        num_key = key_to_number(key)
        
        if num_key == 0:
            self.select_groupstage()
            return

        else:
            return matchups[num_key-1]

    def interactive_link_insertion(self, vods):
        """vod contains title_of_vod and the link"""
        import pyperclip
        self.options_menu()

        for vod in vods:
            vod_name, vod_link = vod
            print(f"{vod_name} - {vod_link}")
            result = self.select_groupstage()

            if result is None:
                continue

            matchup_name, ind_end_matchup = result
            print("inserted!")
            self.split_wiki = insert_vod(self.split_wiki, ind_end_matchup, vod_link)

        full_wiki = '\n'.join(self.split_wiki)

        pyperclip.copy(full_wiki)
            

if __name__ == "__main__":
    from organizers.pig.pig_channels import PigVods
    from liquipedia_interface.link_insertion_utils import make_url

    pv = PigVods()
    df_fused_info = pv.load_fused_info()
    df_fused_info['url'] = df_fused_info.apply(make_url, axis=1)

    wiki_pig = 'PiG_Sty_Festival/6'


    import pandas as pd

    to_insert = df_fused_info[
        (df_fused_info['website'] == 'youtube') &
        (df_fused_info['wiki_page'] == wiki_pig) &
        (pd.isna(df_fused_info['inserted_in_wiki'])) &
        (df_fused_info['video_title'] != 'Private video')
    ]

    vods = zip(list(to_insert['video_title']), list(to_insert['url']))

    
    wiki_gsl = 'Global_StarCraft_II_League/2025/Season_1'

    menu = Menu(wiki_pig)
    menu.interactive_link_insertion(vods)