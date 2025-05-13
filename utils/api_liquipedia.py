class LiquipediaAPI():
    def __init__(self):
        from config import HEADER_LIQUIPEDIA
        self.time_to_wait = 0
    
        self.url = "https://liquipedia.net/starcraft2/api.php"
        self.headers = HEADER_LIQUIPEDIA

        self.cache_page = {}

    def wait(self, time_between_request=2):
        import time
        time.sleep(time_between_request)

    def get_page(self, player):
        import requests

        self.wait(self.time_to_wait)

        params = {
            "action": "opensearch",
            "format": "json",
            "search": player,
            "limit": 5
        }

        response = requests.get(self.url, params=params, headers=self.headers)
        json = response.json()

        self.time_to_wait = 2

        # No player with the name exists
        if not json[1]:
            return ""
        
        candidate_pages = [page for page in json[1] if "/" not in page]
        
        if len(candidate_pages) != 1:
            return candidate_pages

        # return json[1][0]
        return candidate_pages[0]
    
    def get_raw_wiki_text(self, page):
        import requests

        if page in self.cache_page:
            return self.cache_page[page]

        self.wait(self.time_to_wait)

        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": page,
            "rvslots": "main",
            "rvprop": "content"
        }

        response = requests.get(self.url, params=params, headers=self.headers)
        data = response.json()

        # Extract the raw wikitext
        raw_wiki = ""

        pages = data["query"]["pages"]
        for page_id in pages:
            content = pages[page_id]["revisions"][0]["slots"]["main"]["*"]
            raw_wiki += content

        self.time_to_wait = 2

        self.cache_page[page] = raw_wiki

        return raw_wiki
    
    def extract_info_raw_wiki(self, raw_wiki):
        id = raw_wiki.split('|id=')[1].split('\n')[0]
        race = raw_wiki.split('|race=')[1].split('\n')[0]

        def parse_race(race):
            if race.lower() == "z":
                return "Zerg"
            elif race.lower() == "p":
                return "Protoss"
            elif race.lower() == "t":
                return "Terran"
            return race

        return id, parse_race(race)
    
    def extract_info_from_player(self, player):
        page = self.get_page(player)

        if not page:
            return (player, "")
        if type(page) is list:
            return (str(page), "")
        
        raw_wiki = self.get_raw_wiki_text(page)

        return self.extract_info_raw_wiki(raw_wiki)
    
    def get_list_first_player(self, bbb_number):
        page_name = f"Basilisk_Big_Brain_Bouts/{bbb_number}"
        raw_page_bbb = self.get_raw_wiki_text(page_name)

        p1, p3, p5, p7 = [raw_page_bbb.split(f'|p{num}=')[1].split('\n')[0].split('|')[0] for num in [1, 3, 5, 7]]

        return p1, p3, p5, p7
    


if __name__ == "__main__":
    api = LiquipediaAPI()
    api.get_list_first_player(49)
