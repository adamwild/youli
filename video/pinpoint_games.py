class PinpointGames():
    def __init__(self, m3u8_url, screen_configuration):
        import json
        from pathlib import Path
            
        video_folder = Path(__file__).parent
        self.video_folder = video_folder

        self.m3u8_url = m3u8_url
        self.screen_configuration = screen_configuration


        path_games = video_folder / "data" / "games.json"

        with open(path_games, "r") as f:
            self.games = json.load(f)

    def set_m3u8_url(self, m3u8_url):
        self.m3u8_url = m3u8_url

    def pinpoint(self, games = ""):
        """Gets the games starts closer to when they start being aired"""
        import os
        from multiprocessing import Pool
        from itertools import repeat
        

        if games:
            self.games = games

        # is_game_frame(m3u8_url, frame_in_seconds, screen_configuration)

        pairs = [(int(game_start) - 10, int(game_start) + 60) for game_start in self.games.keys()]

        args = list(zip(pairs, repeat(self.m3u8_url), repeat(self.screen_configuration)))

        with Pool() as pool:
            pinpointed_game_starts = pool.map(binary_search_threshold, args)

        pinpointed_games = {}

        for game_start, pinpointed_game_start in zip(self.games.keys(), pinpointed_game_starts):
            if pinpointed_game_start is None:
                pinpointed_games[game_start] = self.games[game_start]
            else:
                pinpointed_games[str(pinpointed_game_start-2)] = self.games[game_start]

        self.pinpointed_games = pinpointed_games
        
        self.save()

    def first_frame_from_timers(self):
        """Finds the """

    def save(self):
        import json

        path_pted_games = self.video_folder / "data" / "pinpointed_games.json"

        with open(path_pted_games, "w") as f:
            json.dump(self.pinpointed_games, f, indent=4)


def binary_search_threshold(args):
    from video.video_utils import is_game_frame

    pair, m3u8_url, screen_configuration = args

    a, b = pair
    left, right = a + 1, b
    threshold = None
    while left <= right:
        mid = (left + right) // 2
        if is_game_frame(m3u8_url, mid, screen_configuration):
            threshold = mid
            right = mid - 1
        else:
            left = mid + 1
    return threshold

if __name__ == "__main__":
    # Example:
    vod_twitch = "https://www.twitch.tv/videos/2430096036"
    vod_soop = "https://vod.sooplive.co.kr/player/158381047"
    vod_yt = 'https://www.youtube.com/watch?v=-UFqr7fbsxE'

    vod_pig = "https://www.twitch.tv/videos/2444811242"

    vod = 'https://www.youtube.com/watch?v=-UFqr7fbsxE'

    from video.video_utils import get_m3u8
    from video.screen_config import WardiTV_yt_coordinates
    m3u8 = get_m3u8(vod)

    pg = PinpointGames(m3u8, WardiTV_yt_coordinates)

    pg.pinpoint()

