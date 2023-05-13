#general
from typing import List
from typing import Dict
import sqlite3
from datetime import datetime
from datetime import timedelta
#bs4 setup
from bs4 import BeautifulSoup
#requests setup
import requests
#selenium setup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class Spider:
    """
    Spider to scrape odds and their respective bookmakers

    Attributes:
        date: Date of the games whose odds need scraping
        sport: Sport to scrape
    """

    def __init__(self, start_date: str, sport: str):
        """
        Initializes the instance with origin date and sport.

        Args:
          start_date: Date the spider should start crawling at. Format YYYYMMDD.
          sport: The sport the spider should start crawling at. Options to add later ('football' for now).
          options: Flags determining chrome driver behavior.
          driver: Chrome driver controlled by Selenium.
          soup: Last HTML page worked on represented by a BeautifulSoup object.
        """
        self.date = start_date
        self.sport = sport
        #selenium setup
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.options)
        #bs4 setup
        self.soup = BeautifulSoup("")
    
    def crawl(self) -> List[str]:
        """
        Retrives a list of urls to scrape.

        Mimics request to API to recieve JSON data containing urls to scrape, which are then
        put into a list and returned. 

        Returns:
            A list of urls to scrape.
        """

        strDate = '{}{:02d}{:02d}'.format(self.date.year, self.date.month, self.date.day)

        headers = {
            'authority': 'www.oddsportal.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'referer': f'https://www.oddsportal.com/matches/{self.sport}/{strDate}/',
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
            f'https://www.oddsportal.com/ajax-nextgames/1/-4/1/{strDate}/yje83.dat',
            params={'_': '/',},
            headers=headers,
        )

        gamePageObjs = response.json()["d"]["rows"]

        urls = []
        for i in range(len(gamePageObjs)):
            urls.append('https://www.oddsportal.com' + gamePageObjs[i]["url"])

        return urls
    
    def load_page(self, secs: int, url: str, xpath: str) -> bool:
        """
        Allows page to load until desired elements to appear

        Args:
            secs: Seconds to wait before timeout.
            url: URL of page to load.
            xpath: Full xpath of an HTML element which needs to be loaded.
        
        Returns:
            True if the element at the xpath is found. False if timeout.
        """
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, secs).until(EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except:
            print('')
            print("Something went wrong")
            return False

    
    def scrape(self, url: str) -> Dict[str, List[float]]:
        """
        Retrives betting odds for a specific game.

        Retrieves betting odds from a specific game via its page. The page is 
        is loaded via Selenium, and the data extracted via Beautiful Soup. Should work 
        for any sport and any market.

        Args:
            url: URL of the page to scrape.

        Returns:
            A dictionary with keys corresponding to bookmakers and values corresponding to odds.
        """
        if (self.load_page(10, url, '/html/body/div[1]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[2]/div[2]/div')):
            self.soup = BeautifulSoup(self.driver.page_source, 'lxml')
            all_book_elemts = self.soup.find_all('p', class_="height-content max-mm:hidden pl-4")
            all_odd_elemts = self.soup.select('div[data-v-cb2b6512] > p')
            books_to_odds = {}

            i2 = 0
            for i in range(len(all_book_elemts)):
                cur_book = all_book_elemts[i].text
                cur_odds = [all_odd_elemts[i2].text, all_odd_elemts[i2+1].text, all_odd_elemts[i2+2].text]
                i2 += 3
                books_to_odds[cur_book] = cur_odds

            return books_to_odds
        return None
    
    def hunt(self, start_date: datetime, end_date: datetime):
        """
        Retrives betting odds for all games in a range of dates.

        Aquires pages to scrape via 'crawl()', after which every page's data is extracted by 'scrape()'

        Args:
            start_date: Date to begin scraping, inclusive
            end_date: Date to end scraping, inclusive

        Returns:
            TODO: Make it save the information into a database. For now it just prints it out.
        """
        delta = end_date - start_date
        cur_date = start_date

        for i in range(delta.days + 1):
            self.date = cur_date
            toScrape = self.crawl()
            for i2 in range(len(toScrape)):
                data = self.scrape(toScrape[i2])
                print('')
                strDate = '{}{:02d}{:02d}'.format(self.date.year, self.date.month, self.date.day)
                print('DATE: ' + strDate)
                print('LINK: ' + toScrape[i2])
                try:
                    for k, v in data.items():
                        print(k, v)
                except:
                    print("No odds")

            cur_date += timedelta(days=1)