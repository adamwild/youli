class FrameAnalyzer():
    def __init__(self, screen_configuration, reset = True, sampling = 60, threshold_quality = 2):
        from pathlib import Path
        
        video_folder = Path(__file__).parent

        self.frames_folder = video_folder / "frames"
        self.data_folder = video_folder / "data"

        self.data_folder.mkdir(parents=True, exist_ok=True)

        if reset:
            self.reset()

        self.screen_configuration = screen_configuration
        self.sampling = sampling
        self.threshold_quality = threshold_quality

        self.get_frames()

    def get_frames(self):
        frames = [f for f in self.frames_folder.iterdir() if f.is_file()]
        frames_seconds = [int(frame.name.split('_')[1].split('.')[0]) * self.sampling for frame in frames]
        
        self.frames = frames
        self.frames_seconds = frames_seconds

    def save_checkpoint(self, data, name_data):
        import json

        path_save = (self.data_folder / name_data).with_suffix(".json")

        with open(path_save, "w") as f:
            json.dump(data, f, indent=4)

    def load_checkpoint(self, name_data):
        import json

        path_load = (self.data_folder / name_data).with_suffix(".json")

        with open(path_load, "r") as f:
            data = json.load(f)

        return data
    
    def reset(self):
        # Delete all checkpoints
        checkpoints = [f for f in self.data_folder.iterdir() if f.is_file() and f.name.endswith('.json')]
        for checkpoint in checkpoints:
            checkpoint.unlink()

    def get_info_frames(self):
        from itertools import repeat
        from multiprocessing import Pool
        from video.video_utils import extract_info_frame

        frame_numbers = [frame.name.split("_")[1][:4] for frame in self.frames]
        args_list = list(zip(self.frames, frame_numbers, self.frames_seconds, repeat(self.screen_configuration)))
        total_frames = len(args_list)

        results = []
        with Pool() as pool:
            for idx, result in enumerate(pool.imap_unordered(extract_info_frame, args_list), 1):
                results.append(result)
                print(f"\rFrames analyzed - {idx}/{total_frames}", end='', flush=True)

        results.sort(key=lambda frame_info: frame_info['frame_seconds'])

        print()
        self.save_checkpoint(results, "info_frames")
        return results
    
    def identify_games(self):

        def update_match_info(match_info, player1, player2, map_name):
            for player in [player1, player2]:
                if player not in match_info['players']:
                    match_info['players'].append(player)
            if map_name not in match_info['map_names']:
                    match_info['map_names'].append(map_name)

            return match_info
        
        info_frames = self.load_checkpoint("info_frames")

        matches = {}

        for frame_num, frame_info in enumerate(info_frames):

            # If a frame is from a stream break, don't take it into account
            if "brb" in frame_info and frame_info['brb']:
                continue

            player1, player2, map_name = frame_info['player1'], frame_info['player2'], frame_info['map_name'],

            if "start" in frame_info:

                # Get starter time, if within 5 sec, merge with existing starter time
                starter_time = frame_info['start']
                for key in matches.keys():
                    if abs(int(key) - int(frame_info['start'])) < 6:
                        starter_time = key
                        break

                if starter_time not in matches:
                    matchup = f"{player1} vs {player2} - {map_name}"
                    match_info = {"matchup": matchup, "players": [player1, player2], "map_names": [map_name]}
                    matches[starter_time] = [match_info, 1]
                else:
                    matches[starter_time][1] += 1
                    match_info = matches[starter_time][0]

                    match_info = update_match_info(match_info, player1, player2, map_name)
                    if map_name not in matches[starter_time][0]:
                        matches[starter_time][0] = match_info

        sorted_games = self.sort_games_by_quality(matches)

        self.save_checkpoint(sorted_games, "games")

    def sort_games_by_quality(self, matches, threshold_quality = ""):
        if threshold_quality:
            self.threshold_quality = threshold_quality

        sorted_games = {}

        high_quality, low_quality = [], []
        for starter_time, (_, quality_count) in matches.items():
            if quality_count <= self.threshold_quality:
                low_quality.append(starter_time)
            else:
                high_quality.append(starter_time)

        for starter_time in high_quality + low_quality:
            sorted_games[starter_time] = matches[starter_time]

        return sorted_games



if __name__ == "__main__":
    from video.screen_config import WardiTV_yt_coordinates, PiG_twitch_coordinates

    fa = FrameAnalyzer(WardiTV_yt_coordinates)
    fa.get_info_frames()
    fa.identify_games()