from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from dresslily.spiders.hoody import HoodySpider
from dresslily.spiders.review import ReviewSpider 


def main():
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(HoodySpider)
    process.crawl(ReviewSpider)
    process.start()

if __name__=='__main__':
    main()