# Youli

## Description

**Youli** is a command-line interface (CLI) tool for keeping Liquipedia pages up to date with the latest VoDs of matches.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [License](#license)
- [Contact](#contact)

## Installation

Clone the project, activate your virtual environment and install the required dependencies.

```bash
pip install -r requirements.txt
```

**Youli** relies on several APIs to function. Logically, if you want to interact with different websites and video providers, you will need to setup your API keys.
For that go to `OPEN_ME.py` and add your secrets. Rename the file to `config.py` once finished.

You also need to have [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed with the correct path in your `config.py`.

## Usage

### Detect and timestamp game starts from long VoDs

This pipeline invokes the `VideoPipeline` class from the `video_pipeline.py` file. It performs the following steps:
- Captures one frame every 60 seconds from the video source.
- Applies OCR to each frame to detect game information such as player names, in-game timer, and map name. (see `youli/video/data_example/info_frames.json`)
- Uses the detected game frames and in-game timer to estimate possible game start times. 
- Identifies the most likely game starts based on the number of frames supporting each timestamp. (see `youli/video/data_example/games.json`)
- Using the player’s names, map name, and game date, we match each detected game to its corresponding Liquipedia entry.
- Copies the updated Liquipedia page content to the clipboard via `pyperclip`, allowing the user to paste it manually into the wiki.

```bash
# Extract frames from <video_url> using <screen_configuration>. 
# Uses OCR to detect and timestamp all games, then inserts them into <liquipedia_page>.
# All games must occur on the same day. You can specify the target day with <YYYY-MM-DD>, or leave it empty to use today's date.
lp -vp <screen_configuration> <video_url> <liquipedia_page> <YYYY-MM-DD>
```

For instance, this [revision](https://liquipedia.net/starcraft2/index.php?title=WardiTV_May&diff=prev&oldid=2583216) was yielded by using this command:

```bash
lp -vp wardi https://www.youtube.com/watch?v=FU05ayGxRNA WardiTV_May
```

### Track Vods uploaded by multiple content creators from multiple sources

Using the YouTube and Twitch APIs, this pipeline tracks the latest videos uploaded by content creators. It labels the corresponding Liquipedia pages for each video and presents the user with an interactive menu to insert these links with just a few clicks.

```bash
# Fetch all new videos from the different sources
lp -f

# Presents the user with an interactive prompting system to complete missing Liquipedia pages entries
lp -ww

# Interactive menu to insert links for each Liquipedia page
lp -uw
```

A little demo, which made this [revision](https://liquipedia.net/starcraft2/index.php?title=PiG_Sty_Festival/6&diff=prev&oldid=2580247)

![Demo](https://github.com/adamwild/open-data/blob/main/ochef/demo_vods.gif)

For adding new content creators, see the following examples `youli/organizers/<caster_or_orga>/<caster_or_orga>_channels.py`.
After adding a new content creator, update the `VodsToWiki` in `vods_to_wiki`.

## Dependencies

This project uses [Tesseract OCR](https://github.com/tesseract-ocr/tesseract), which is licensed under the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0).

- Tesseract OCR (version 5.5.0)
  - License: Apache License 2.0
  - See [LICENSE](LICENSE) for more details.