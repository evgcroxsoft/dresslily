import requests
import scrapy
from scrapy.loader import ItemLoader
from dresslily.items.review import ReviewItem
from dresslily.settings import HEADERS


class ReviewSpider(scrapy.Spider):
    name = "review"
    allowed_domains = ["www.dresslily.com"]
    start_urls = ["https://www.dresslily.com/hoodies-c-181.html"]
    custom_settings = {
        'FEEDS': { 'reviews_data.csv': { 'format': 'csv', 'overwrite': True}},
        'FEED_EXPORT_FIELDS': ['product_id','rating','timestamp', 'text', 'size', 'color']
        }

    def parse(self, response):
        links = response.css('a.js-picture.js_logsss_click_delegate_ps.twoimgtip.category-good-picture-link::attr(href)').getall()
        for link in links:
            yield scrapy.Request(url=link, callback=self.parse_hoody)

        next_page = response.xpath("//a[contains(.//text(), '>')]").attrib['href']
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def get_pages(self, id, page = 1):
        url = f'https://www.dresslily.com/m-review-a-view_review_list-goods_id-{id}-page-{page}'
        r = requests.get(url=url, headers=HEADERS)
        reviews = r.json()
        return reviews

    def parse_hoody(self, response):
        id = response.css('#hidden-goodsId::attr(value)').get()
        if self.get_pages(id):
            total_pages = self.get_pages(id)['data']['page_count']
            for page in range(0, total_pages):
                reviews = self.get_pages(id, page)['data']['review']['review_list']
                for review in reviews:
                    product_id = response.css('em.sku-show').get()
                    l = ItemLoader(item = ReviewItem(), selector=review)

                    l.add_value('product_id', product_id)
                    l.add_value('rating', review['rate_overall'])
                    l.add_value('timestamp', review['adddate'])
                    l.add_value('text', review['pros'])
                    l.add_value('size', review['review_size']['overall_fit'])
                    l.add_value('color', review['goods']['color'])

                    yield l.load_item()