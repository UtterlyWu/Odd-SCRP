from spider import Spider
from dbmanager import DatabaseManager
from datetime import datetime

if __name__ == '__main__':
    #Tests
    spider = Spider('football', market='bts')
    db = DatabaseManager('odds.db', False)

    #Test crawling
    toPrintUrls = spider.crawl()
    for i in range(len(toPrintUrls)):
        print(toPrintUrls[i])
    print('')

    #Test scraping
    test_page = 'https://www.oddsportal.com/football/england/premier-league/leicester-liverpool-CAKtamhe/#bts;2'
    toPrintOdds = spider.scrape(test_page)
    print(test_page)
    for k, v in toPrintOdds.items():
        print(k, v)
    print('')

    #Test hunting
    spider.hunt(datetime.strptime('20230518', '%Y%m%d'), datetime.strptime('20230518', '%Y%m%d'), db)