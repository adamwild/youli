def title_to_wiki(video_title, publishedAt, description, tournament_name, wiki_page):
    if tournament_name in video_title:
        return wiki_page
    return ""

def title_number_to_wiki(video_title, publishedAt, description, tournament_name, wiki_page):
    if tournament_name in video_title:
        number = video_title.split(tournament_name)[1].strip().split(' ')[0]
        return f'{wiki_page}/{number}'
    return ""
