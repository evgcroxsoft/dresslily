import json
import scrapy
from inline_requests import inline_requests
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
            yield scrapy.Request(url=link, callback=self.check_review)

        next_page = response.xpath("//a[contains(.//text(), '>')]").attrib['href']
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
    
    @inline_requests
    def check_review(self, response):

        # Get number of pages
        id = response.css('#hidden-goodsId::attr(value)').get()
        url = f'https://www.dresslily.com/m-review-a-view_review_list-goods_id-{id}-page-1'
        reviews_response = yield scrapy.Request(url=url, headers=HEADERS)
        reviews = json.loads(reviews_response.text)
        total_pages = reviews['data']['page_count']

        links = [f'https://www.dresslily.com/m-review-a-view_review_list-goods_id-{id}-page-{page}' for page in range(total_pages+1)]
        for link in links:
            product_id = response.css('em.sku-show').get()
            yield scrapy.Request(url=link, headers=HEADERS, callback=self.parse_hoody, meta={'product_id': product_id})

    def parse_hoody(self, response):
        reviews = json.loads(response.text)
        for review in reviews['data']['review']['review_list']:
            product_id = response.meta.get('product_id')
            l = ItemLoader(item = ReviewItem(), selector=review)

            l.add_value('product_id', product_id)
            l.add_value('rating', review['rate_overall'])
            l.add_value('timestamp', review['adddate'])
            l.add_value('text', review['pros'])
            l.add_value('size', review['review_size']['overall_fit'])
            try:
                l.add_value('color', review['goods']['color'])
            except:
                pass

            yield l.load_item()