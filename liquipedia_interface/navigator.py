class Navigator():
    def __init__(self, wiki_page):
        from utils.api_liquipedia import LiquipediaAPI

        self.api = LiquipediaAPI()

        self.wiki_page = wiki_page
        self.raw_wiki = self.api.get_raw_wiki_text(wiki_page)

        self.split_wiki = self.raw_wiki.split('\n')

    def gather_games(self):
        """Gather games while keeping the general structure of the page
        example output: {'Playoffs': [('Serral - Dark', <ind_vod_insertion>), ...]}
        """
        games = {}
        flag_game = False
        for ind, row in enumerate(self.split_wiki):
            if row.startswith('==={{Stage|'):
                curr_stage = row.split('|')[1].split('}')[0]
                curr_group = ''

            elif row.startswith('===={{HiddenSort|'):
                curr_group = row.split('|')[1].split('}')[0]
            
            if "opponent1=" in row:
                flag_game = True
                oppo1 = row.split('|')[2].split('}')[0].replace("1=", "")

            elif "opponent2=" in row:
                oppo2 = row.split('|')[2].split('}')[0].replace("1=", "")

            elif row.strip() == '}}' and flag_game:
                flag_game = False
                groupstage = curr_stage
                if curr_group:
                    groupstage += ' - ' + curr_group

                curr_game = (f'{oppo1} vs {oppo2}', ind-1)
                if groupstage not in games:
                    games[groupstage] = [curr_game]
                else:
                    games[groupstage].append(curr_game)
            
        return games


if __name__ == "__main__":

    wiki_pig = "PiG_Sty_Festival/6"
    wiki_gsl = 'Global_StarCraft_II_League/2025/Season_1'
    nav = Navigator(wiki_pig)

    games = nav.gather_games()
    for groupstage, game in games.items():
        print(groupstage, game)
