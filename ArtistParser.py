import re
import time
from bs4 import BeautifulSoup
import pandas as pd
from urllib import request

class LinkArtist:

    def __init__(self,
                 artists,
                 output_path = "OutputSongTable.csv",
                 site = "https://lyrics.com",
                 sleep_time = 1.5
                 ):
        '''
        artists: ist of artists to scrape
        output_path: path in which to store the output csv
        '''
        self.artists = artists
        self.path = output_path
        self.site = site
        self.sleep = sleep_time

    def get_artist_page(self, artist):
        """
        Return the scraped search page for the given artist

        Parameters
        ----------
        artist: Name of the artist
        """
        search_pattern = re.sub(" ", "%20", artist.lower())
        link = self.site + "/lyrics/" + search_pattern
        return request.urlopen(link).read().decode("utf-8")

    def titles_from_artist(self, artist):
        """
        Return the url and the name of the artist (as visualized in the site)

        Parameters
        ----------
        artist: Name of the artist
        """
        soup = BeautifulSoup(self.get_artist_page(artist), "lxml")
        first_result = soup.find("td", {"class": "tal fx"})
        raw_url = first_result.find("a")["href"]
        singer = first_result.text
        return raw_url, singer

    def df_single_artist(self, artist):
        """
        Return DataFrame with information of all artsist's songs

        Parameters
        ----------
        artists: name of the artist
        """

        raw_url, singer = self.titles_from_artist(artist)
        artist_link = self.site + raw_url
        artist_page = request.urlopen(artist_link).read().decode("utf-8")
        soup = BeautifulSoup(artist_page, "lxml")
        df = pd.DataFrame(columns=["artist", "song_title", "year", "link", "text"])

        for result in soup.find_all("div", {"class": "clearfix"}):
            try:
                year = re.search("\[(\d+)\]", result.find("span",
                                                          {"class": "year"}).text).groups()[0]
                for song in result.find_all("td", {"class": "tal qx"}):
                    df = pd.concat((df,
                                    pd.DataFrame({
                                        "artist": [singer],
                                        "song_title": [re.search("[^\[]+", song.find("a").text).group(0).strip()],
                                        "year": [year],
                                        "link": [self.site + song.find("a")["href"]],
                                        "text": [""]
                                    })))

            except:
                continue
        df.reset_index(drop=True, inplace=True)
        return df.drop_duplicates(["artist", "song_title"], keep = "last")

    def populate_df(self):
        """
        Return DataFrame containing information regarding all songs of all the artists
        """
        df = pd.DataFrame(columns=["artist", "song_title", "year", "link", "text"])
        for artist in self.artists:
            df = pd.concatenate((df, self.df_single_artist(artist)))

            time.sleep(self.sleep)
        df.reset_index(drop = True, inplace = True)
        df.to_csv(self.path, index=False)

        return df



