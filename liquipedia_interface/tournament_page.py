"""Class responsible with taking a wiki_page, idenitfying the games and managing vod links"""

class TournamentPage():
    def __init__(self, wiki_page):
        from utils.api_liquipedia import LiquipediaAPI

        self.api = LiquipediaAPI()
        self.wiki_page = wiki_page
        self.raw_wiki = self.api.get_raw_wiki_text(wiki_page)

        # Allows to access the matches directly
        self.list_matches = []

        self.split_wiki = self.raw_wiki.split('\n')

        self.broken_down_page = self.break_down_wiki()
        self.structure_matches()
        self.contexts = list(self.structured_matches.keys())

        

    def break_down_wiki(self):
        """Break down the wiki page into a list [text_part, game1, game2, ...]
        With text_part being just a string of the wiki containing no games
        and game# being a Game object"""
        from liquipedia_interface.match import Match
        match_flag = False
        left_curly, right_curly = 0, 0
        broken_down_page = []
        curr_stage, curr_group = '', ''
        curr_text = []

        def update_left_right_curly_count(left_curly, right_curly, row):
            left_curly += row.count('{')
            right_curly += row.count('}')
            return left_curly, right_curly 
        
        for ind, row in enumerate(self.split_wiki):
            # If the liquipedia page has them, grab the part names (stage and group)
            if row.strip().startswith('==={{Stage|'):
                curr_stage = row.split('|')[1].split('}')[0]
                curr_group = ''

            elif row.strip().startswith('===={{HiddenSort|'):
                curr_group = row.split('|')[1].split('}')[0]


            # If a match is detected, count curly braces, when they even out, the full match is parsed
            if "{{Match" in row and not "Matchlist" in row:
                match_flag = True
                left_curly, right_curly = update_left_right_curly_count(left_curly, right_curly, row)
                curr_match = [row]

                if curr_text:
                    broken_down_page.append("\n".join(curr_text))
                    curr_text = []

            elif match_flag:
                left_curly, right_curly = update_left_right_curly_count(left_curly, right_curly, row)
                curr_match.append(row)

                # The full match is parsed
                if left_curly == right_curly:
                    match_flag = False
                    match_obj = Match(curr_match, curr_stage, curr_group)
                    broken_down_page.append(match_obj)
                    self.list_matches.append(match_obj)


            else:
                curr_text.append(row)

        if curr_text:
            broken_down_page.append("\n".join(curr_text))

        return broken_down_page
    
    def structure_matches(self):
        """Creates a dictionnary with {match.context : [<matches_that_have_the_same_context, ...], ...}"""
        structured_matches = {}

        for match in self.list_matches:
            if match.context not in structured_matches:
                structured_matches[match.context] = [match]
            else:
                structured_matches[match.context].append(match)

        self.structured_matches = structured_matches

    def pp_menu_contexts(self):
        from liquipedia_interface.menu_utils import number_to_key
        for ind, context in enumerate(self.structured_matches.keys()):
            matches_for_context = str([match.matchup_name for match in self.structured_matches[context][:5]])

            proper_key = number_to_key(ind+1)
            print(f"{proper_key}. {context} - {matches_for_context}")

            print()

    def pp_menu_matches(self, context):
        from liquipedia_interface.menu_utils import number_to_key
        print(context)
        for ind, match in enumerate(self.structured_matches[context]):
            proper_key = number_to_key(ind+1)
            print(f"\t{proper_key}. {match.matchup_name}")

        print()

    def copy(self):
        import pyperclip
        pyperclip.copy(str(self))

        print(f"cp - {self.wiki_page}")
    
    def __str__(self):
        return "\n".join([str(elt) if not isinstance(elt, str) else elt for elt in self.broken_down_page])


if __name__ == "__main__":
    wiki_page = 'PiG_Sty_Festival/6'
    wiki_quali = 'PiG_Sty_Festival/6/Qualifier_2'

    tp = TournamentPage(wiki_page)
    # tp.break_down_wiki()
    # tp.pp_menu_contexts()