#general
from typing import List
from typing import Dict
from datetime import datetime
from datetime import timedelta
from dbmanager import DatabaseManager
#bs4 setup
from bs4 import BeautifulSoup
#requests setup
import requests
#selenium setup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class Spider:
    """
    Spider to scrape odds and their respective bookmakers.

    Attributes:
        date (datetime): Date for scraper to target. Format YYYYMMDD.
        sport (str): Sport for scraper to target.
        market (str): Market to scraper to target.
        options (str): Flags determining chrome driver behavior.
        driver (webdriver): Chrome driver controlled by Selenium.
        soup (BeautifulSoup): Last HTML page worked on represented by a BeautifulSoup object.
    """
    markets = {"1X2" : "1X2",
               "Home/Away" : "home-away",
               "Both Teams to Score" : "bts",
               "Double Chance" : "double",
               "Draw No Bet" : "dnb",
               "Odd or Even" : "odd-even"}

    def __init__(self, sport: str, market: str = '1X2'):
        """
        Initializes the instance with origin date and sport.

        Args:
          sport: The sport the spider should start crawling at. Options to add later ('football' for now).
          market: The market the spider should target when retrieving data. Options to add later ('1X2' for now).
        """
        self.date = datetime.strptime('20230516', '%Y%m%d')
        self.sport = sport
        self.market = market
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

        List of urls is retrieved from a page based on self.sport and self.date.
        And example of one of these pages is: https://www.oddsportal.com/matches/football/20230516/

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

    
    def scrape(self, url: str) -> Dict[str, List[float]]:
        """
        Retrives betting odds for a specific game.

        Betting odds are retrieved from one of these pages: 
        https://www.oddsportal.com/football/czech-republic/division-e/brno-bzenec-0x81ByeF/ 
        
        Should work for any sport and any market except Over/Under, Asian Handicap, and 
        European Handicap, Correct Score, and Halftime/Fulltime. Scrapes FULL TIME bets.

        Args:
            url: URL of the page to scrape.

        Returns:
            A dictionary with keys corresponding to bookmakers and values corresponding to odds.
        """
        try:
            #Go to market if it exists
            self.driver.get(url + f'#{Spider.markets[self.market]}')

            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.odds-item')))
            self.soup = BeautifulSoup(self.driver.page_source, 'lxml')
            markets_set = set()
            market_elemts = self.soup.select('.odds-item')
            for elemt in market_elemts:
                markets_set.add(elemt.text)
            
            if (self.market not in markets_set):
                return None

            #Retrieve data from page
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-v-44b45d80]')))
            self.soup = BeautifulSoup(self.driver.page_source, 'lxml')
            all_book_elemts = self.soup.find_all('p', class_="height-content max-mm:hidden pl-4")
            all_odd_elemts = self.soup.select('div[data-v-cb2b6512] > p')
            
            #Turn data into dictionary of 'bookmaker' to 'list of odds'
            odds_to_book = len(all_odd_elemts)//len(all_book_elemts)
            books_odds_dict = {}
            i3 = 0

            for i in range(len(all_book_elemts)):
                cur_book = all_book_elemts[i].text
                cur_odds = []

                for i2 in range(odds_to_book):
                    cur_odds.append(all_odd_elemts[i3].text)
                    i3 += 1

                books_odds_dict[cur_book] = cur_odds

            return books_odds_dict
        
        except:
            pass

        return None
    

    def hunt(self, start_date: datetime, end_date: datetime, db_manager: DatabaseManager):
        """
        Retrives betting odds for all games in a range of dates.

        Args:
            start_date: Date to begin scraping, inclusive.
            end_date: Date to end scraping, inclusive.
            db_manager: Database manager to move extracted data into database of choice.
            db: Name or path to database to connect to. Make sure to end with '.db'.

        Returns:
            TODO: Make it save the information into a database. For now it just prints it out.
        """
        #Run in case table doesn't exist
        db_manager.create_table()

        #Collect data and enter into database
        delta = end_date - start_date
        cur_date = start_date if (end_date >= start_date) else end_date

        for i in range(abs(delta.days) + 1):
            self.date = cur_date
            toScrape = self.crawl()

            for i2 in range(10):
                data = self.scrape(toScrape[i2])
                link = toScrape[i2]
                str_date = '{}{:02d}{:02d}'.format(self.date.year, self.date.month, self.date.day)
                market = self.market
                if (data != None):
                    for k, v in data.items():
                        bookmaker = k
                        odds = v
                        db_manager.add_to_table(link, str_date, market, bookmaker, odds)
                else:
                    db_manager.add_to_table(link, str_date, market, 'N/A', [])
            
            cur_date += timedelta(days=1)
        
        #Commit changes to database
        db_manager.commit()

