# Handles updating tracked channels, asks the user the complete missing data (vods without a clear wiki page)
# Handles menuing to dispatch the vods onto the different liquipedia pages

class VodsToWiki():
    def __init__(self):
        from organizers.pig.pig_channels import PigVods
        from organizers.wardi.wardi_channels import WardiVods
        from organizers.gsl.gsl_channels import GlobalStarcraftLeagueVods

        self.organizers = [PigVods(), WardiVods(), GlobalStarcraftLeagueVods()]

    def fetch_new_vods(self):
        """Check new videos uploaded on all channels, update fused_channels_info.csv for all organizers"""
        for organizer in self.organizers:
            # For each channel, update the local table with new videos
            organizer.update_tracked_channels()

            # Fuse local tables and update the main table containing all the vods for a given content creator / tournament organizer
            organizer.update_fused_info()

    def complete_tables_wiki(self):
        """For all fused_channels_info.csv, ask the user to complete the 'wiki_page' column for missing entries"""
        for organizer in self.organizers:
            organizer.assign_wiki_pages_manual()

    def update_wikis(self):
        """Goes through each (website, vod, wiki_page), asks the user where to add them on the liquipedia page"""
        from liquipedia_interface.tournament_menu import TournamentMenu

        for organizer in self.organizers:
            list_df_to_insert = organizer.get_list_df_to_insert()

            for df_to_insert in list_df_to_insert:
                curr_wiki = df_to_insert['wiki_page'].iloc[0]

                vods = zip(list(df_to_insert['video_title']), list(df_to_insert['url']))

                tm = TournamentMenu(curr_wiki)

                tm.interactive_link_insertion(vods)

                tm.copy()

                input("Proceed to next Liquipedia page?")

                organizer.mark_df_as_inserted(df_to_insert)

if __name__ == "__main__":
    vods_to_wiki = VodsToWiki()

    # vods_to_wiki.fetch_new_vods()
    # vods_to_wiki.complete_tables_wiki()
    vods_to_wiki.update_wikis()