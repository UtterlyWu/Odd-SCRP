#general
from typing import List
#bs4 setup
from bs4 import BeautifulSoup
#requests setup
import requests
#selenium setup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Spider:
    """Spider to scrape odds and their respective bookmakers

    Attributes:
        date: Date of the games whose odds need scraping
        sport: Sport to scrape
    """

    def __init__(self, start_date: str, sport: str):
        """
        Initializes the instance with origin date and sport.

        Args:
          start_date: Date the spider should start crawling at. Format YYYMMDD.
          sport: The sport the spider should start crawling at. Options to add later ('football' for now).
        """
        self.date = start_date
        self.sport = sport
    
    def crawl(self) -> List[str]:
        """
        Retrives a list of urls to scrape.

        Mimics request to API to recieve JSON data containing urls to scrape, which are then
        put into a list and returned. 

        Args:
            N/A

        Returns:
            A list of urls to scrape.
        """

        headers = {
            'authority': 'www.oddsportal.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'referer': f'https://www.oddsportal.com/matches/{self.sport}/{self.date}/',
            'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            
        }

        response = requests.get(
            f'https://www.oddsportal.com/ajax-nextgames/1/-4/1/{self.date}/yje83.dat',
            params={'_': '/',},
            headers=headers,
        )

        gamePageObjs = response.json()["d"]["rows"]

        urls = []
        for i in range(len(gamePageObjs)):
            urls.append(gamePageObjs[i]["url"])

        return urls

#Test
spider = Spider('20230509', 'football')
toPrint = spider.crawl()
for i in range(len(toPrint)):
    print(toPrint[i])