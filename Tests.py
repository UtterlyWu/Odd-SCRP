from spider import Spider
from dbmanager import DatabaseManager
from datetime import datetime

if __name__ == '__main__':
    #Tests
    spider = Spider('football', market='1X2')
    db = DatabaseManager('odds.db', False)

    #Test crawling
    toPrintUrls = spider.crawl()
    for i in range(len(toPrintUrls)):
        print(toPrintUrls[i])
    print('')

    #Test scraping
    test_page = 'https://www.oddsportal.com/football/australia/a-league/melbourne-city-sydney-fc-Iuuv8EFR/'
    toPrintOdds = spider.scrape(test_page)
    for k, v in toPrintOdds.items():
        print(k, v)
    print('')

    #Test hunting
    spider.hunt(datetime.strptime('20230520', '%Y%m%d'), datetime.strptime('20230521', '%Y%m%d'), db)

