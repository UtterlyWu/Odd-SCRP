from Spider import Spider
from datetime import datetime

if __name__ == '__main__':
    #Tests
    spider = Spider(datetime.strptime('20230514', '%Y%m%d'), 'football')

    #Test crawling
    toPrintUrls = spider.crawl()
    for i in range(len(toPrintUrls)):
        print(toPrintUrls[i])
    print('')

    #Test scraping
    toPrintOdds = spider.scrape('https://www.oddsportal.com/football/czech-republic/division-e/brno-bzenec-0x81ByeF/')
    print('https://www.oddsportal.com/football/czech-republic/division-e/brno-bzenec-0x81ByeF/')
    for k, v in toPrintOdds.items():
        print(k, v)
    print('')

    spider.hunt(datetime.strptime('20230514', '%Y%m%d'), datetime.strptime('20230515', '%Y%m%d'))