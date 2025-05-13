def is_from_playlist(video_title, publishedAt, description, wiki_playlist):
    return wiki_playlist

def is_pig6(video_title, publishedAt, description):
    if 'PiGFest 6.0' in video_title:
        return 'PiG_Sty_Festival/6'
    return ""