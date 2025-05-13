class VideoPipeline():
    def __init__(self, video_link, screen_config, wiki_page, target_date = "today", name_pipeline = "", game_source="normal"):
        from pathlib import Path
        from datetime import date

        main_folder = Path(__file__).parent

        self.pipeline_info_folder = main_folder / "video" / "pipelines"
        self.pipeline_info_folder.mkdir(parents=True, exist_ok=True)

        self.wiki_page = wiki_page
        self.video_link = video_link
        self.screen_config = screen_config

        self.m3u8_url = ""
        self.name_pipeline = name_pipeline
        self.get_path_pipeline()
        self.game_source = game_source

        if target_date == "today":
            self.target_date = date.today().isoformat()
        else:
            self.target_date = target_date

        self.is_new_pipeline = self.is_new_pipeline()
        if self.is_new_pipeline:
            self.info_pipeline = self.make_info_pipeline()
            self.save_pipeline()
        else:
            self.info_pipeline = self.load_pipeline()

    def make_info_pipeline(self):
        info_pipeline = {}

        info_pipeline['name_pipeline'] = self.name_pipeline
        info_pipeline['target_date'] = self.target_date
        info_pipeline['wiki_page'] = self.wiki_page
        info_pipeline['video_link'] = self.video_link
        
        if self.m3u8_url:
            info_pipeline['m3u8_url'] = self.m3u8_url

        return info_pipeline

    def get_path_pipeline(self):
        if not self.name_pipeline:
            name_pipeline = "curr_pipeline.json"

        path_pipeline = self.pipeline_info_folder / name_pipeline
        self.path_pipeline = path_pipeline
        
        return path_pipeline

    def save_pipeline(self):
        import json

        path_pipeline = self.get_path_pipeline()
        info_pipeline = self.make_info_pipeline()

        with open(path_pipeline, "w") as f:
            json.dump(info_pipeline, f, indent=4)

    def load_pipeline(self):
        import json

        path_pipeline = self.get_path_pipeline()

        with open(path_pipeline, "r") as f:
            info_pipeline = json.load(f)

        return info_pipeline
    
    def is_new_pipeline(self):
        if not self.path_pipeline.is_file():
            return True
        
        prev_info_pipeline = self.load_pipeline()
        curr_info_pipeline = self.make_info_pipeline()

        is_new_pipeline = any([prev_info_pipeline[key] != curr_info_pipeline[key] for key in curr_info_pipeline.keys()])

        return is_new_pipeline


    def vod_to_wiki(self):
        from video.frame_extraction import FrameExtractor
        from video.frame_analysis import FrameAnalyzer
        from video.pinpoint_games import PinpointGames
        from utils.liquipedia_vods import LiquipediaVods

        # Extract frames from the vod, stored under ./video/frames/
        # FrameExtractor gets the m3u8_url and gets all the frames
        if 'm3u8_url' in self.info_pipeline:
            m3u8_url = self.info_pipeline['m3u8_url']
        else:
            m3u8_url = ""
        frame_extractor = FrameExtractor(self.video_link, reset = self.is_new_pipeline, m3u8_url = m3u8_url)
        self.save_pipeline()
        
        if not frame_extractor.has_all_frames():
            frame_extractor.reset()
            frame_extractor.frame_extraction()

        self.m3u8_url = frame_extractor.get_m3u8_url()
        self.save_pipeline()

        # Apply OCR to the frames to build possible games
        # Creates ./video/data/info_frames.json and ./video/data/games.json
        frame_analyzer = FrameAnalyzer(self.screen_config, reset = self.is_new_pipeline)
        frame_analyzer.get_info_frames()
        frame_analyzer.identify_games()

        # Uses binary search to pinpoint when a game is first shown on screen
        if self.game_source == "pinpoint":
            pinpoint_games = PinpointGames(self.m3u8_url, self.screen_config)
            pinpoint_games.pinpoint()

        # Inserts the game urls into the wikipedia page
        # Autocopies to the system clipboard
        liquipedia_vods = LiquipediaVods(self.wiki_page, game_source=self.game_source)
        liquipedia_vods.insert_links(self.video_link, self.target_date)





if __name__ == "__main__":
    from video.screen_config import WardiTV_yt_coordinates, PiG_twitch_coordinates

    vod_pig = "https://www.twitch.tv/videos/2452117289"
    wiki_pig6 = "PiG_Sty_Festival/6"
    wiki_pigauso = "PiGosaur_Monday/30"

    vod_wardi = "https://www.youtube.com/watch?v=FU05ayGxRNA"
    wiki_wardi = "WardiTV_Mondays/35"
    wiki_wardi_may = 'WardiTV_May'

    vod_gsl = "https://www.youtube.com/watch?v=4fGLV9125AI"
    wiki_gsl = "Global_StarCraft_II_League/2025/Season_1"

    # vp = VideoPipeline(vod_pig, PiG_twitch_coordinates, wiki_pigauso, target_date = "today")
    # vp = VideoPipeline(vod_wardi, WardiTV_yt_coordinates, wiki_wardi, target_date = "today")

    # Should work with "lp -vp wardi https://www.youtube.com/watch?v=FU05ayGxRNA WardiTV_May"
    vp = VideoPipeline(vod_wardi, WardiTV_yt_coordinates, wiki_wardi_may, target_date = "today")


    vp.vod_to_wiki()
    