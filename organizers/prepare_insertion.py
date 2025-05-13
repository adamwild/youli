# Prepares fused video info of all channels for a given organizer
# Does the proper data preparation and handling

from organizers.multi_platform_vods import MultiPlatformVODs

class InsertionPreparator(MultiPlatformVODs):
    def __init__(self, list_link_channels):
        super().__init__(list_link_channels)

    def is_wiki_known_for_all(self):
        """Test if each vod has a corresponding wikipedia page to insert it to"""
        df_wiki_known = self.select([('wiki_page', 'nan')])
        return df_wiki_known.empty

    def get_list_website_for_insertion(self):
        """Gather the websites that have vods that are not inserted into wikipedia"""
        selection = [('inserted_in_wiki', 'nan')]
        df_non_inserted = self.select(selection)

        self.list_website_for_insertion = list(set(df_non_inserted['website']))

    def get_list_df_to_insert(self):
        """Each df_to_insert is for a unique website and with uninserted_links"""
        from liquipedia_interface.link_insertion_utils import make_url

        self.get_list_website_for_insertion()

        list_df_to_insert = []

        for website in self.list_website_for_insertion:
            # Select the df with a given website and wikis not inserted
            selection = [('website', website), ('inserted_in_wiki', 'nan'), ('video_title', 'not_Private video')]
            df_website = self.select(selection)

            wiki_pages = list(set(df_website['wiki_page']))

            for wiki_page in wiki_pages:
                if wiki_page == "none":
                    continue

                selection = [('website', website), ('wiki_page', wiki_page), ('inserted_in_wiki', 'nan'), ('video_title', 'not_Private video')]
                df_to_insert_website = self.select(selection)

                # Also adds the url at this stage
                df_to_insert_website['url'] = df_to_insert_website.apply(make_url, axis=1)

                list_df_to_insert.append(df_to_insert_website)

        return list_df_to_insert

    def mark_df_as_inserted(self, df):
        """When a df has been successfully inserted into liquipedia, update the fused_channels_info.csv"""
        video_ids_to_update = set(df['video_id'])

        mask = self.df_fused_info['video_id'].isin(video_ids_to_update)

        self.df_fused_info.loc[mask, 'inserted_in_wiki'] = True

        self.save_fused_info()