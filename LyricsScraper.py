# Native modules
import re
import time
from urllib import request
# Third party dependencies
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm


class LyricsScraper():
    def __init__(self,
                 lyrics_df_path,
                 output_df,
                 sleep = .5
                 ):
        self.lyrics_df_path = lyrics_df_path
        self.sleep = sleep
        self.output_df = output_df

    def get_source_page(self, link):
        '''
        Return the HTML page referred to the link in bs4 format
        Parameters
        ----------
        soup: HTML page of the song
        '''
        song_source = request.urlopen(link).read().decode("utf-8")
        return BeautifulSoup(song_source, "lxml")

    def check_artist(self, artist, soup):
        return artist == soup.find("div", {"class": "lyric-infobox clearfix"}).find("h4").text

    def get_text(self, soup):
        '''
        Return the lyrics of the song associated with the HTML page
        Parameters
        ----------
        soup: HTML page of the song
        '''
        raw_text = soup.find("pre", {"id": "lyric-body-text"}).text
        text = re.sub("\n", " ", raw_text)
        return text

    def extract_info(self):
        '''
        This function gets the clean text and the year of every input song link
        The output is stored in a data frame and saved in a csv file
        '''
        df = pd.read_csv(self.lyrics_df_path)

        for i in tqdm(range(len(df))):
            soup = self.get_source_page(df.loc[i, "link"])
            artist = df.loc[i, "artist"]

            if self.check_artist(artist, soup):
                df.loc[i, "text"] = self.get_text(soup)

        pd.to_csv(self.output_df, index = False)

