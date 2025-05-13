"""Class responsible for a single match, insert vod, remove them ..."""

class Match():
    def __init__(self, match, stage, group):
        """match is a list of strings
        stage and group can be non-empty strings"""

        self.match = match
        self.stage = stage
        self.group = group

        self.scan()
        self.get_matchup_name()
        self.get_context_name()

    def insert_vod(self, vod_url = 'youtube.com/some_url'):
        """Update the row starting with |vod=, if it does not exist, insert the vod link at the end of the match description"""
        indent = '    '
        
        for ind, row in enumerate(self.match):
            if row.strip().startswith("|map"):
                indent = row.split('|')[0]

            if row.strip().startswith("|vod="):
                self.match[ind] = indent + '|vod=' + vod_url
                return
            
        self.match.insert(-1, indent + '|vod=' + vod_url)

    def scan(self):
        """Scan itself to identify the opponents"""
        for row in self.match:
            if "opponent1=" in row:
                self.oppo1 = row.split('|')[2].split('}')[0].replace("1=", "")

            elif "opponent2=" in row:
                self.oppo2 = row.split('|')[2].split('}')[0].replace("1=", "")

    def get_matchup_name(self):
        self.matchup_name = f'{self.oppo1} vs {self.oppo2}'

    def get_context_name(self):
        context = self.stage
        if context and self.group:
            context += ' - ' + self.group
        elif self.group:
            context = self.group

        if not context:
            context = "None"
        self.context = context

    def delete_vods(self, website_to_remove = "", specific_vod_to_remove = ""):
        """Deletes all previous vods
        Delete vods from website_to_remove, delete all vods if no website_to_remove
        specific_vod_to_remove = 'only_maps', 'only_full_vod, default is empty -> deletes all'"""
        for ind, row in enumerate(self.match):
            is_map = row.strip().startswith("|map")

            if "|vod=" in row:
                if website_to_remove not in row:
                    continue

                row_split = row.split('|vod=')

                if is_map and (specific_vod_to_remove == 'only_maps' or not specific_vod_to_remove):
                    self.match[ind] = row_split[0] + "}}"

                elif not is_map and (specific_vod_to_remove == 'only_full_vod' or not specific_vod_to_remove):
                    self.match[ind] = row_split[0] + '|vod='

    def __str__(self):
        return '\n'.join(self.match)