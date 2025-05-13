class FrameExtractor():
    def __init__(self, video_link, reset = True, sampling = 60, m3u8_url = ""):
        from pathlib import Path
        from video.video_utils import get_m3u8_youtube, get_m3u8_twitch
        
        video_folder = Path(__file__).parent

        self.frames_folder = video_folder / "frames"
        self.frames_folder.mkdir(parents=True, exist_ok=True)

        self.video_link = video_link

        self.possible_sources = ["youtube", "twitch"]
        self.m3u8_getter_functions = [get_m3u8_youtube, get_m3u8_twitch]

        # Take a frame every self.sampling seconds
        self.sampling = sampling

        self.source_video = self.get_source_video()

        self.m3u8_url = m3u8_url
        self.duration = ""

        if reset:
            self.reset()

    def can_use_m3u8(self):
        return True
        
    def get_source_video(self):
        for possible_source in self.possible_sources:
            if possible_source in self.video_link:

                return possible_source
            
    def get_m3u8_getter_function(self):
        for possible_source, getter_function in zip(self.possible_sources, self.m3u8_getter_functions):
            if possible_source == self.source_video:

                return getter_function
            
    def get_m3u8_url(self):
        if self.m3u8_url:
            return self.m3u8_url
        
        m3u8_getter_function = self.get_m3u8_getter_function()
        m3u8_url = m3u8_getter_function(self.video_link)

        self.m3u8_url = m3u8_url

        return m3u8_url
    
    def get_duration(self):
        from video.video_utils import get_m3u8_duration
        if self.duration:
            return self.duration

        if not self.m3u8_url and self.can_use_m3u8():
            self.get_m3u8_url()

        if self.m3u8_url:
            self.duration = get_m3u8_duration(self.m3u8_url)
            return self.duration
    
    def frame_extraction(self):
        from multiprocessing import Pool
        from video.video_utils import get_frame_from_m3u8

        m3u8_url = self.get_m3u8_url()

        duration_sec = self.get_duration()
        num_frames_to_get = int(duration_sec // self.sampling)

        args_list = [(num_frame_to_get, m3u8_url, self.frames_folder, self.sampling) for num_frame_to_get in range(num_frames_to_get)]

        total = len(args_list)
        with Pool() as pool:
            for idx, _ in enumerate(pool.imap_unordered(get_frame_from_m3u8, args_list), 1):
                print(f"\rFrames extracted - {idx}/{total}", end='', flush=True)
                
        print()

    def get_frames(self):
        frames = [f for f in self.frames_folder.iterdir() if f.is_file()]
        return frames

    def has_all_frames(self):
        frames = self.get_frames()
        self.get_duration()
        if self.duration == 0:
            raise IOError("Video has duration of 0s")
        
        return len(frames) == self.duration // self.sampling

    def reset(self):
        # Delete all frames taken
        frames = self.get_frames()
        for frame in frames:
            frame.unlink()

if __name__ == "__main__":
    # Example:
    vod_twitch = "https://www.twitch.tv/videos/2430096036"
    vod_soop = "https://vod.sooplive.co.kr/player/158381047"
    vod_yt = 'https://www.youtube.com/watch?v=-UFqr7fbsxE'

    vod_pig = "https://www.twitch.tv/videos/2444811242"

    yt_pig = "https://www.youtube.com/watch?v=h9cd-oy_wbk"



    fe = FrameExtractor(vod_yt)
    fe.frame_extraction()

    print(fe.has_all_frames())
        
    
