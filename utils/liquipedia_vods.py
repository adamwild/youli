from utils.api_liquipedia import LiquipediaAPI
from utils.liquipedia_base import *

class LiquipediaVods(LiquipediaAPI):
    def __init__(self, wiki_page, game_source = "normal"):
        super().__init__()

        import json
        from pathlib import Path
        
        main_folder = Path(__file__).parent.parent

        path_raw_games = main_folder / "video" / "data" / "games.json"
        path_pinpointed_games = main_folder / "video" / "data" / "pinpointed_games.json"

        if game_source == "normal":
            if path_raw_games.is_file():
                with open(path_raw_games, "r") as f:
                    self.raw_games = json.load(f)

                print(f"{path_raw_games.name} loaded!")

        elif game_source == "pinpointed":
            if path_pinpointed_games.is_file():
                with open(path_pinpointed_games, "r") as f:
                    self.raw_games = json.load(f)
                print(f"{path_pinpointed_games.name} loaded!")

        self.wiki_page = wiki_page

        self.raw_wiki = self.get_raw_wiki_text(self.wiki_page)

    def split_raw_wiki(self):
        return self.raw_wiki.split('\n')

    def grab_matchups_for_day(self, target_date):
        raw_wiki_split = self.split_raw_wiki()

        is_target_date = False

        naming_first_opponent = True
        opponent1, opponent2 = "", ""
        
        matchups_for_day = []

        for ind, row in enumerate(raw_wiki_split):
            date = get_date(row)
            if date:
                is_target_date = (date == target_date)

            if is_target_date:
                opponent = get_opponent(row)
                if opponent:
                    if naming_first_opponent:
                        opponent1 = opponent
                    else:
                        opponent2 = opponent
                    naming_first_opponent = not naming_first_opponent

                map = get_map(row)
                if map:
                    matchups_for_day.append((ind, opponent1, opponent2, map))

        return matchups_for_day
    
    def count_maps_for_day(self, target_date):
        count = 0

        days = self.raw_wiki.split("|date=")

        for day in days:
            if target_date in day:
                count += day.count('Map|map=')

        return count
    
    def sanity_check_before_insertion(self, matchups_for_day):
    
        num_matches_on_liquipedia = len(matchups_for_day)
        num_matches_on_vods = len(self.raw_games)

        if num_matches_on_liquipedia > num_matches_on_vods:
            num_missed = num_matches_on_liquipedia - num_matches_on_vods
            print(f"{num_missed} missing games from the VoD")

        elif num_matches_on_liquipedia < num_matches_on_vods:
            num_extra = num_matches_on_vods - num_matches_on_liquipedia
            print(f"{num_extra} superfluous games on the VoD")

        else:
            print("Perfect match on games!")

    def insert_links(self, vod_link, target_date):
        # with links = [(matchup, yt_link)]
        # with self.raw_games = [{'matchup': 'LiquidClem vs SKillous - [TLMC20] PERSEPHONE', 'players': ['LiquidClem', 'SKillous'], 'map_names': ['[TLMC20] PERSEPHONE']}, 7]

        import pyperclip
        
        raw_wiki_split = self.split_raw_wiki()

        matchups_for_day = self.grab_matchups_for_day(target_date)

        # Check if the number of matches on liquipedia and on the VoD match
        self.sanity_check_before_insertion(matchups_for_day)

        for liquipedia_matchup in matchups_for_day:
            ind_row_wiki, opponent1, opponent2, map_played = liquipedia_matchup
            # opponent1, opponent2 = liquipedia_to_game_name(opponent1), liquipedia_to_game_name(opponent2)
            found_match = False

            for starter_time, (game, quality_count) in self.raw_games.items():
                # fused_vod_matchup, yt_link = vod_matchup

                vod_link_timestamp = make_vod_link(vod_link, starter_time)

                if has_same_players_map(game, opponent1, opponent2, map_played):
                    row = raw_wiki_split[ind_row_wiki]
                    updated_row = add_vod_to_map(row, vod_link_timestamp)

                    raw_wiki_split[ind_row_wiki] = updated_row

                    del self.raw_games[starter_time]
                    # links.pop(ind_link)

                    found_match = True

                    break

            if not found_match:
                print(f"Could not find VoD for {opponent1} vs {opponent2} - {map_played}")

        for starter_time, (game, quality_count) in self.raw_games.items():
            vod_link_timestamp = make_vod_link(vod_link, starter_time)

            print(f'{game["matchup"]} did not find a match on liquipedia - {vod_link_timestamp}')

        wiki_with_links = "\n".join(raw_wiki_split)

        pyperclip.copy(wiki_with_links)

        return wiki_with_links




if __name__ == "__main__":
    wiki_page = "WardiTV_Spring_Championship/2025"
    wiki_pig6 = "PiG_Sty_Festival/6"
    wiki_wardi = "WardiTV_Mondays/33"

    lv = LiquipediaVods(wiki_wardi)
    date = "2025-04-28"

    vod = 'https://www.youtube.com/watch?v=-UFqr7fbsxE'

    lv.insert_links(vod, date)


    """from video_analysis import VideoTool
    vt = VideoTool()
    date = vt.upload_date"""

    # matchup_links = vt.make_matchup_links()

    # lv.insert_links(matchup_links, date)