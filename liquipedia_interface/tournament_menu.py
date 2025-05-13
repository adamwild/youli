from liquipedia_interface.tournament_page import TournamentPage
from liquipedia_interface.menu_utils import *

class TournamentMenu(TournamentPage):
    def __init__(self, wiki_page):
        
        super().__init__(wiki_page)

        self.time_to_wait = 1

    def options_menu(self):
        import keyboard
        import time
        self.clear_screen()
        
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

        self.pp_menu_contexts()
        
        time.sleep(self.time_to_wait)
        key = keyboard.read_event().name
        num_key = key_to_number(key)
        
        if num_key == 0:
            self.clear_screen()
            return

        return self.select_matchup(self.contexts[num_key-1])
    
    def select_matchup(self, context):
        import time
        import keyboard

        self.pp_menu_matches(context)

        time.sleep(self.time_to_wait)
        key = keyboard.read_event().name
        num_key = key_to_number(key)

        if num_key == 0:
            self.select_groupstage()
            return

        else:
            match = self.structured_matches[context][num_key-1]
            if self.delete_previous:
                match.delete_vods()

            return match
    
    def interactive_link_insertion(self, vods):
        """vod contains title_of_vod and the link"""
        import pyperclip
        self.options_menu()

        for vod in vods:
            vod_name, vod_link = vod
            print(f"{vod_name} - {vod_link}")
            match = self.select_groupstage()

            if match is None:
                # Add vod to a .txt file, it will be marked as inserted and will be handled by another pipeline
                self.add_vod_to_video_pipeline_stack(vod_name, self.wiki_page, vod_link)
                continue

            match.insert_vod(vod_link)
            self.clear_screen()

        pyperclip.copy(str(self))

    def add_vod_to_video_pipeline_stack(self, vod_name, wiki_page, vod_link):
        import pandas as pd
        from pathlib import Path

        # Get the path to the CSV file
        main_folder = Path(__file__).parent.parent
        video_data_folder = main_folder / 'video' / 'data'
        path_vods_for_video_pipeline = video_data_folder / 'vods_for_video_pipeline.csv'

        video_data_folder.mkdir(parents=True, exist_ok=True)

        df_row = {'vod_name': [vod_name], "wiki_page": [wiki_page], 'vod_link': [vod_link]}
        df_row = pd.DataFrame(df_row)

        if not path_vods_for_video_pipeline.is_file():
            df_row.to_csv(path_vods_for_video_pipeline, index=False)
            return
        
        else:
            with open(path_vods_for_video_pipeline, 'r') as f:
                if not f.read().strip():
                    df_row.to_csv(path_vods_for_video_pipeline, index=False)
                    return

        df_stack = pd.read_csv(path_vods_for_video_pipeline)
        df_stack = pd.concat([df_stack, df_row])
        df_stack = df_stack.drop_duplicates()

        df_stack.to_csv(path_vods_for_video_pipeline, index=False)

    def clear_screen(self):
        import os
        os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    from organizers.pig.pig_channels import PigVods
    from liquipedia_interface.link_insertion_utils import make_url

    pv = PigVods()
    df_fused_info = pv.load_fused_info()
    df_fused_info['url'] = df_fused_info.apply(make_url, axis=1)

    wiki_pig = 'PiG_Sty_Festival/6'

    wiki_gsl = 'Global_StarCraft_II_League/2025/Season_1'

    tm = TournamentMenu(wiki_pig)
    tm.add_vod_to_video_pipeline_stack("hello")
    # tm.copy()

    """import pandas as pd

    to_insert = df_fused_info[
        (df_fused_info['website'] == 'youtube') &
        (df_fused_info['wiki_page'] == wiki_pig) &
        (pd.isna(df_fused_info['inserted_in_wiki'])) &
        (df_fused_info['video_title'] != 'Private video')
    ]

    vods = zip(list(to_insert['video_title']), list(to_insert['url']))"""