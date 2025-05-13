def make_HH_MM_SS_timestamp(time_seconds):
    minutes, seconds = time_seconds // 60, time_seconds % 60

    timestamp = f"{minutes // 60:02d}:{minutes % 60:02d}:{seconds:02d}"

    return timestamp

def get_frame_from_m3u8(args):
    """Extract a single frame """
    import subprocess

    num_frame_to_get, m3u8_url, frames_folder, sampling = args

    frame_in_seconds = sampling*num_frame_to_get

    timestamp = make_HH_MM_SS_timestamp(frame_in_seconds)
    output_path = f"{frames_folder}/frame_{num_frame_to_get:04d}.jpg"

    subprocess.run([
        "ffmpeg",
        "-ss", timestamp,
        "-i", m3u8_url,
        "-frames:v", "1",
        "-q:v", "2",
        "-loglevel", "error",
        output_path
    ])

def get_PIL_image_from_m3u8(m3u8_url, frame_in_seconds):
    """Loads a frame from a video directly, without storing it"""
    import subprocess
    from PIL import Image
    import io

    timestamp = make_HH_MM_SS_timestamp(frame_in_seconds)

    result = subprocess.run(
        [
            "ffmpeg",
            "-ss", timestamp,
            "-i", m3u8_url,
            "-frames:v", "1",
            "-q:v", "2",
            "-f", "image2",
            "-vcodec", "mjpeg",
            "-loglevel", "error",
            "pipe:1"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode != 0 or not result.stdout:
        raise RuntimeError(f"FFmpeg failed: {result.stderr.decode()}")

    return Image.open(io.BytesIO(result.stdout))

def is_game_frame(m3u8_url, frame_in_seconds, screen_configuration):
    frame = get_PIL_image_from_m3u8(m3u8_url, frame_in_seconds)

    args = frame, 'frame_number', frame_in_seconds, screen_configuration
    frame_info = extract_info_frame(args)

    is_frame_from_break = "brb" in frame_info and frame_info['brb']
    is_game_frame = 'start' in frame_info

    if is_game_frame and not is_frame_from_break:
        return True

    return False

def get_m3u8_duration(m3u8_url):
    import subprocess

    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        m3u8_url
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    duration_seconds = float(result.stdout.strip())
    return duration_seconds

# m3u8 getter functions
# add new functions to FrameExtractor init
def get_m3u8_youtube(youtube_video):
    import subprocess
    
    result = subprocess.run(["yt-dlp", "-g", youtube_video], capture_output=True, text=True)
    return result.stdout.strip().split('\n')[0]

def get_m3u8_twitch(twitch_vod_url):
    import streamlink

    streams = streamlink.streams(twitch_vod_url)
    best_stream = streams['best']
    return best_stream.url

def get_m3u8(video_url):
    if 'youtube' in video_url:
        return get_m3u8_youtube(video_url)
    
    if 'twitch' in video_url:
        return get_m3u8_twitch(video_url)



def extract_text(image):
    import pytesseract
    from config import PATH_TESSERACT

    pytesseract.pytesseract.tesseract_cmd = PATH_TESSERACT
    extracted_text = pytesseract.image_to_string(image)

    return extracted_text

def load_image(image_or_path):
    from PIL import Image

    from pathlib import Path
    if isinstance(image_or_path, Path):
        # image_or_path is a path to an image
        frame = Image.open(image_or_path)
    else:
        # image_or_path is an image
        frame = image_or_path

    return frame

def extract_info_frame(args):

    image_or_path, frame_number, frame_seconds, screen_configuration = args

    frame = load_image(image_or_path)

    frame_info = {}

    frame_info['frame_number'] = frame_number
    frame_info['frame_seconds'] = frame_seconds
    
    # Extract timer, player 1, player 2 and map name from the screen
    for name_coord, coord in screen_configuration.items():
        cropped_image = frame.crop(coord)

        frame_info[name_coord] = extract_text(cropped_image).strip()

    def only_digits(value):
        import re
        candidate = re.sub(r'\D', '', str(value))

        if candidate:
            return int(candidate)
        return 0

    # Compute additional info
    if ":" in frame_info['timer']:
        split_timer = frame_info['timer'].split(':')
        if len(split_timer)==2:
            min, sec = split_timer
            min, sec = only_digits(min), only_digits(sec)
            frame_info['min'], frame_info['sec'] = min, sec
            frame_info['gametime'] = 60*min + sec
            frame_info['start'] = str(frame_seconds - int((1/1.0167) * (60*min + sec)))

    return frame_info




if __name__ == "__main__":
    # Example:
    vod_url = "https://www.twitch.tv/videos/2430096036"
    vod_soop = "https://vod.sooplive.co.kr/player/158381047"
    vod_yt = 'https://www.youtube.com/watch?v=iTTHdCyvmPk'

    # m3u8_url = get_m3u8_twitch(vod_soop)
    m3u8_url = get_m3u8_youtube(vod_yt)
    print(m3u8_url)

