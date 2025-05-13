import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "-vp",
    "--video_pipeline",
    nargs="+",
    help="From a full video stream, extract all games, inserts them into a Liquipedia page",
)

parser.add_argument("-f", "--fetch_channels", help="For all organizers, updates the tables of vods for each channel", action="store_true")
parser.add_argument("-ww", "--write_wikis", help="Manually enter the Liquipedia pages from missing entries", action="store_true")
parser.add_argument("-uw", "--update_wikis", help="Goes through each Liquipedia page with uninserted vods, asks the user how to insert them", action="store_true")

from pathlib import Path

liquipedia_folder = str(Path(__file__).parent)

os.chdir(liquipedia_folder)

verbose = True

args = parser.parse_args()

from vods_to_wiki import VodsToWiki
from video_pipeline import VideoPipeline
from video.screen_config import WardiTV_yt_coordinates, PiG_twitch_coordinates

if __name__ == "__main__":
    if args.video_pipeline:
        screen_configuration, video_url, liquipedia_page = args.video_pipeline[0:3]
        optional_date = args.video_pipeline[3] if len(args.video_pipeline) == 4 else "today"

        if screen_configuration == 'pig':
            coordinates = PiG_twitch_coordinates

        elif screen_configuration == 'wardi':
            coordinates = WardiTV_yt_coordinates

        vp = VideoPipeline(video_url, coordinates, liquipedia_page, target_date = optional_date)

        vp.vod_to_wiki()

    elif args.fetch_channels:
        vods_to_wiki = VodsToWiki()

        vods_to_wiki.fetch_new_vods()

    elif args.write_wikis:
        vods_to_wiki = VodsToWiki()

        vods_to_wiki.complete_tables_wiki()

    elif args.update_wikis:
        vods_to_wiki = VodsToWiki()

        vods_to_wiki.update_wikis()
